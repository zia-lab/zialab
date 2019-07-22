#!/usr/bin/env python3

import serial
from time import sleep
import sys
import os

############################################
#   ____      _            _  _    ___  _  #
#  / ___|   _| |__   ___  | || |  / _ \/ | #
# | |  | | | | '_ \ / _ \ | || |_| | | | | #
# | |__| |_| | |_) |  __/ |__   _| |_| | | #
#  \____\__,_|_.__/ \___|    |_|  \___/|_| #
#                                          #
############################################

# Coded by David on Jul 16 2019

######## TO DO ########
# test in windows
# automatic port detection
# include analog mode case
#######################

# defaults and others
global defaults
global cube_notes
defaults = {
'port' :  '/dev/ttyUSB0',
'baudrate' : 19200,
'lf' : '\r\n',
'timeout': 0.1, # as per the serial conn
'write_timeout': 0.1, # as per the serial conn
'latency_t': 0.1 # used here and there as needed
}

# add comments here
cube_notes = '''
Cube is a tiny little thing.
'''

class Cube:
    def __init__(self,
                port=defaults['port'],
                baudrate=defaults['baudrate'],
                lf=defaults['lf'],
                verbose=False,
                dummy=False):
        # must match name of pdf filename, save the extension
        self.fullname = 'Coherent - Cube 401'
        self.manual_fname = './zialab/Manuals/'+self.fullname + '.pdf'
        self.shortname = 'Cube'
        self.wavelength = '401'
        self.baudrate = baudrate
        self.port = port
        self.lf = lf
        self.platform = sys.platform
        self.timeout = defaults['timeout']
        self.latency_t = defaults['latency_t']
        self.write_timeout = defaults['write_timeout']
        self.notes = cube_notes
        # set up the serial connection
        if not dummy:
            if port == 'auto':
                print('finding port keeping the platform in mind...')
            else:
                try:
                    self.serialconn = serial.Serial(port=self.port,
                                        baudrate=self.baudrate,
                                        timeout=self.timeout,
                                        write_timeout=self.write_timeout)
                except:
                    print("Error: check connections and make sure serial is configured correctly.")
        else:
            self.serialconn = 'dummy'
    def makecmd(self,command):
        '''composes command according to serial config'''
        return command+self.lf
    def sendtodev(self,command):
        '''send commands through the serial connection'''
        self.serialconn.write(self.makecmd(command).encode())
        sleep(self.latency_t)
        return '\n'.join([s.decode()[:-2] for s in self.serialconn.readlines()])
    def manual(self):
        '''open the pdf manual'''
        platform_open_cmds = {'linux':'xdg-open','darwin':'open'}
        try:
            print("Opening the manual.")
            os.system('%s "%s"' % (platform_open_cmds[self.platform],self.manual_fname))
        except:
            print("wups, could not open")
    def cls(self):
        '''clear the queue on the laser'''
        self.sendtodev(self.makecmd('CLS'))
    def state(self):
        '''query the current state of the laser'''
        cube_state = self.sendtodev('?CW').split('=')[-1]
        if cube_state == '0':
            return "off"
        if cube_state == '1':
            return "on"
        return "error"
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
        if self.get_operation_status() == 'standby':
            self.sendtodev('L=1')
            print("Laser was in standby.")
        return self.sendtodev('CW=1')
    def off(self):
        '''turn the laser off'''
        return self.sendtodev('CW=0')
    def set_power(self,power_in_mW):
        '''set the power'''
        cube_reply=self.sendtodev('P=%f' % power_in_mW)
        self.cls()
        cube_power = self.get_power()
        return str(cube_reply)
    def get_power(self):
        '''get the power'''
        cube_power = self.sendtodev('?P').split('=')[-1]
        self.cw_power = cube_power
        return cube_power
    def get_fault_list(self):
        '''query faults'''
        fault_list = self.sendtodev("?FL")
        self.fault_list = fault_list
        return fault_list
    def get_operation_status(self):
        '''get op status'''
        self.opstatus = self.sendtodev("?STA").split('=')[-1]
        if self.opstatus == '1':
            self.opstatus = 'warmp-up'
        if self.opstatus == '2':
            self.opstatus = 'standby'
        if self.opstatus == '3':
            if self.sendtodev('?CW').split('=')[-1] == '1':
                self.opstatus = 'laser ready and on'
            else:
                self.opstatus = 'laser ready but off'
        if self.opstatus == '4':
            self.opstatus = 'error'
        if self.opstatus == '5':
            self.opstatus = 'fatal error'
        return self.opstatus
    def get_full_status(self):
        '''get the status'''
        self.status = self.sendtodev("?S")
        return self.status
