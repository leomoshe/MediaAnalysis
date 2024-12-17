#!/usr/bin/python
import subprocess
import time
import socket
import logging
import json
import os
import psutil
import requests
from flask import Flask
from flask import request


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename='main.log', mode='w', encoding='utf-8')
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_process_id(entrypoint_fullpath):
    return os.path.split(os.path.dirname(entrypoint_fullpath))[-1]


def config_by_id(server_id):
    res = next((item for item in config['dependencies'] if item['id'] == server_id), None)
    return res


class ServerManager:
    def __init__(self):
        self.processes = []

    @staticmethod
    def get_process_id(entrypoint_fullpath):
        return get_process_id(entrypoint_fullpath) #return os.path.split(os.path.dirname(entrypoint_fullpath))[-1]

    # Technicals debt:
    # 1) send command like: 'tasklist /v /fo CSV /fi "IMAGENAME eq cmd.exe" | findstr "process_srt"'
    # 2) Instead Popen, run with capture_output=True, text=True, shell=True
    # 3) use of psutil.process_iter
    def get_process(self, entrypoint_fullpath):
        entrypoint_fullpath = os.path.abspath(entrypoint_fullpath)
        # cmd = 'tasklist /v /fo CSV /fi "IMAGENAME eq cmd.exe" | findstr "process_srt"'
        # process = subprocess.run([cmd], capture_output=True, text=True, shell=True)
        tasklist = subprocess.Popen(['tasklist', '/v', '/fo', 'CSV', '/fi', "IMAGENAME eq cmd.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = tasklist.stdout.read()
        # stderr = tasklist.stderr.read()
        tasklist_data = stdout.decode().split('\r\n')
        process_id = ServerManager.get_process_id(entrypoint_fullpath)
        process_data = list(filter(lambda item: process_id in item, tasklist_data))
        if len(process_data) == 0:
            return None
        process_pid = int(process_data[0].split('"')[3])
        return psutil.Process(process_pid)


    def server_status(self, url, max_attemps=10, interval=2):
        attemps=0
        while attemps < max_attemps:
            try:
                response = requests.get(url, timeout=1)
                response.raise_for_status()
                print(f"The server {url} is running")
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
                print(f"Attemps {attemps+1}: The server {url} isn't running")
                time.sleep(interval)
                attemps += 1
        else:
            print("The server {url} can't run")


    def run_server(self, python_fullpath, entrypoint_fullpath):
        python_fullpath = os.path.abspath(python_fullpath)
        entrypoint_fullpath = os.path.abspath(entrypoint_fullpath)
        p_id = get_process_id(entrypoint_fullpath)
        conf_server = config_by_id(p_id)
        port = conf_server['port']
        subprocess.Popen(["start", "cmd", "/K", python_fullpath, entrypoint_fullpath], cwd=os.path.dirname(entrypoint_fullpath), shell=True)
        self.server_status(f'http://localhost:{port}/')
        server_process = self.get_process(entrypoint_fullpath)
        self.processes.append({"process": server_process, "port": port})
        print(f"{python_fullpath} run the script {entrypoint_fullpath} on port {port} with PID: {server_process.pid}")


    def find_available_port(self, base_port=5001):
        for port in range(base_port, base_port + 51):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                if soc.connect_ex(("localhost", port)) != 0:
                    return port
        return None


    def monitor_servers(self):
        while True:
            for process in self.processes:
                if process.poll() is not None:  # Proces has terminated
                    print(f"Script with PID {process.pid} has terminated.")
                    self.processes.remove(process)
            time.sleep(10)


    def finalize(self):
        for process in self.processes:
            process["process"].terminate()
            target_url = f'http://localhost:{process["port"]}/shutdown'
            response = requests.post(target_url)
            return response.text, response.status_code, response.headers.items()


@app.route('/', methods=["POST", "GET"])
def main_route():
    result = []
    result.append('/process_srt: input srt, output with entities')
    result.append('All the files must be in utf-8 format with CR LF at eol')
    return 'NEW_LINE'.join(result)


@app.route('/process_srt', methods=["POST"])
def process_srt():
    server_id = request.path.replace('/', '')
    server_config = config_by_id(server_id)
    app.logger.info(f"{server_id} called")
    headers = request.headers
    params = request.args
    data = request.get_data()
    server_port = server_config['port']
    target_url = f'http://localhost:{server_port}/{server_id}'
    response = requests.post(target_url, headers=headers, data=data, params=params)
    return response.text, response.status_code, response.headers.items()


@app.route('/process_media', methods=["POST"])
def process_media():
    server_id = request.path.replace('/', '')
    server_config = config_by_id(server_id)
    app.logger.info(f"{server_id} called")
    headers = request.headers
    params = request.args
    data = request.get_data()
    server_port = server_config['port']
    target_url = f'http://localhost:{server_port}/{server_id}'
    response = requests.post(target_url, headers=headers, data=data, params=params)
    return response.text, response.status_code, response.headers.items()


if __name__ == "__main__":
    app.logger.info("Program running")
    with open('app.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    server_manager = ServerManager()

    for server in config['dependencies']:
        server_manager.run_server(f".\\{server['id']}\\.venv\\Scripts\\python.exe", f".\\{server['id']}\\app.py")
    main_host = config['host']
    main_port = config['port']
    print(f"Domain: http://{main_host}:{main_port}")
    app.run(host=main_host, port=main_port, debug=False, use_reloader=False)
    server_manager.finalize()
    print('finish')
