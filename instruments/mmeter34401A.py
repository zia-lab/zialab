#!/usr/bin/env python3
# Use to connect to the Agilent Multimeter
# Coded by David on Jul 19 2019
# Only methods to query ac/dc current or voltage are currently included

#     _         _ _            _     _____ _  _   _  _    ___  _    _
#    / \   __ _(_) | ___ _ __ | |_  |___ /| || | | || |  / _ \/ |  / \
#   / _ \ / _` | | |/ _ \ '_ \| __|   |_ \| || |_| || |_| | | | | / _ \
#  / ___ \ (_| | | |  __/ | | | |_   ___) |__   _|__   _| |_| | |/ ___ \
# /_/   \_\__, |_|_|\___|_| |_|\__| |____/   |_|    |_|  \___/|_/_/   \_\
#         |___/

import serial
import sys

class Agilent34401A():
    def __init__(self, settings={}):
        self.defaults = {'port':'/dev/ttyUSB0',
            'baudrate':9600,
            'lf':'\r\n',
            'timeout': 0.5,
            'mode':'DC'}
        self.shortname = 'Multimeter'
        self.fullname = 'Agilent - 34401A Multimeter'
        self.manual_fname = './zialab/man/'+self.fullname + '.pdf'
        self.platform = sys.platform
        self.notes = '''This to read voltages, currents, and the like.'''
        if settings: # if settings are given, then set it up like so
            self.settings = settings
        else: # else use defaults
            print("Using default settings:")
            print(self.defaults)
            self.settings = self.defaults
        self.baudrate = self.settings['baudrate']
        self.port = self.settings['port']
        self.timeout = self.settings['timeout']
        self.lf = self.settings['lf']
        self.mode = self.settings['mode']
        try:
            print("Setting up the serial connection.")
            self.serialconn = serial.Serial(port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout)
            print("Setting up the system to remote mode...")
            self.sendtodev('SYST:REMOTE')
            print("Setting up the AC/DC mode...")
            self.sendtodev('CONF:VOLT:%s' % self.mode.upper())
        except:
            print("There was a problem setting up the serial connection.")
    def makecmd(self,command):
        '''composes command according to serial config'''
        return command+self.lf
    def sendtodev(self,command):
        '''sends command through the serial connection'''
        self.serialconn.write(self.makecmd(command).encode())
        return '\n'.join([s.decode()[:-2] for s in self.serialconn.readlines()])
    def get_dc_voltage(self):
        '''get DC voltage'''
        if self.mode.upper() != 'DC':
            print("Changing mode to DC.")
            self.sendtodev('CONF:VOLT:DC')
        return float(self.sendtodev('MEAS:VOLT:DC?'))
    def get_dc_current(self):
        '''get DC current'''
        if self.mode.upper() != 'DC':
            print("Changing mode to DC.")
            self.sendtodev('CONF:CURR:DC')
            self.mode = 'DC'
        return float(self.sendtodev('MEAS:CURR:DC?'))
    def get_ac_voltage(self):
        '''get AC voltage'''
        if self.mode.upper() != 'AC':
            print("Changing mode to AC.")
            self.sendtodev('CONF:VOLT:AC')
        return float(self.sendtodev('MEAS:VOLT:AC?'))
    def get_ac_current(self):
        '''get AC current'''
        if self.mode.upper() != 'AC':
            print("Changing mode to AC.")
            self.sendtodev('CONF:CURR:AC')
            self.mode = 'AC'
        return float(self.sendtodev('MEAS:CURR:AC?'))
