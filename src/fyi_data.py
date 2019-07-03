#coding: UTF-8
import re
import csv
import random
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import pandas as pd
import computation.tfidf as tf
import re


def update_data():
    #loading stored data in a frame
    raw_data = pd.read_csv('pinned_infra.tsv', sep  = '\t', header = 0)
    print("Updated raw_data")

    #makeing bag of words
    all_unique_words = set()
    for x in raw_data.Data:
        all_unique_words = all_unique_words.union(set(x.split(" ")))
    print(f"number of unique words: {len(all_unique_words)}")

    return all_unique_words, raw_data


# @respond_to(u'? (.*)')
# def question_mark(message, something):
#     list_word_freq_ht, tfidf_res = get_tfidf(raw_data.Data.tolist(), all_unique_words)
#     response = get_best_response_based_on_tfidf_score(raw_data, tfidf_res, something)
#     if response:
#         message.reply('Here is what you are looking for: \n{}'.format(response))
#     else:
#         message.reply('Sorry I am not sure of:{}'.format(something))


@respond_to('Give me (.*)', re.IGNORECASE)
def giveme(message, something):
    all_unique_words, raw_data = update_data() 
    list_word_freq_ht, tfidf_res = get_tfidf(raw_data.Data.tolist(), all_unique_words)
    response = get_best_response_based_on_tfidf_score(raw_data, tfidf_res, something)
    if response:
        message.reply('Here is what you are looking for: \n{}'.format(response), in_thread=True)
    else:
        message.reply('Sorry I am not sure of:{}'.format(something), in_thread=True)

#get tfidf rank of sentences
def get_tfidf(list_of_sentences, unique_words):
    list_word_freq_ht = list()
    tf_score_list = list()
    empty_ht = dict.fromkeys(list(unique_words), 0)
    for l in list_of_sentences:
        ht = empty_ht.copy()
        bow = set(l.split(' '))

        for w in l.split(' '):
            ht[w] += 1

        tf_score_list.append(tf.computeTF(ht, bow))        
        list_word_freq_ht.append(ht)
        
    idfs = tf.computeIDf(list_word_freq_ht)
    res = [tf.computeTFIDF(x, idfs) for x in tf_score_list]
    
    return list_word_freq_ht, res

#get the best response for query
def get_best_response_based_on_tfidf_score(data, tfidf_res, query):
    tf_score_query_list_sum = [0] * data.shape[0]
    for w in query.split(" "):
        print(w)
        tf_score_query_list = [tfidf_score[w] for tfidf_score in tfidf_res]
        tf_score_query_list_sum = [x + y for x, y in zip(tf_score_query_list_sum, tf_score_query_list)]
    return data.Data[tf_score_query_list_sum.index(max(tf_score_query_list_sum))]


@respond_to('store (.*)', re.IGNORECASE)
def store_data(message, something):
    print("inside store")
    acknowledge = store_data(something)
    print(acknowledge)
    message.react('thumbsup')
    message.react('fyi')
#fuction to store data in excel sheet

def store_data(something):
    print("inside_Storedata")
    with open('pinned_infra.tsv','r') as tsv:
        next(tsv)
        AoA = [line.strip().split('\t') for line in tsv]
    ID_list = list()
    for a in AoA:
        ID_list.append(int(a[0]))
    ID = max(ID_list)
    tsv.close()
    data_csv = open('pinned_infra.tsv', 'a')
    with data_csv:
        writer = csv.writer(data_csv, delimiter="\t")
        print(f"Id value: {ID}")
        print(f"something: {something}")
        ID += 1
        print(f"id updated {ID}")
        row = []
        row.append(ID)
        row.append(something)
        print(row)
        writer.writerow(row)
        print(something)
        ack = "data stored"
    data_csv.close()
    return ack


# @respond_to(react('fyi'))
# if message.react is react('fyi'):
#     store_data(message)

#@listen_to(::)

# ######I start here #######

# from simple_slack_bot.simple_slack_bot import SimpleSlackBot

# simple_slack_bot = SimpleSlackBot(debug=True)

# # character's name will be the key while the value will a list of all their lines
# character_lines = {}


# @simple_slack_bot.register("message")
# def office_callback(request):


#     """Our callback which is called every time a new message is sent by a user
#     :param request: the request object that came with the message event
#     """

#     if request.message is not None:
#         for token in request.message.split(' '):
#             if token.lower() in character_lines:
#                 character_name = token.lower()
#                 random_index = random.randint(0, len(character_lines[character_name]) - 1)
#                 request.write(character_name.capitalize() + ": " + character_lines[character_name][random_index])


# def read_in_characters_lines():
#     """Stores all characters' lines into a dictionary
#     """

#     with open(r"the_office_lines_scripts.csv", "r", encoding='utf-8') as csvfile:
#         csv_f = csv.reader(csvfile)

#         for _, _, _, _, line_text, speaker, _ in csv_f:
#             speaker = speaker.lower()
#             if speaker in character_lines:
#                 character_lines[speaker].append(line_text)
#             else:
#                 character_lines[speaker] = []
#                 character_lines[speaker].append(line_text)


# def main():
#     read_in_characters_lines()
#     print("bot ready!")
#     simple_slack_bot.start()


# if __name__ == "__main__":
#     main()
