import requests
import os
import json
import sys
import argparse
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename='post.log', mode='w', encoding='utf-8')
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(0)
   

def process_srt_file(file_path):
    url = f'http://localhost:{config["process_srt"]["port"]}/process_srt'
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    params = {'fullpath': file_path}
    response = requests.post(url, headers=headers, data=open(file_path, 'rb').read(), params=params)
    print('Status Code', response.status_code)


def process_srt(full_path):
    file_path = os.path.normpath(full_path)
    if os.path.isdir(file_path):
        for filepath in os.listdir(file_path):
            if filepath.endswith('.srt'):
                process_srt_file(os.path.join(full_path, filepath))
    elif os.path.isfile(full_path):
        process_srt_file(full_path)


def process_media_file(file_path):
    url = f'http://localhost:{config["process_media"]["port"]}/process_media'
    headers = {'Content-Type': 'audio/wav', 'Content-Length': str(os.path.getsize(file_path))}
    params = {'fullpath': file_path}
    #response = requests.post(url, headers=headers, data=open(file_path, 'rb').read(), params=params)
    with open(file_path, 'rb') as data:
        response = requests.post(url, headers=headers, data=data, params=params)
    print('Status Code', response.status_code)


def process_media(full_path):
    file_path = os.path.normpath(full_path)
    if os.path.isdir(file_path):
        for filepath in os.listdir(file_path):
            if filepath.endswith('.srt'):
                process_media_file(os.path.join(full_path, filepath))
    elif os.path.isfile(full_path):
        process_media_file(full_path)


if __name__ == "__main__":
    with open('post.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    parser = Parser()
    parser.add_argument('-p', '--path', required=True, help='Path to the file or the folder: C:\\dev\\data\\poc_a1.srt')
    parser.add_argument('-t', '--type', required=True, help='Type of preocess m[edia], s[rt] or [f]ull')
    args = parser.parse_args()
    process_type = args.type
    file_path = args.path
    if process_type == 'm':
        process_media(file_path)
    elif process_type == 's':
        process_srt(file_path)
