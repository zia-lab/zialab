#!/usr/bin/env python3

import serial
import serial.tools.list_ports
from time import sleep
import sys

class NanoPZ():
    '''
    This class can be used to interface with a 
    Newport NanoPZ switchbox connected to linear actuators.
    By default it tries to find the device in COM5.
    '''
    def __init__(self, port='COM5'):
        self.serial_settings = {
            'baudrate':19200,
            'lf':'\r\n',
            'timeout': 0.5,
            'bytesize': serial.EIGHTBITS,
            'stopbits': serial.STOPBITS_ONE,
            'xonxoff': True,
            'parity': serial.PARITY_NONE}
        self.shortname    = 'NanoPZ'
        self.fullname     = 'Newport - NanoPZ'
        self.MAX_RETRIES  = 10
        self.platform     = sys.platform
        self.port         = port
        self.MAX_AMP      = 10000000
        self.line_feed    = '\r\n'
        self.start_serial()
        self.scan_and_connect()
        print('Turning on the motor...')
        self.set_motor_on()

    @staticmethod
    def list_ports():
        '''List the ports'''
        ports = list(serial.tools.list_ports.comports())
        the_ports = []
        for port, desc, hwid in sorted(ports):
            the_ports.append((port,desc,hwid))
            print('{}: {} [{}]'.format(port, desc, hwid))
        return the_ports

    def start_serial(self):
        self.serial_connection = serial.Serial(
            port      = self.port,
            baudrate  = self.serial_settings['baudrate'],
            timeout   = self.serial_settings['timeout'],
            bytesize  = self.serial_settings['bytesize'],
            stopbits  = self.serial_settings['stopbits'],
            xonxoff   = self.serial_settings['xonxoff'],
            parity    = self.serial_settings['parity']
        )
        print('Serial connection established.')

    def scan_and_connect(self):
        print('Scanning switchbox for controllers...')
        self.send_to_dev('1BX?')

    def make_cmd(self, command):
        return command + self.line_feed

    def send_to_dev(self, command):
        self.serial_connection.write(self.make_cmd(command).encode())
        return '\n'.join([s.decode()[:-2] for s in self.serial_connection.readlines()])

    def set_motor_off(self):
        self.send_to_dev('1MF')

    def set_motor_on(self):
        self.send_to_dev('1MO')

    def close(self):
        '''
        Close the serial connection.
        '''
        self.set_motor_off()
        self.serial_connection.close()
    
    def is_moving(self):
        '''
        Queries if the device is in motion,
        if it is, return True,
        if it is not, return False,
        if there's an error in querying, keep trying
        '''
        for _ in range(self.MAX_RETRIES):
            rep = self.send_to_dev('1TS?')
            if '1TS?' in rep:
                return rep.split(' ')[-1] == 'P'
            else:
                print('Error in querying motion, trying again ...')
                sleep(0.1)

    def read_position(self, axis):
        '''
        Read the current reading of the given axis.
        
        Parameters
        ----------
        axis (str): either 'x', 'y', or 'z'
        
        Returns
        -------
        position (int): in steps
        '''
        if len(axis) == 1:
            assert axis in ['x','y','z'], 'Invalid axis specified.'
            channel = channel = {'x':1, 'y':2, 'z': 3}[axis]
            current_channel = self.query_channel()
            if channel != current_channel:
                self.set_channel(channel)
            num_steps = int(self.send_to_dev('1TP?').split(' ')[-1])
            return num_steps
        else:
            return {single_axis: self.read_position(single_axis) for single_axis in axis}

    def set_channel(self, channel):
        '''
        Set the channel (axis) to which the controller is set to.
        If the channel is already set to the given channel, then nothing
        is done.
        '''
        if isinstance(channel, str):
            channel = channel.lower()
            assert channel in ['x','y','z']
            channel = {'x':1, 'y':2, 'z': 3}[channel]
        if self.query_channel() != channel:
            self.set_motor_off()
            self.send_to_dev('1MX%d' % channel)
            self.set_motor_on()

    def query_channel(self):
        '''
        Get the channel to which the controller is currently set to.
        '''
        rep     = self.send_to_dev('1MX?')
        channel = rep.split(' ')[-1]
        return int(channel)

    def relative_move(self, axis, step_size, unit='steps', wait = True):
        '''
        Make a relative move with the given axis.

        Parameters
        ----------
        axis (str)  : either 'x' or 'y' or 'z'
        step_size (int, or float if unit not steps) : how much to move
        wait (bool) : whether the function waits till stage stops moving
        unit (str)  : either 'nm', 'step_size', or 'um'

        Returns
        -------
        None
        '''
        if unit == 'steps':
            axis = axis.lower()
            assert (step_size >= -self.MAX_AMP) and (step_size <= self.MAX_AMP), 'step_size out of range'
            assert isinstance(step_size, int), 'step_size must be an integer'
            assert axis in ['x', 'y', 'z'], 'Invalid axis specified.'
            channel = {'x':1, 'y':2, 'z': 3}[axis]
            if self.query_channel() != channel:
                self.set_channel(channel)
            self.send_to_dev('1PR%d' % step_size)
            if wait:
                while self.is_moving():
                    continue
        elif unit in ['nm','um','mm']:
            divider = {'nm':10,'um':10/1000,'mm':10/1000/1000}[unit]
            step_size = round(step_size/divider)
            self.relative_move(axis, step_size, unit='steps', wait=wait)

