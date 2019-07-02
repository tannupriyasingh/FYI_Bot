import argparse
import datetime
import errno
import json
import operator
import os
import sys
import time
import slacker

USERNAMES = 'users.json'
CHANNEL_NAME_LIST = ['fyi']


def mkdir_p(path):
    """Create a directory if it does not already exist.
    http://stackoverflow.com/a/600612/1558022
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def slack_ts_to_datetime(ts):
    """Try to convert a 'ts' value from the Slack into a UTC datetime."""
    time_struct = time.localtime(float(ts))
    return datetime.datetime.fromtimestamp(time.mktime(time_struct))


def download_history(channel_info, history, path):
    """Download the message history and save it to a JSON file."""
    mkdir_p(os.path.dirname(path))
    try:
        with open(path) as infile:
            existing_messages = json.load(infile)['messages']
    except (IOError, OSError):
        existing_messages = []

    # TODO: For convenience, the messages yielded from `history` usually
    # have more than just the raw Slack API response: in particular, they have
    # a username and a date string.  If the username and/or timestamp format
    # changes, we could inadvertently save duplicate messages.
    for msg in history:
        if msg in existing_messages:
            break
        existing_messages.append(msg)

    # Newest messages appear at the top of the file
    existing_messages = sorted(existing_messages,
                               key=operator.itemgetter('ts'),
                               reverse=True)
    data = {
        'channel': channel_info,
        'messages': existing_messages,
    }
    json_str = json.dumps(data, indent=2, sort_keys=True)
    with open(path, 'w') as outfile:
        outfile.write(json_str)


def download_public_channels(slack, outdir):
    """Download the message history for the public channels where this user
    is logged in.
    """
    for channel in slack.channels():
        if channel['is_member']:
        	if channel['name'] in CHANNEL_NAME_LIST:
	            history = slack.channel_history(channel=channel)
	            path = os.path.join(outdir, '%s.json' % channel['name'])
	            download_history(channel_info=channel, history=history, path=path)



class AuthenticationError(Exception):
    pass



class SlackHistory:
    """Wrapper around the Slack API.  This provides a few convenience
    wrappers around slacker.Slacker for the particular purpose of history
    download.
    """

    def __init__(self, token):
        self.slack = slacker.Slacker(token=token)
        self.usernames = self._fetch_user_mapping()


    def _get_history(self, channel_class, channel_id):
        """Returns the message history for a channel, group or DM thread.
        Newest messages are returned first.
        """
        # This wraps the `channels.history`, `groups.history` and `im.history`
        # methods from the Slack API, which can return up to 1000 messages
        # at once.
        #
        # Rather than spooling the entire history into a list before
        # returning, we pass messages to the caller as soon as they're
        # retrieved.  This means the caller can choose to exit early (and save
        # API calls) if they turn out not to want older messages, for example,
        # if they already have a copy of those locally.
        last_timestamp = None
        while True:
            response = channel_class.history(channel=channel_id,
                                             latest=last_timestamp,
                                             oldest=0,
                                             count=1000)
            for msg in sorted(response.body['messages'],
                              key=operator.itemgetter('ts'),
                              reverse=True):
                last_timestamp = msg['ts']
                msg['date'] = str(slack_ts_to_datetime(msg['ts']))
                try:
                    msg['username'] = self.usernames[msg['user']]
                except KeyError:  # bot users
                    pass
                yield msg
            if not response.body['has_more']:
                return

    def _fetch_user_mapping(self):
        """Gets a mapping of user IDs to usernames."""
        return {
            u['id']: u['name']
            for u in self.slack.users.list().body['members']}

    def channels(self):
        """Returns a list of public channels."""
        return self.slack.channels.list().body['channels']

    def channel_history(self, channel):
        """Returns the message history for a channel."""
        return self._get_history(self.slack.channels, channel_id=channel['id'])

def pull_write_data(outdir):
    token = open('../secrets/slack_token.secrets', 'r').readline()
    token = token.replace('\n', '')
    
    try:
        slack = SlackHistory(token=token)
    except AuthenticationError as err:
        sys.exit(err)

    print('Saving public channels to %s' % outdir)
    download_public_channels(slack, outdir=outdir)
