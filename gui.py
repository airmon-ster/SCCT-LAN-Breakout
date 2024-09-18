
# Documentation:
#   https://flask.palletsprojects.com/en/3.0.x/

import subprocess
import os
import sys
from flask import Flask, request, jsonify, render_template, redirect
# import numpy as np
import requests
import base64
import re
import platform
from flask_cors import CORS
import psutil
import json
import webbrowser

WIREGUARD_SERVER = '20.55.32.50'

# WORKSAFE=False
# try:
#     from gevent.pywsgi import WSGIServer
# except Exception as e:
#     print(e)
#     WORKSAFE=True


def get_platform_type():
    system = platform.system()
    return system


def run_with_switches(system):
    webbrowser.open_new_tab('http://127.0.0.1:8000')#'https://www.splintercellonline.net/')

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

# Enable CORS with specific configurations
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:8000", "https://www.splintercellonline.net"]  # "http://www.splintercellonline.net",
    },
})

# getting the name of the directory
# where the this file is present.
path = os.path.dirname(os.path.realpath(__file__))

# Global variable to keep track of the subprocess
script_process = None


def run_scct_script(args):
    global script_process
    script_process = subprocess.Popen([sys.executable] + args)

# def run_scct_script(args):
#     global script_process
#     startupinfo = None

#     if os.name == 'nt':  # Check if the OS is Windows
#         # This will hide the console window on Windows
#         startupinfo = subprocess.STARTUPINFO()
#         startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

#     script_process = subprocess.Popen(
#         [sys.executable] + args,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         startupinfo=startupinfo
#     )


# Routes
@app.route('/')
def index():
    # Retrieve data from query parameters
    data = {
        'django_username': request.args.get('django_username'),
        'username': request.args.get('username'),
        'discord_id': request.args.get('discord_id'),
        'avatar': request.args.get('avatar'),
        'role': request.args.get('role'),
        'email': request.args.get('email'),
        'status': request.args.get('status'),
        'reason': request.args.get('reason')
    }

    # file_path = f'{os.path.dirname(os.path.realpath(__file__))}/templates/index.html'

    # with open(file_path, 'r') as file:
    #     html = ''
    #     for line in file:
    #         html += line

    #     return render_template_string(html)
    return render_template('index.html', data=data)


def obfuscate_ip(ip: str) -> str:
    # Encode the IP address using Base64
    encoded_ip = base64.urlsafe_b64encode(ip.encode())
    return encoded_ip.decode()


def deobfuscate_ip(obfuscated_ip: str) -> str:
    # Decode the Base64 encoded IP address
    decoded_ip = base64.urlsafe_b64decode(obfuscated_ip.encode())
    return decoded_ip.decode()


@app.route('/scops')
def scops():
    return redirect('http://127.0.0.1:8000')#'https://www.splintercellonline.net/')#'http://127.0.0.1:8001')#'https://www.splintercellonline.net/')


@app.route('/api/get_id', methods=['GET'])
def get_id():
    # Get the data from the request
    # data = request.json.get('data') # for POST requests with data
    # from python_modules import python_modules
    # go_message = python_modules.main()
    # ip = requests.get('https://api.ipify.org').text.strip()
    # user_id = obfuscate_ip(ip)
    try:
        with open('wg0.conf','r') as f:
            config = f.read()
            # Regular expression to capture PublicKey and AllowedIPs
            int_regex = r'\[Interface\]\s*PrivateKey\s*=\s*(\S+)\s*Address\s*=\s*(\S+)'

            interfaces = re.findall(int_regex, content)

            if interfaces:
                for i, interface in enumerate(interfaces, 1):
                    priv_key, address = interface

            peer_regex = r'\[Peer\]\s*PublicKey\s*=\s*(\S+)\s*Endpoint\s*=\s*(\S+)\s*AllowedIPs\s*=\s*(\S+)'

            peers = re.findall(peer_regex, content)

            if peers:
                for i, peer in enumerate(peers, 1):
                    pub_key, endpoint, allowed_ips = interface

        return jsonify({
            'status':'success',
            'client_ip': address
            })
    except Exception as e:
        return jsonify({
            'status':'fail',
            })

@app.route('/api/create_config', methods=['POST'])
def create_config():
    data = request.json  # for POST requests with data
    client_ip = data.get('client_ip')
    private_key = data.get('private_key')
    server_pub_key = data.get('server_pub_key')
    ps2_ip = data.get('ps2_ip')
    content = f'''
[Interface]
PrivateKey = {private_key}
Address = {client_ip}
#DNS = 10.0.0.1  # Optional: Use this if you want DNS queries to go through the VPN

[Peer]
PublicKey = {server_pub_key}
Endpoint = {WIREGUARD_SERVER}:51820
AllowedIPs = {ps2_ip}/24, {WIREGUARD_SERVER}/32  # Sends all traffic through the VPN
PersistentKeepalive = 25  # Helps with NAT traversal
    '''
    try:
        with open('wg0.conf', 'w') as f:
            f.write(content)
        return jsonify({'status':'success'})
    except Exception as e:
        return jsonify({'status':'fail','message':'Error: '+e})

@app.route('/api/connect', methods=['POST'])
def connect():
    global script_process
    # Get the data from the request
    data = request.json  # for POST requests with data
    client_ip = data.get('client_ip')
    ps2_ip = data.get('ps2_ip')
    adapter = 'wg0'
    # ipv4_pattern = re.compile(r'^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$')
    # count = 0
    # if not ipv4_pattern.match(host_ip) and '.' not in host_ip:
    #     host_ip = deobfuscate_ip(host_ip)
    try:
        #detect unix/win os
        system = get_platform_type()
        if system == 'Darwin' or system == 'Linux':
            #run wireguard command
            command = [
                'sudo',
                'wg-quick',
                'up',
                'wg0.conf'
            ]
            print("Running command:", command)
            subprocess.Popen(command)
        else:
            #run wireguard command
            command = [
                'wireguard',
                '/installtunnelservice',
                'wg0.conf'
            ]
            print("Running command:", command)
            subprocess.Popen(command)
            # PowerShell command to get the InterfaceIndex for wg0 interface
            ps_command = 'Get-NetIPInterface | Where-Object { $_.InterfaceAlias -like "*wg0*" } | Where-Object { $_.AddressFamily -like "*IPv4*" } | Select-Object -ExpandProperty InterfaceIndex'

            # Run the PowerShell command using subprocess
            result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
            # Print the output
            if result.returncode == 0:
                interface_index = result.stdout.strip()  # Get the interface index from the output
            else:
                return jsonify({'status':'fail','message':f"Error: {result.stderr}"})
            ps_command = f'route add {ps2_ip} mask 255.255.255.255 10.0.0.1 metric 1 if {interface_index}'
            # Run the PowerShell command using subprocess
            result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)            
            if result.returncode != 0:
                return jsonify({'status':'fail','message':f"Error: {result.stderr}"})

        # # # Construct the path to scct.py one directory back
        # scct_script_path = os.path.join(os.path.dirname(__file__), 'scct.py')

        # args = [scct_script_path, 'client', '--remote', client_ip, '--nic', adapter]
        # # Start the script in a separate subprocess
        # run_scct_script(args)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status':'fail','message':'Error: '+e})

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    global script_process
    # Get the data from the request
    try:
        #detect unix/win os
        system = get_platform_type()
        if system == 'Darwin' or system == 'Linux':
            #run wireguard command
            command = [
                'sudo',
                'wg-quick',
                'down',
                'wg0.conf'
            ]
            print("Running command:", command)
            subprocess.Popen(command)
        else:
            #run wireguard command
            command = [
                'wireguard',
                '/uninstalltunnelservice',
                'wg0.conf'
            ]
            print("Running command:", command)
            subprocess.Popen(command)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status':'fail','message':'Error: '+e})


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


@app.route('/api/check_localhost_app', methods=['GET'])
def check_localhost_app():
    return jsonify({'status': 'success'})

@app.route('/api/get_network_adapters', methods=['GET'])
def get_network_adapters():
    adapters = psutil.net_if_addrs()
    network_adapters = list(adapters.keys())
    return jsonify({'nics':network_adapters})


if __name__ == '__main__':
    stop_previous_flask_server()

    pid_file = f'{os.path.expanduser("~")}/flask_server.pid'
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))  # Write the PID to the file

    # ADD SPLASH SCREEN?

    # Get current system type
    system = get_platform_type()

    # Run Apped Chrome Window
    run_with_switches(system)

    # if WORKSAFE == False:
    #     http_server = WSGIServer(("127.0.0.1", 8000), app)
    #     http_server.serve_forever()
    # else:
    app.run(debug=True, threaded=True, port=8001, use_reloader=False)
