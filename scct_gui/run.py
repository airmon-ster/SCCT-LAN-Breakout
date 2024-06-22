
# Documentation:
#   https://flask.palletsprojects.com/en/3.0.x/

import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
import random
from flask import Flask, render_template, render_template_string, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
# import numpy as np
import random
import json
import requests
import base64
import re
import importlib
import threading


# WORKSAFE=False
# try:
#     from gevent.pywsgi import WSGIServer
# except Exception as e:
#     print(e)
#     WORKSAFE=True
        
def run_with_switches():
    # Check the default browser
    if os.path.exists("C:/Program Files/Google/Chrome/Application/chrome.exe"):
        command = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe", 
            '--app=http://127.0.0.1:8000', 
            '--disable-pinch', 
            '--disable-extensions', 
            '--guest'
        ]
        print("Running command:", command)
        subprocess.Popen(command)
        return
    elif os.path.exists("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"):
        command = [
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", 
            '--app=http://127.0.0.1:8000', 
            '--disable-pinch', 
            '--disable-extensions', 
            '--guest'
        ]
        print("Running command:", command)
        subprocess.Popen(command)
        return

    print("Chromium-based browser not found or default browser not set.")

def stop_previous_flask_server():
    try:
        # Read the PID from the file
        with open(f'{os.path.expanduser("~")}/flask_server.pid', 'r') as f:
            pid = int(f.read().strip())
        
        # # Check if the Flask server process is still running
        # while True:
        #     if not os.path.exists(f'/proc/{pid}'):
        #         break  # Exit the loop if the process has exited
        #     time.sleep(1)  # Sleep for a short duration before checking again

        # Terminate the Flask server process
        command = f'taskkill /F /PID {pid}'
        subprocess.run(command, shell=True, check=True)
        print("Previous Flask server process terminated.")
    except Exception as e:
        print(f"Error stopping previous Flask server: {e}")

app = Flask(__name__)

# getting the name of the directory
# where the this file is present.
path = os.path.dirname(os.path.realpath(__file__))

# Global variable to keep track of the subprocess
script_process = None

def run_scct_script(args):
    global script_process
    script_process = subprocess.Popen([sys.executable] + args)

# Routes
@app.route('/')
def index():
    html = """
   
    """

    file_path = f'{os.path.dirname(os.path.realpath(__file__))}/templates/index.html'

    with open(file_path, 'r') as file:
        html = ''
        for line in file:
            html += line
            
        return render_template_string(html)
        # return render('index.html')

def obfuscate_ip(ip: str) -> str:
    # Encode the IP address using Base64
    encoded_ip = base64.urlsafe_b64encode(ip.encode())
    return encoded_ip.decode()

def deobfuscate_ip(obfuscated_ip: str) -> str:
    # Decode the Base64 encoded IP address
    decoded_ip = base64.urlsafe_b64decode(obfuscated_ip.encode())
    return decoded_ip.decode()

@app.route('/api/get_id', methods=['GET'])
def get_id():
    # Get the data from the request
    # data = request.json.get('data') # for POST requests with data
    # from python_modules import python_modules
    # go_message = python_modules.main()
    ip = requests.get('https://api.ipify.org').text.strip()
    user_id = obfuscate_ip(ip)

    return jsonify({'user_id': user_id})

@app.route('/api/run_server', methods=['POST'])
def run_server():
    global script_process
    # Get the data from the request
    data = request.json # for POST requests with data
    ps2_ip = data.get('ps2_ip')
    players = data.get('players')
    ipv4_pattern = re.compile(r'^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$')
    for idx, item in enumerate(players):
        if not ipv4_pattern.match(item):
            players[idx] = deobfuscate_ip(item)

    # Construct the path to scct.py one directory back
    scct_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'scct.py')

    args = [scct_script_path, 'server', '--sip', ps2_ip, '--players'] + players
    # Start the script in a separate subprocess
    run_scct_script(args)

    return jsonify({'status': 'done'})

@app.route('/api/connect', methods=['POST'])
def connect():
    global script_process
    # Get the data from the request
    data = request.json # for POST requests with data
    host_ip = data.get('host_ip')
    ipv4_pattern = re.compile(r'^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$')
    count = 0
    if not ipv4_pattern.match(host_ip):
        host_ip = deobfuscate_ip(host_ip)

    # Construct the path to scct.py one directory back
    scct_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'scct.py')

    args = [scct_script_path, 'client', '--remote', host_ip]
    # Start the script in a separate subprocess
    run_scct_script(args)

    return jsonify({'status': 'done'})

@app.route('/api/end_connection', methods=['GET'])
def end_connection():
    global script_process
    if script_process is not None:
        script_process.terminate()
        script_process.wait()
        script_process = None
        return jsonify({'status': 'stopped'})
    else:
        return jsonify({'status': 'not running'}), 400

if __name__ == '__main__':
    stop_previous_flask_server()

    pid_file = f'{os.path.expanduser("~")}/flask_server.pid'
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))  # Write the PID to the file
    
    # ADD SPLASH SCREEN?

    # Run Apped Chrome Window
    run_with_switches()

    # if WORKSAFE == False:
    #     http_server = WSGIServer(("127.0.0.1", 8000), app)
    #     http_server.serve_forever()
    # else:
    app.run(debug=True, threaded=True, port=8000, use_reloader=False)  

    