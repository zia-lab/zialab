#!/usr/bin/env python3

# Module for controlling our Acton Monochromators via USB serial
# Coded by David on Jan 2022

import serial, sys, os, atexit
from time import sleep

class Monochromator:
    defaults = {
        'port' :  'COM5',
        'timeout': 0.1,
        'write_timeout': 0.1,
        'lf': '\r',
        'latency_t': 0.1
    }
    if sys.platform == 'win32':
        defaults['port'] = 'COM5'
    def __init__(self,
                port = defaults['port'],
                verbose=False,
                dummy=False):
        # must match name of pdf filename, save the extension
        self.fullname = 'Princeton Instruments - Monochromator'
        self.shortname = 'Monochromator'
        self.port = port
        self.lf = self.defaults['lf']
        self.platform = sys.platform
        self.timeout = self.defaults['timeout']
        self.write_timeout =  self.defaults['write_timeout']
        self.latency_t = self.defaults['latency_t']

    def open(self):
        self.serialconn = serial.Serial(port=self.port, timeout=self.timeout, write_timeout=self.write_timeout)
        atexit.register(self.close)

    def close(self):
        self.serialconn.close()

    def makecmd(self,command):
        '''composes command according to serial config'''
        return command + self.lf

    def sendtodev(self,command):
        '''send commands through the serial connection'''
        self.serialconn.write(self.makecmd(command).encode())
        sleep(self.latency_t)
        return self.serialconn.read_until().decode().strip()

    def reconnect(self,
            port=defaults['port'],
            lf=defaults['lf']):
        '''restablish the serial connection'''
        self.port = port
        self.lf = lf
        if self.verbose: print("Reconnecting...")
        self.serialconn = serial.Serial(port=self.port,
                            timeout=self.timeout,
                            write_timeout=self.write_timeout)

    def get_position(self):
        '''get the current position in calibrated nm'''
        mono_position = self.sendtodev('?NM')
        try:
            mono_position = float(mono_position.split('nm')[0].strip())
        except:
            mono_position = None
        return (mono_position)

    def has_reached_destination(self):
        '''check to see if monochromator has reached target destination'''
        reply = self.sendtodev('MONO-?DONE').split(' ')[0]
        return reply == '1'

    def set_position(self, position_in_nm):
        '''set the position in calibrated nm'''
        self.sendtodev('%.3f NM' % position_in_nm)
        while not self.has_reached_destination():
            print('.', end='')
            sleep(self.latency_t)
        # for some reason the cache is filled after this
        # need to flush it
        '\n'.join([s.decode()[:-2] for s in self.serialconn.readlines()])

    def set_speed(self, speed_in_nm_per_min):
        try:
            reply = self.sendtodev('%.2f NM/MIN' % speed_in_nm_per_min)
            speed = float(reply.split('nm/min')[0])
        except:
            speed = None

    def get_speed(self):
        try:
            reply = self.sendtodev('?NM/MIN')
            speed = float(reply.split('nm/min')[0])
        except:
            speed = None
        return speed
