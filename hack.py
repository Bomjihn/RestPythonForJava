from flask import Flask, render_template
from flask_socketio import SocketIO
import subprocess
import os
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

def stream_output(process, stream):
    while True:
        output = stream.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            socketio.emit('log message', {'message': output.strip().decode("utf-8")}, namespace='/test')

@socketio.on('execute command', namespace='/test')
def test_message(message):

    command = message['command']
    print("User Input: " + command)

    if "pip" in command:
        temp = command.split()
        command = ""
        for index, value in enumerate(temp):
            if index != 0:
                command = command + value + " "
        command = "miniconda3/bin/python -m pip " + command

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Real-time logging
    threading.Thread(target=stream_output, args=(process, process.stdout)).start()
    threading.Thread(target=stream_output, args=(process, process.stderr)).start()

if __name__ == '__main__':
    # check if the file exists
    file_path = './port.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            port = int(file.read().strip())
    else:
        print('Введите порт вашего сервера: ')
        port = int(input())
        # create the file and write the port
        with open(file_path, 'w') as file:
            file.write(str(port))

    socketio.run(app, host='0.0.0.0', port=port)