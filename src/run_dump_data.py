import datetime
import os
from pathlib import Path
import time
import pull_data 
import json
import pandas as pd


PATH_SLACK_DUMP = "../slack_dump"
JSON_FILE_NAME = 'fyi.json'
TSV_FILE_NAME = 'fyi.tsv'


def create_dir(dir_name):
	os.mkdir(dir_name)


def timestamp_str_format():
	return '%Y_%m_%d_%H_%M_%S'


def timestamp_as_str():
	return datetime.datetime.now().strftime(timestamp_str_format())


def get_text_from_json_obj(json_obj):
    if 'attachments' in json_obj:
        return json_obj['attachments'][0]['text'], json_obj['attachments'][0]
    if 'text' in json_obj:
        return json_obj['text'], json_obj


def store_data(something):
    with open('pinned_infra.tsv','r') as tsv:
        next(tsv)
        AoA = [line.strip().split('\t') for line in tsv]
    ID_list = list()
    for a in AoA:
        ID_list.append(int(a[0]))
    ID = max(ID_list)
    tsv.close()
    
    with open('pinned_infra.tsv', 'a') as data_csv:
        writer = csv.writer(data_csv, delimiter="\t")
        print(f"Id value: {ID}")
        print(f"something: {something}")
        ID += 1
        print(f"id updated {ID}")
        row = []
        row.append(ID)
        row.append(something)
        writer.writerow(row)
    

def read_dumped_json(dump_data_path):
	fname = dump_data_path / JSON_FILE_NAME
	json_obj = json.load(open(fname, 'r'))
	return json_obj


def process_json_write_as_tsv(json_obj, tsv_name):
	text_list = list()
	json_list = list()

	for x in json_obj["messages"]:
		text_json = get_text_from_json_obj(x)
		print(x)
		print(text_json)
		text_list.append(text_json[0])
		json_list.append(text_json[1])

	df = pd.DataFrame()
	df['data'] = text_list
	df['json'] = json_list
	df['id'] = df.reset_index().index

	df = df[['id', 'data', 'json']]

	df.to_csv(tsv_name, sep = '\t', index = False)

if __name__ == "__main__":
	# specify the time in sec for the data to be dumped
  	dump_every = 10

  	while True:
  		current_timestamp = timestamp_as_str()
  		dump_data_path = Path(PATH_SLACK_DUMP)/current_timestamp
  		create_dir(dump_data_path)
  		pull_data.pull_write_data(dump_data_path)
  		json_obj = read_dumped_json(dump_data_path)
  		tsv_name = dump_data_path / TSV_FILE_NAME
  		process_json_write_as_tsv(json_obj, tsv_name)
  		time.sleep(dump_every) 
  		

			
