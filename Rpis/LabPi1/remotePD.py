#!/usr/bin/python3
from flask import Flask, request
import subprocess

log_fname = '/home/pi/Log/volt.log'

# Initialize Flask API
app = Flask(__name__)

FlaskPort = 7777 # The TCP port at which the API will serve

@app.route('/')
def readme():
    readmeh = '''Welcome to photodiode.'''
    return readmeh

@app.route('/getvoltage')
def getem():
    num_recs = request.args.get('num_recs')
    skip = request.args.get('skip')
    result = subprocess.run(['tail','-n%s' % num_recs,log_fname],
                            stdout=subprocess.PIPE)
    data = result.stdout.decode().split('\n')
    bits = '\n'.join(data[::-int(skip)])
    return bits

if __name__ == '__main__':
    # Setup the serial device
    app.run(
        host='0.0.0.0',#host=PI_IP,
       port=7777
    )
