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
import shutil
import time
import datetime
import logging
import json
import argparse
#from flask import Flask
#from flask import request
#from flask import jsonify
#import spacy
from dataclasses import dataclass, field
from typing import Dict, Optional
common_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(common_path)
from tools import Configuration


NEW_LINE = '\n'
R2L = '\u202b'
CR_LF = '\r\n'

#app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename=os.path.basename(__file__).replace('py', 'log'), mode='w', encoding='utf-8')
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)


#@app.route('/', methods=["POST", "GET"])
def main_route():
    result = []
    result.append('/produce_tsrt: input srt, output with entities')
    result.append('All the files must be in utf-8 format with CR LF at eol')
    return 'NEW_LINE'.join(result)


#@app.route('/shutdown', methods=["POST", "GET"])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)


class InfoFileDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\\\([^\\])'), r'\1\\\\\\\\\2'),    # Replace string\\string with string\\\\string
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2')           # Replace string\string with string\\string
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)


#@app.route('/produce_tsrt', methods=["POST"])
def produce_tsrt(fullpath=None):
    #app.logger.info("/produce_tsrt called")
    csv_separator='#'
    by_request = False
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

    header = text[0].replace("\ufeff", '').split(csv_separator)
    text = [dict(zip(header, line.split(csv_separator))) for line in text[1:]]
    
    logger.info(f"Process: {fullpath}")
    # Convert text lines to "{domain}?src={full_path_media_name.mp4}&tsrt={tsrt_name}&start={time}&end={time}#{subtitle}" format lines
    info_fullpath = fullpath[:-29] + ".info.json"
    with open(info_fullpath, 'r', encoding='utf-8') as info_file:
        info_data = json.load(info_file, cls=InfoFileDecoder)


    media_type = info_data['media_type'] if 'media_type' in info_data else ''
    media_type = ','.join(set(media_type.split(',')))
    full_path_media_name = info_data["media_path"]
    for replace_values in config['media_path_replace']:
        full_path_media_name = full_path_media_name.replace(replace_values['oldvalue'], replace_values['newvalue'])

    tsrt_filename = path.basename(fullpath).replace(".entities.csv", ".tsrt.csv")
    tsrt_fullpath = config["tsrt_path"] + tsrt_filename

    result = [["movieurl", "movietext", "start", *header[3:]]]
    for item in text:
        if item["mediatext"] != '' and item["mediatext"] is not None:
            movieurl = config["domain"] + "?src=" + full_path_media_name + "&tsrt=" + tsrt_fullpath + "&start=" + item["start"] + "&end=" + item["end"] + "&mt=" + media_type
            value = [movieurl, item["mediatext"], item["start"], *[item[key] for key in header[3:]]]
            result.append(value)

    file_name = path.basename(fullpath)[:-13] # Select only the file name without the extension
    dst_fullpath = path.join(config['output'], file_name + ".tsrt.csv")
    with open(dst_fullpath, "w", encoding='utf-8-sig') as dst_file:
        for line in result:
            dst_file.write(csv_separator.join(line) + NEW_LINE)
    #app.logger.info(f"Created {dst_fullpath} file")

    if by_request:
        return jsonify(sucess=True)


def files_by_posfix(folder, posfix):
    filenames = os.listdir(folder)
    res = [filename for filename in filenames if filename.endswith(posfix)]
    return res

@dataclass
class TsrtItem:
    #media_path: Optional[str] = field(default=None)
    #media_type: Optional[str] = field(default=None)
    text: Optional[str] = field(default=None)
    start: Optional[str] = field(default=None)
    end: Optional[str] = field(default=None)
    entities: Dict[str, str] = field(default_factory=dict)
 
if __name__ == "__main__":
    #app.logger.info("Program running")
    parser = argparse.ArgumentParser()
    parser.add_argument('-ep', '--entities_paths', nargs='+', required=False)
    parser.add_argument('-tp', '--tsrt_path')
    parser.add_argument('-o', '--output')
    config = Configuration(__file__.replace('py', 'json'), parser)
    logger.info(config)
    Path(config['output']).mkdir(parents=True, exist_ok=True)

    csv_separator='#'
    entities_paths_files = []
    for entity_path in config['entities_paths']:
        entities_paths_files.append(os.listdir(entity_path))

    info_files = files_by_posfix(config['entities_paths'][0], '.info.json')
    for info_file_name in info_files:
        base_name = info_file_name[:-10] # Select only the file name without the extension
        tsrt_items: list[TsrtItem] = []
        for idx_entity_path, entity_path in enumerate(config['entities_paths']):
            #entity_file_path = next((os.path.join(entity_path,item) for item in spacy_entities_files if item[:-29] == info_file[:-10]), None)
            entity_file_path = next((os.path.join(entity_path,item) for item in entities_paths_files[idx_entity_path] if item[:-13] == base_name), None)
            print(entity_file_path)
            with open(entity_file_path, 'r', encoding='utf-8') as entity_file:
                text = []
                tsrt_item_idx = 0
                for idx, item in enumerate(entity_file):

                    #text.append(item)
                    entities_file_item = item.replace("\ufeff", '').replace('\n', '').split(csv_separator)
                    if idx == 0:
                        entities_names = entities_file_item[3:]
                    else:
                        if idx_entity_path == 0:
                            tsrt_items.append(TsrtItem())
                        tsrt_item = tsrt_items[tsrt_item_idx]
                        entities_keys = entities_file_item[3:]
                        if idx_entity_path == 0:
                            tsrt_item.text = entities_file_item[0]
                            tsrt_item.start = entities_file_item[1]
                            tsrt_item.end = entities_file_item[2]
                        for entity_idx, entity_name in enumerate(entities_names):
                            tsrt_item.entities[entity_name] = entities_keys[entity_idx]
                        tsrt_items[tsrt_item_idx] = tsrt_item
                        tsrt_item_idx = tsrt_item_idx + 1
        #print(info_file)

        info_file_path = os.path.join(config['entities_paths'][0], info_file_name)
        with open(info_file_path, 'r', encoding='utf-8') as info_file:
            info_data = json.load(info_file, cls=InfoFileDecoder)
        media_type = info_data['media_type'] if 'media_type' in info_data else ''
        media_type = ','.join(set(media_type.split(',')))
        full_path_media_name = info_data["media_path"]
        for replace_values in config['media_path_replace']:
            full_path_media_name = full_path_media_name.replace(replace_values['oldvalue'], replace_values['newvalue'])

        tsrt_filename = info_file_name.replace(".info.json", ".tsrt.csv")
        tsrt_fullpath = config["tsrt_path"] + tsrt_filename
        result = [["movieurl", "movietext", "start"] + list(tsrt_items[0].entities.keys())]
        for idx, item in enumerate(tsrt_items):
            mediatext = item.text
            if mediatext != '' and mediatext is not None:
                movieurl = config["domain"] + "?src=" + full_path_media_name + "&tsrt=" + tsrt_fullpath + "&start=" + item.start + "&end=" + item.end + "&mt=" + media_type
                '''
                entity_location = safe_prop(dicta_item, "GPE") + ';' + safe_prop(dicta_item, "LOC") + ';' + safe_prop(dicta_item, "FAC")
                entity_location = ';'.join(set(entity_location.split(';')))
                '''
                '''
                entity_values = [safe_prop(dicta_item, "PER"), safe_prop(dicta_item, "TIMEX"),safe_prop(dicta_item, "ORG"), entity_location.strip(';'), safe_prop(dicta_item, "TTL"), 
                    safe_prop(item, "EntityMoney"), safe_prop(item, "EntityLanguage")]
                '''
                value = [movieurl, mediatext, item.start] + list(item.entities.values())
                result.append(value)

        dst_fullpath = path.join(config['output'], tsrt_filename)
        with open(dst_fullpath, "w", encoding='utf-8-sig') as dst_file:
            for line in result:
                dst_file.write(csv_separator.join(line) + NEW_LINE)

    print("## Postprocess")
    print(f"Copy the files from {config['output']} to the destination 'tsrt' folder")
 

'''
if __name__ == "__main__":
    #app.logger.info("Program running")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', required=False, help='Path to the file or the folder: C:\\dev\\data\\poc_a1.srt')
    parser.add_argument('-o', '--output')
    parser.add_argument('-tp', '--tsrt_path')
    config = Configuration(__file__.replace('py', 'json'), parser)
    logger.info(config)
    Path(config['output']).mkdir(parents=True, exist_ok=True)
    if config['path'] is not None:
        arg_path = os.path.normpath(config['path'])
        if os.path.isdir(arg_path):
            for filepath in os.listdir(arg_path):
                if filepath.endswith('.entities.csv'):
                    produce_tsrt(os.path.join(arg_path, filepath))
        elif os.path.isfile(arg_path):
            produce_tsrt(arg_path)
        print("## Postprocess")
        dst_folder = config["tsrt_path"].replace('\\', '')
        print(f"$ sudo mkdir /home/temp/{dst_folder}/tsrt")
        print(f"$ sudo mv /home/leo/Public/dev/MediaAnalysis/preprocess/data/{dst_folder}/tsrt/* /home/temp/{dst_folder}/tsrt/")
    else:
        host = config['host']
        port = config['port']
        print(f"Domain: http://{host}:{port}")
        app.run(debug=True, host=host, port=port)
'''
