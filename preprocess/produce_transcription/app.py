#!/usr/bin/python
import os
import sys
import signal
import posixpath
import ntpath
from os import path
import logging
import json
import csv
import shutil
import argparse
import subprocess
import traceback
from datetime import datetime
from flask import Flask
from flask import request
from flask import jsonify
from pathlib import Path
import faster_whisper
common_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(common_path)
import tools

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename=os.path.basename(__file__).replace('py', 'log'), mode='w', encoding='utf-8')
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

datetime_fmt = "%Y_%m_%d-%H:%M:%S"
# Check if NVIDIA GPU is available
# cuda, float16
# cpu, int8
DEVICE = "cpu" # cuda, cpu
COMPUTE_TYPE = "int8" # float16, int8_float16, int8
model = None

'''
import torch
def force_cudnn_init():
    s = 32
    dev = torch.device('cuda')
    torch.nn.functional.conv2d(torch.zeros(s, s, s, s, device=dev), torch.zeros(s, s, s, s, device=dev))
torch.cuda.empty_cache()
force_cudnn_init()
'''

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("uncaught exception:", exc_value)
sys.excepthook = handle_exception


@app.route('/', methods=["POST", "GET"])
def main_route():
    result = []
    result.append('/process_srt: input srt, output with entities')
    result.append('All the files must be in utf-8 format with CR LF at eol')
    return 'NEW_LINE'.join(result)


@app.route('/shutdown', methods=["POST", "GET"])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)


def video2mp3(video_fullpath: str, mp3_fullpath: str) -> int:
    #filename, ext = os.path.splitext(video_fullpath)
    return_code = subprocess.call(["ffmpeg", "-y", "-i", video_fullpath, mp3_fullpath],stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    return return_code


def get_mediainfo(media_fullpath: str) -> str:
    command = ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,height,width,display_aspect_ratio', '-of', 'default=noprint_wrappers=1', media_fullpath]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = process.communicate()
    if error:
        logger.info(error)
    res = out.decode("utf-8").splitlines()
    audio = True if 'codec_type=audio' in res else False
    video = False
    if 'codec_type=video' in res:
        width_item = [item for item in res if item.startswith('width')]
        if len(width_item) > 0:
            width = width_item[0].split('=')[1]
            if width != '64':
                video = True
        height_item = [item for item in res if item.startswith('height')]
        if len(height_item) > 0:
            height = height_item[0].split('=')[1]
            if height != '64':
                video = True
        display_aspect_ratio_item = [item for item in res if item.startswith('display_aspect_ratio')]
        if len(display_aspect_ratio_item) > 0:
            display_aspect_ratio = display_aspect_ratio_item[0].split('=')[1]
            if display_aspect_ratio != '1:1':
                video = True

    codecs = []
    if audio:
        codecs.append('a')
    if video:
        codecs.append('v')
    return ','.join(codecs)


def create_srt_file(full_path="transcribe.srt", results=None, fast_whisper=True):
    try:
        os.remove(full_path)
    except OSError:
        pass
    with open(full_path, mode="w", encoding='utf-8-sig') as file_dst:
        for index, _dict in enumerate(results):
            if fast_whisper:
                start_time = _dict.start #_dict[2]#_dict[0] # start
                end_time = _dict.end #_dict[3]#_dict[1] # end
                text = _dict.text #_dict[4]#_dict[2] # text
            else:
                start_time = _dict["start"]
                end_time = _dict["end"]
                text = _dict["text"]
            s_h, e_h = int(start_time//(60 * 60)), int(end_time//(60 * 60))
            s_m, e_m = int((start_time % (60 * 60))//60), int((end_time % (60 * 60))//60)
            s_s, e_s = int(start_time % 60), int(end_time % 60)
            file_dst.write(f'{index+1}\n{s_h:02}:{s_m:02}:{s_s:02},000 --> {e_h:02}:{e_m:02}:{e_s:02},000\n{text}\n\n')


def srt_to_text(lines):
    text = ""
    for line in lines:
        line = line.strip()
        if "-->" in line:
            continue
        if line.isnumeric() or line == '':
            continue
        text += line + "\n"
    return text.strip()


def create_txt_file(src_fullpath, dst_fullpath):
    with open(src_fullpath, "r", encoding="utf-8") as file:
        lines = file.readlines()
    with open(dst_fullpath, "w", encoding="utf-8") as file:
        file.write(srt_to_text(lines))     


def create_info_file(dst_basename, fullpath, language):
    filename = dst_basename + ".info.json"
    try:
        os.remove(filename)
    except OSError:
        pass
    mt = get_mediainfo(fullpath)
    data = {
        "version": 1,
        "media_path": fullpath,
        "media_type": mt,
        "language": language
    }
    with open(filename, mode="w", encoding="utf-8") as file_info:
        json.dump(data, file_info, ensure_ascii=False, indent=4)


@app.route('/process_media', methods=["POST"])
def process_audio(fullpath=None):
    by_request = True if fullpath is None else False

    if by_request:
        fullpath = request.args['fullpath'].replace(ntpath.sep, posixpath.sep)

    logger.info(f"Processing: {fullpath}")
    filename = os.path.splitext(os.path.basename(fullpath))[0]

    #app.logger.info(f"Processing: {fullpath}")
    tmp_folder = path.join(config['output'], "tmp")
    Path(tmp_folder).mkdir(parents=True, exist_ok=True)

    local_fullpath = path.join(tmp_folder, os.path.basename(fullpath))

    if by_request:
        # Convert stream to wav
        chunk_size = 1024
        with open(local_fullpath, 'wb') as dst_file:
            while True:
                chunk = request.stream.read(chunk_size)
                if not chunk:
                    break
                dst_file.write(chunk)
    else:    
        shutil.copyfile(fullpath, local_fullpath)

    language = ''
    percent = ''
    comment = ''
    try:
        srt_folder = path.join(config['output'], "srt")
        Path(srt_folder).mkdir(parents=True, exist_ok=True)
        dst_basename = path.join(srt_folder, filename)

        srt_fullpath = os.path.splitext(fullpath)[0] + ".srt"
        if os.path.exists(srt_fullpath):
           shutil.copyfile(srt_fullpath, dst_basename + ".srt") 
           comment = 'external srt'
        else:
            segments, info = model.transcribe(local_fullpath, beam_size=5, language=config['language'])
            #segments, info = model.transcribe(local_fullpath, beam_size=5, language=config['language'], temperature=0.2)
            language = info.language
            percent = info.language_probability
            #print("For '%s' detected language '%s' with probality %f" % (fullpath, info.language, info.language_probability))

            if language == config['language']:
                logger.info("Transcription started")
                segments = list(segments)  # The transcription will actually run here.
                logger.info("Transcription ended")
                create_srt_file(full_path=dst_basename + ".srt", results=segments, fast_whisper=True)
                app.logger.info(f"Created {dst_basename}.srt file")
            
        if os.path.exists(dst_basename + ".srt"):
            create_info_file(dst_basename, fullpath, language)
            txt_folder = path.join(config['output'], "txt")
            Path(txt_folder).mkdir(parents=True, exist_ok=True)
            create_txt_file(dst_basename + ".srt", path.join(txt_folder, filename + ".txt"))
    except Exception as exc:
        #dst_folder = traceback.format_exception(*sys.exc_info())
        comment = str(exc)
        logger.error(f"{datetime.now().strftime(datetime_fmt)},{fullpath},{str(exc)}")

    if os.path.isfile(config['report_file']):
        with open(config['report_file'], 'a', encoding='utf-8') as report_file:
            report_file.write(f"{datetime.now().strftime(datetime_fmt)}#{fullpath}#{language}#{percent}#{comment}\n")
    #logger.info(f"{datetime.now().strftime(datetime_fmt)},{fullpath},{language},{dst_folder}")
    os.remove(local_fullpath)
    if by_request:
        if language == 'ERROR':
            return jsonify(sucess=False)
        else:
            return jsonify(sucess=True)


if __name__ == "__main__":
    logger.info("Program running")
    parser = argparse.ArgumentParser()
    parser.add_argument('-mp', '--model_path')
    parser.add_argument('-l', '--language')
    parser.add_argument('-p', '--path', required=False, help='Path to the file or the folder: C:\\dev\\data\\poc_a1.wav')
    parser.add_argument('-o', '--output')
    parser.add_argument('-f', '--from', required=False, help='Format: YYYY_MM_DD')
    config = tools.Configuration(__file__.replace("py", "json"), parser)
    logger.info(config)
    # Only for internal use
    # os.environ["HUGGINGFACE_HUB_CACHE"] = config["model_path"]
    model = faster_whisper.WhisperModel(config['model_path'], device=DEVICE, compute_type=COMPUTE_TYPE)
    Path(config['output']).mkdir(parents=True, exist_ok=True)
    config['report_file'] = path.join(config['output'], "report_srt.csv")
    from_time = None if config['from'] is None else datetime.strptime(config['from'], "%Y_%m_%d")
    #logger.info(f"Time,Fullpath,Language,DstFolder")
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
                    report_file.write(f"Time#Fullpath#Language#%#Comment\n")
            filenames = [filename for filename in os.listdir(arg_path) if os.path.isfile(os.path.join(arg_path, filename))]
            for filename in filenames:
                filepath = os.path.join(arg_path, filename)
                file_mt = datetime.fromtimestamp(os.path.getmtime(filepath))
                exists = next((item for item in report_data if item['Fullpath'] == filepath), None)
                if exists is None or (from_time is not None and file_mt > from_time):
                    file_rootname, file_extension = os.path.splitext(filename)
                    if file_extension.lower() in tools.multimedia_extensions:
                        process_audio(filepath)

        elif os.path.isfile(arg_path):
            process_audio(arg_path)
    else:
        host = config['host']
        port = config['port']
        print(f"Domain: http://{host}:{port}")
        app.run(debug=True, host=host, port=port)

