import datetime
import os
from pathlib import Path
import time
import pull_data 
import json
import pandas as pd
#from .computation.tfidf import computeTF, computeIDf, computeTFIDF
import sys
sys.path.insert(0, '../')
from computation import tfidf as tf


PATH_SLACK_DUMP = '../slack_dump'
JSON_FILE_NAME = 'fyi.json'
TSV_FILE_NAME = 'fyi.tsv'
TEXT_FILE_NAME = 'bow.txt'


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


def read_dumped_json(dump_data_path):
	fname = dump_data_path / JSON_FILE_NAME
	json_obj = json.load(open(fname, 'r'))
	return json_obj


def process_json_write_as_tsv(json_obj, tsv_name):
	text_list = list()
	json_list = list()

	for x in json_obj["messages"]:
		text_json = get_text_from_json_obj(x)
		text_list.append(text_json[0])
		json_list.append(text_json[1])

	df = pd.DataFrame()
	df['data'] = text_list
	df['json'] = json_list
	df['id'] = df.reset_index().index
	df = df[['id', 'data', 'json']]
	df.to_csv(tsv_name, sep = '\t', index = False)
	print(preprocessing())



def preprocessing():
	print(dump_data_path / TSV_FILE_NAME)
	raw_data = pd.read_csv(dump_data_path / TSV_FILE_NAME, sep  = '\t', header = 0)
	print("Updated raw_data")
	#makeing bag of words
	all_unique_words = set()
	for x in raw_data.data:
		all_unique_words = all_unique_words.union(set(x.split(" ")))
		print(f"number of unique words: {len(all_unique_words)}")

	list_word_freq_ht, tfidf_res = get_tfidf(raw_data.data.tolist(), all_unique_words)
	
	with open(dump_data_path / TEXT_FILE_NAME, 'w+') as bow:
		bow.write(str(tfidf_res))
		bow.close()
	return "data stored"

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
  		

			
