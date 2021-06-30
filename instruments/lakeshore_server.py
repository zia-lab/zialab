
from flask import Flask, request
import serial

# This server works as a relay to control and query
# the Lakeshore controller through a serial connection.

comport = 'COM4'
timeout = 0.01
terminators = "\r\n"
flaskPort = 7777 # The TCP port at which the API will serve

ser = serial.Serial(comport, baudrate=57600,
                    parity=serial.PARITY_ODD, stopbits=1,
                    bytesize=7, timeout=timeout)

def query(message):
    """
    Send a message over the serial connection and return the reply.

    Input:
    message:    UTF-8 string to send to via the serial port (Do not include termination characters)

    Output:
    res:        A UTF-8 string containing the serial port response
    """
    ser.write((str(message) + terminators).encode())
    return ser.read(1000).decode()

# Initialize Flask API
app = Flask(__name__)

@app.route('/')
def readme():
    readmeh = '''Welcome to a world of heaters.'''
    return readmeh

@app.route('/commander')
def settemp():
    the_command = request.args.get('cmd')
    return query(the_command)

if __name__ == '__main__':
    app.run(port=flaskPort, threaded=False)
