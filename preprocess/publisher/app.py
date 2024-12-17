#!/usr/bin/python
import os
import sys
from os import path
from pathlib import Path
import shutil
import logging
import json
import argparse
import subprocess
from datetime import datetime
common_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(common_path)
import tools

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename=os.path.basename(__file__).replace('py', 'log'), mode='w', encoding='utf-8')
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

datetime_fmt = "%Y_%m_%d-%H:%M:%S"
postfix_len = len("_XXXXXXXX_XXXXXX.tsrt.csv")
def common_tsrt_basefilename(fullpath):
    return os.path.basename(fullpath)[:-postfix_len]


def copy_file(src_fullpath, dst_folder):
    dst_fullpath = os.path.join(dst_folder, os.path.basename(src_fullpath))
    if os.path.exists(dst_fullpath):
        return None
    try:
        #shutil.copy2(src_fullpath, dst_fullpath)
        cmd = f'sudo cp "{src_fullpath}" "{dst_fullpath}"'
        subprocess.call(cmd, shell=True)
        return dst_fullpath
    except Exception as exc:
        print(f"Error copying files: {exc}")

if __name__ == "__main__":
    #app.logger.info("Program running")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project')
    parser.add_argument('-l', '--local_container')
    parser.add_argument('-d', '--destination')
    config = tools.Configuration(__file__.replace("py", "json"), parser)
  
    local_folder = os.path.join(config['local_container'], config['project'])

    config['report_file'] = path.join(local_folder, "report_publisher.csv")
    if not os.path.isfile(config['report_file']):
        with open(config['report_file'], 'w', encoding='utf-8') as report_file:
            report_file.write(f"Time#DestinationTsrt#DestinationSrt#\n")

    src_tsrt_folder = os.path.join(local_folder, 'tsrt')
    src_srt_folder = os.path.join(local_folder, 'srt')
    dst_tsrt_folder = os.path.join(config['destination'], config['project'])
    dst_srt_folder = os.path.join(config['destination'], config['project'], 'srt')   

    src_tsrt_filespath = [os.path.join(src_tsrt_folder, filename) for filename in os.listdir(src_tsrt_folder) if os.path.isfile(os.path.join(src_tsrt_folder, filename))]
    for src_tsrt_filepath in src_tsrt_filespath:
        base_filename = common_tsrt_basefilename(src_tsrt_filepath)
        
        dst_tsrt_filepath = [dst_tsrt for dst_tsrt in os.listdir(dst_tsrt_folder) if common_tsrt_basefilename(dst_tsrt) == base_filename]
        if len(dst_tsrt_filepath) == 0:
            dst_tsrt_filepath = copy_file(src_tsrt_filepath, dst_tsrt_folder)
        else:
            dst_tsrt_filepath = None

        #dst_srt_filepath = [dst_srt for dst_srt in os.listdir(dst_srt_folder) if os.path.basename(dst_srt) == base_filename + ".srt"]
        #if len(dst_srt_filepath) == 0:
        src_srt_filepath = os.path.join(src_srt_folder, base_filename + ".srt")
        dst_srt_filepath = copy_file(src_srt_filepath, dst_srt_folder)
        
        if dst_tsrt_filepath is not None or dst_srt_filepath is not None:
            with open(config['report_file'], 'a', encoding='utf-8') as report_file:
                report_file.write(f"{datetime.now().strftime(datetime_fmt)}#{dst_tsrt_filepath}#{dst_srt_filepath}\n")

