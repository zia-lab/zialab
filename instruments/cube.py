#!/usr/bin/env python3

############################################
#   ____      _            _  _    ___  _  #
#  / ___|   _| |__   ___  | || |  / _ \/ | #
# | |  | | | | '_ \ / _ \ | || |_| | | | | #
# | |__| |_| | |_) |  __/ |__   _| |_| | | #
#  \____\__,_|_.__/ \___|    |_|  \___/|_| #
#                                          #
############################################

# Coded by David on Jul 16 2019
# Improved on July of 2020 to use in pulsed mode

import serial, sys, os, atexit
from time import sleep

class Cube:
    defaults = {
        'port' :  '/dev/ttyUSB0',
        'baudrate' : 19200,
        'lf' : '\r\n',
        'timeout': 0.1, # as per the serial conn
        'write_timeout': 0.1, # as per the serial conn
        'latency_t': 0.1 # used here and there as needed
    }
    if sys.platform == 'win32':
        defaults['port'] = 'COM4'
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
        self.cdrh = 0
        self.HID = 'F96021702 1139602 401'
        self.platform = sys.platform
        self.timeout = self.defaults['timeout']
        self.latency_t = self.defaults['latency_t']
        self.write_timeout = self.defaults['write_timeout']
        self.notes = 'Cube is a tiny little thing, with a so-so single-mode.'
        # set up the serial connection
        if not dummy:
            if port == 'auto':
                print('finding port keeping the platform in mind...')
            else:
                # try:
                self.serialconn = serial.Serial(port=self.port,
                                    baudrate=self.baudrate,
                                    timeout=self.timeout,
                                    write_timeout=self.write_timeout)
                # except:
                #     print("Error: check connections and make sure serial is configured correctly.")
        else:
            self.serialconn = 'dummy'
        self.set_cdrh(self.cdrh)
        atexit.register(self.close)
    def close(self):
        self.off()
        self.serialconn.close()
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
    def set_cdrh(self,cdrh_state):
        if cdrh_state not in [0,1]:
            return "invalid cdrh state"
        self.sendtodev(self.makecmd('CDRH=%d') % cdrh_state)
    def set_mode(self,mode):
        mode = mode.lower()
        if mode not in ["cw","pulsed"]:
            return "Invalid mode"
        if mode == 'cw':
            self.sendtodev(self.makecmd('CW=1'))
        else:
            self.sendtodev(self.makecmd('CW=0'))
    def cls(self):
        '''clear the queue on the laser'''
        self.sendtodev(self.makecmd('CLS'))
    def state(self):
        '''query the current light-emission state of the laser'''
        cube_state = self.sendtodev('?L').split('=')[-1]
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
    def ping(self):
        try:
            pong = self.sendtodev('?HID')
        except:
            print("Failed in reaching device...")
            pong = 'failed'
        return (pong  == self.HID)

    def on(self):
        '''turn the laser on'''
        self.sendtodev('L=1')
        # if self.get_operation_status() == 'standby':
        #     self.sendtodev('L=1')
        #     print("Laser was in standby.")
        # return self.sendtodev('CW=1')
    def off(self):
        '''turn the laser off'''
        self.sendtodev('L=0')
        # return self.sendtodev('CW=0')
    def set_pulsed_power(self,power_in_mW):
        '''set the power'''
        cube_reply=self.sendtodev('CAL=%f' % power_in_mW)
    def set_power(self,power_in_mW):
        '''set the power'''
        cube_reply=self.sendtodev('P=%f' % power_in_mW)
        cube_power = self.get_power()
        return str(cube_reply)
    def get_power(self):
        '''get the power'''
        cube_power = self.sendtodev('?P').split('=')[-1]
        return cube_power
    def get_set_power(self):
        '''get the currently set power'''
        cube_power = self.sendtodev('?SP').split('=')[-1]
        self.set_power = cube_power
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
