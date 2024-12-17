'''
import transformers
import torch 
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
model_path = "/home/temp/dev/MediaAnalysis/models/dicta-bert-ner/"
model_path = "/mnt/prsecspma/models/dicta-bert-ner-20240725T122501Z-001/dicta-bert-ner/"
tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
model = AutoModelForTokenClassification.from_pretrained(model_path)
'''
#!/usr/bin/python

import re
import os
import sys
import signal
import posixpath
import ntpath
from collections import namedtuple
from os import path
from pathlib import Path
import csv
import shutil
import time
import datetime
import logging
import json
import argparse
from flask import Flask
from flask import request
from flask import jsonify
import torch    # AutoModelForTokenClassification requires the PyTorch library
import transformers
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
common_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
sys.path.append(common_path)
from tools import Configuration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import entities_tools as et

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename=os.path.basename(__file__).replace('py', 'log'), mode='w', encoding='utf-8')
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

datetime_fmt = "%Y_%m_%d-%H:%M:%S"

labels_map = {
    "PER": "EntityPerson",
    "LOC": "EntityLocation",
    "GPE": "EntityLocation",
    "FAC": "EntityLocation",
    "ORG": "EntityOrganization",
    "TIMEX": "EntityTime",
    "TTL": "EntityTitle"
}


@app.route('/', methods=["POST", "GET"])
def main_route():
    result = []
    result.append('/produce_entities: input srt, output with entities')
    result.append('All the files must be in utf-8 format with CR LF at eol')
    return 'NEW_LINE'.join(result)


@app.route('/shutdown', methods=["POST", "GET"])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)


def extract_entities(nlp, text):
    if not text:
        return {}
    doc = nlp(text)
    labels = {group: [item["word"] for item in doc if item["entity_group"] == group] for group in set(item["entity_group"] for item in doc)}

    return labels


nlp = None
@app.route('/produce_entities', methods=["POST"])
def produce_entities(fullpath=None):
    app.logger.info("/produce_entities called")
    csv_separator='#'

    by_request = True if fullpath is None else False
    if by_request:
        fullpath = request.args['fullpath'].replace(ntpath.sep, posixpath.sep)

        # Convert stream to text lines
        text = []
        chunk_size = 4096
        last = ''
        while True:
            chunk = request.stream.read(chunk_size)
            if len(chunk) == 0:
                break
            data = [item.strip('\n\r') for item in (last + str(chunk.decode(encoding='utf-8', errors='ignore'))).split('\n')]
            last = data[-1]
            text.extend(data[:-1])
        if last:
            text.append(last)
        if not text:
            return ''
    else:
        text = []
        with open(fullpath, encoding='utf-8') as data:
            for item in data:
                text.append(item.replace('\n', ''))
            #text = data.readlines()
    logger.info(f"Process: {fullpath}")
    # Convert text lines to "{domain}?src={full_path_media_name.mp4}&tsrt={tsrt_name}&start={time}&end={time}#{subtitle}" format lines
    info_fullpath = os.path.splitext(fullpath)[0] + ".info.json"
    if os.path.isfile(info_fullpath):
        shutil.copy2(info_fullpath, path.join(config['output'], os.path.basename(info_fullpath)))
        
        sent_s_e = et.srt2sbt_s_e(text)
        entities, labels = et.create_sbt_entities(extract_entities, nlp, logger, sent_s_e)

        fullpath_name = path.basename(fullpath)[:-4] # Select only the file name without the extension

        entities_full_name = f"{fullpath_name}.raw_entities.csv"
        dst_fullpath = path.join(config['output'], entities_full_name)
        raw_entities = et.create_raw_entities(sent_s_e, entities, labels)
        with open(dst_fullpath, "w", encoding='utf-8-sig') as dst_file:
            for line in raw_entities:
                dst_file.write(csv_separator.join(line) + et.NEW_LINE)
        
        
        #entities_full_name = f"{fullpath_name}_{time.strftime('%Y%m%d_%H%M%S')}.entities.csv"
        entities_full_name = f"{fullpath_name}.entities.csv"
        dst_fullpath = path.join(config['output'], entities_full_name)
        entities = et.create_entities(labels_map, sent_s_e, entities, labels)
        with open(dst_fullpath, "w", encoding='utf-8-sig') as dst_file:
            for line in entities:
                dst_file.write(csv_separator.join(line) + et.NEW_LINE)
        app.logger.info(f"Created {dst_fullpath} file")

        comment = ""
        if os.path.isfile(config['report_file']):
            with open(config['report_file'], 'a', encoding='utf-8') as report_file:
                report_file.write(f"{datetime.datetime.now().strftime(datetime_fmt)}#{fullpath}#{dst_fullpath}#{comment}\n")

    if by_request:
        return jsonify(sucess=True)


if __name__ == "__main__":
    app.logger.info("Program running")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', required=False, help='Path to the file or the folder: C:\\dev\\data\\poc_a1.srt')
    parser.add_argument('-o', '--output')
    config = Configuration(__file__.replace('py', 'json'), parser)
    logger.info(config)

    tokenizer =  AutoTokenizer.from_pretrained(config['model_path'], use_fast=False)
    model = AutoModelForTokenClassification.from_pretrained(config['model_path'])
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    Path(config['output']).mkdir(parents=True, exist_ok=True)
    config['report_file'] = path.join(config['output'], "report_entities.csv")
    if config['path'] is not None:
        arg_path = os.path.normpath(config['path'])
        if os.path.isdir(arg_path):
            report_data = []
            if os.path.isfile(config['report_file']):
                with open(config['report_file'], 'r', encoding='utf-8') as report_file:
                    reader_file = csv.DictReader(report_file, delimiter='#')
                    for row in reader_file:
                        report_data.append(row)
            else:
                with open(config['report_file'], 'w', encoding='utf-8') as report_file:
                    report_file.write(f"Time#SrtPath#EntPath#Comment\n")

            for filepath in os.listdir(arg_path):
                if filepath.endswith('.srt'):
                    srtPath = os.path.join(arg_path, filepath)
                    exists = next((item for item in report_data if item['SrtPath'] == srtPath), None)
                    if exists is None:
                        produce_entities(srtPath)
        elif os.path.isfile(arg_path):
            produce_entities(arg_path)
    else:
        host = config['host']
        port = config['port']
        print(f"Domain: http://{host}:{port}")
        app.run(debug=True, host=host, port=port)
