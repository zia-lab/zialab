#!/usr/bin/env python3

import serial
from time import sleep
import atexit
import sys

# defaults and notes
global defaults
global verdi_notes
defaults = {
'port': '/dev/ttyUSB0',
'baudrate': 19200,
'lf': '\r\n',
'timeout': 0.1,
'write timeout': 0.1
}
verdi_notes = '''Verdi is green and mighty.
It's power can be set to a precision of 0.0001 W!'''

class Verdi():
    def __init__(self,
                port=defaults['port'],
                baudrate=defaults['baudrate'],
                lf=defaults['lf'],
                verbose=False,
                dummy=False):
        self.fullname = 'Coherent - Verdi'
        self.shortname = 'Verdi'
        self.manual_fname = './zialab/man/'+self.fullname + '.pdf'
        self.wavelength = '532'
        self.max_power = 0.5 # in watts
        self.baudrate = baudrate
        self.port = port
        self.lf = lf
        self.platform = sys.platform
        self.timeout = defaults['timeout']
        self.write_timeout = defaults['write timeout']
        self.latency_t = defaults['latency_t']
        self.notes = verdi_notes
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
    def manual(self):
        '''open the pdf manual'''
        platform_open_cmds = {'linux':'xdg-open','darwin':'open'}
        try:
            print("Opening the manual.")
            os.system('%s "%s"' % (platform_open_cmds[self.platform],self.manual_fname))
        except:
            print("wups, could not open")
    def makecmd(self,command):
        '''composes command according to serial config'''
        return command+self.lf
    def sendtodev(self,command):
        '''send commands through the serial connection'''
        self.serialconn.write(self.makecmd(command).encode())
        sleep(self.latency_t)
        return '\n'.join([s.decode()[:-2] for s in self.serialconn.readlines()])
    # set
    def set_shutter(self,shutter):
        '''set the shutter: 0=closed, 1=opened'''
        if int(shutter) == 0: #close verdi
            self.sendtodev('S=0')
        if int(shutter) == 1: #open verdi
            self.sendtodev('S=1')
        return get_shutter()
    def set_power(self,power_in_watts):
        '''set the power, give in watts'''
        power=round(float(power_in_watts),4)
        if 0<=power<=self.max_power:
            verdi_reply = self.sendtodev('P='+str(power))
        else:
            verdi_reply = 'Invalid power setting.'
        return get_regulated_power()
    # get
    def get_regulated_power(self):
        '''get the power from verdi'''
        verdi_reply = self.sendtodev('?SP')
        return verdi_reply
    def get_calibrated_power(self):
        '''get the calibrated power'''
        verdi_reply = self.sendtodev('?P')
        return verdi_reply
    def get_shutter(self):
        '''get the shutter state'''
        verdi_reply = self.sendtodev('?S')
        return verdi_reply
