#!/usr/bin/env python3

# Module for controlling an OBIS Coherent laser
# Coded by David on Jun 14 2021

import serial, sys, os, atexit
from time import sleep

class Obis:
    defaults = {
        'port' :  '/dev/ttyUSB0',
        'baudrate' : 19200,
        'lf' : '\r\n',
        'timeout': 0.1, # as per the serial conn
        'write_timeout': 0.1, # as per the serial conn
        'latency_t': 0.1 # used here and there as needed
    }
    if sys.platform == 'win32':
        defaults['port'] = 'COM3'
    def __init__(self,
                port=defaults['port'],
                baudrate=defaults['baudrate'],
                lf=defaults['lf'],
                verbose=False,
                dummy=False):
        # must match name of pdf filename, save the extension
        self.fullname = 'Coherent - Obis 405'
        self.shortname = 'Obis'
        self.wavelength = 403
        self.baudrate = baudrate
        self.port = port
        self.lf = lf
        self.cdrh = 'OFF'
        self.platform = sys.platform
        self.timeout = self.defaults['timeout']
        self.latency_t = self.defaults['latency_t']
        self.write_timeout = self.defaults['write_timeout']
        self.notes = 'Obis is a tiny diode laser, but a good one.'

    def open(self):
        self.serialconn = serial.Serial(port=self.port,baudrate=self.baudrate,timeout=self.timeout,write_timeout=self.write_timeout)
        self.set_cdrh(self.cdrh)
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
        return '\n'.join([s.decode()[:-2] for s in self.serialconn.readlines()])

    def set_cdrh(self,cdrh_state):
        cdrh_state = cdrh_state.upper()
        if cdrh_state not in ["ON","OFF"]:
            return "invalid cdrh state"
        self.sendtodev('SYST:CDRH %s' % cdrh_state)

    def set_mode(self,mode):
        mode = mode.lower()
        if mode not in ["cw","pulsed"]:
            return "Invalid mode"
        if mode == 'cw':
            self.sendtodev('SOUR:AM:INT CWP')
        else:
            self.sendtodev('SOUR:AM:EXT DIG')

    def state(self): #n
        '''query the current light-emission state of the laser'''
        obis_state = self.sendtodev('SOUR:AM:STAT?').split('\n')[0]
        return obis_state

    def reconnect(self,
            port=defaults['port'],
            baudrate=defaults['baudrate'],
            lf=defaults['lf']):
        '''restablish the serial connection'''
        self.port = port
        self.baudrate = baudrate
        self.lf = lf
        if self.verbose: print("Reconnecting...")
        self.serialconn = serial.Serial(port=self.port,
                            baudrate=self.baudrate,
                            timeout=self.timeout,
                            write_timeout=self.write_timeout)

    def on(self):
        '''turn the laser on'''
        self.sendtodev('SOUR:AM:STAT ON')

    def off(self):
        '''turn the laser off'''
        self.sendtodev('SOUR:AM:STAT OFF')

    def set_power_in_mW(self,power_in_mW):
        '''set the power in mW, can be set to five sig figs'''
        obis_reply=self.sendtodev('SOUR:POW:LEV:IMM:AMPL %.5f' % (power_in_mW/1000))
        obis_power = self.get_power_in_mW()
        return str(obis_reply)

    def get_power_in_mW(self):
        '''get the current power in mW'''
        obis_power = self.sendtodev('SOUR:POW:LEV?').split('\n')[0]
        return float(obis_power)*1000

    def get_set_power_in_mW(self):
        '''get the currently set power'''
        obis_power = self.sendtodev('SOUR:POW:LEV:IMM:AMPL?').split('\n')[0]
        return float(obis_power)*1000

    def get_operating_mode(self):
        '''get op status'''
        self.opmode = self.sendtodev("SOUR:AM:SOUR?").split('\n')[0]
        return self.opmode
