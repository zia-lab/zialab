#!/usr/bin/env python3

import serial, sys, atexit
from time import sleep

# defaults and notes
defaults = {
    'port':'COM12',
    'baudrate': 19200,
    'lf': '\r\n',
    'timeout': 0.1,
    'write timeout': 0.1,
    'latency_t': 0.1,
    'max_power': 0.5,
    'wavelength': 488 # [514,501,496,488,476,457]
    }

status_str='''LASER is {laser_status}
++++++++++
{sys_faults}
{hours_till_shutdown} hours till shutdown
current={current}A
power={power}W
status={laser_status}
mode={mode}
wavelength={wavelength}
{PT}'''

innova_notes = '''Innova is a fiery maelstrom of argon ions and its power
can be set high and mighty. Be sure to block the plasma glow, and to set
the wavelength you seek in the rear.'''

# if baudrate not right, baudrate can be seen and set in the remote control

class Innova300():
    def __init__(self,
                port=defaults['port'],
                baudrate=defaults['baudrate'],
                lf=defaults['lf'],
                verbose=False,
                dummy=False,
                max_power=defaults['max_power'],
                wavelength=defaults['wavelength']):
        self.port = port
        self.fullname = 'Coherent - Verdi'
        self.shortname = 'Verdi'
        self.max_power = max_power # in watts
        self.baudrate = baudrate
        self.port = port
        self.lf = lf
        self.notes = innova_notes
        self.platform = sys.platform
        self.timeout = defaults['timeout']
        self.write_timeout = defaults['write timeout']
        self.latency_t = defaults['latency_t']
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
        self.set_wavelength(wavelength)
        # print a status report
        status = {'PT': self.get_PT(),
                  'current': self.get_current(),
                  'power': self.get_power(),
                  'id': self.get_id(),
                  'laser_status': self.get_status(),
                  'mode': self.get_mode(),
                  'sys_faults': self.sendtodev('PRINT FAULTS'),
                  'wavelength': self.get_wavelength(),
                  'hours_till_shutdown': self.get_hours_till_shutdown()}
        assert status['id'] == 'I300', 'This device is not the I300.'
        print(status_str.format(**status))
    def makecmd(self,command):
        '''composes command according to serial config'''
        return command+self.lf
    def sendtodev(self,command):
        '''send commands through the serial connection'''
        self.serialconn.write(self.makecmd(command).encode())
        sleep(self.latency_t)
        return '\n'.join([s.decode()[:-2] for s in self.serialconn.readlines()])
    def get_current(self):
        '''get the current current'''
        reply = self.sendtodev('PRINT CURRENT')
        return reply
    def get_power(self):
        '''get the calibrated output power in Watts'''
        reply = self.sendtodev('PRINT LIGHT 3')
        return reply
    def get_water_flow(self):
        '''get the water flow in gallons per minute'''
        reply = self.sendtodev('PRINT FLOW')
        return reply
    def get_id(self):
        '''get the id of the laser'''
        reply = self.sendtodev('PRINT ID')
        return reply
    def get_status(self):
        '''get status of the laser'''
        reply = self.sendtodev('PRINT LASER')
        if reply == '0':
            return 'OFF'
        elif reply == '1':
            return 'IN START DELAY'
        elif reply == '2':
            return 'ON'
        else:
            return ''
    def get_mode(self):
        '''get the current mode of the laser'''
        reply = self.sendtodev('PRINT MODE')
        if reply == '0':
            return 'CURRENT REGULATION'
        elif reply == '1':
            return 'LIGHT REGULATION (REDUCED BANDWIDTH )'
        elif reply == '2':
            return 'LIGHT REGULATION (STANDARD)'
        elif reply == '3':
            return 'LIGHT REGULATION (OUT OF RANGE)'
    def get_PT(self):
        '''returns the status of PowerTrack'''
        reply = self.sendtodev('PRINT PT')
        if reply == '0':
            return 'PowerTrack not installed'
        elif reply == '-1':
            return 'PowerTrack is out of range'
        elif reply == '1':
            return 'PowerTrack is OFF'
        elif reply == '2':
            return 'PowerTrack is parked' # PT is selected but the PT servo is inactive
        elif reply == '3':
            return 'PowerTrack is ON'
        else:
            return ''
    def get_water_temperature(self):
        reply = self.sendtodev('PRINT WATER TEMPERATURE')
        return reply
    def get_hours_till_shutdown(self):
        reply = self.sendtodev('PRINT HRSTILSHUTDOWN')
        return reply
    def set_power(self, power_in_watts):
        '''if not in light-regulated mode, mode will be changed by this
        power must be given in watts'''
        if power_in_watts > self.max_power:
            return 'power out of set maximum of %.1f' % self.max_power
        else:
            reply = self.sendtodev('LIGHT=%.4f' % power_in_watts)
            return self.get_power()
    def close_serial(self):
        self.serialconn.close()
    def off(self):
        '''set the laser OFF'''
        reply = self.sendtodev('LASER=0')
    def on(self):
        '''set the laser ON(1) or OFF(0)'''
        reply = self.sendtodev('LASER=1')
    def get_wavelength(self):
        reply = self.sendtodev('PRINT WAVELENGTH')
        return reply
    def set_wavelength(self, wave):
        '''this only changes the wavelength that the internal power meter
        assumes, actual wavelength needs to be changed manually'''
        if wave in [514,501,496,488,476,457]:
            reply = self.sendtodev('WAVELENGTH=%d' % wave)
        else:
            return 'wavelength not valid'
    def flip_mirror(self,dir):
        if dir == 'up':
            self.sendtodev('STATUS=2')
            sleep(0.1)
            self.sendtodev('STATUS=2')
        elif dir == 'down':
            self.sendtodev('STATUS=1')
            sleep(0.1)
            self.sendtodev('STATUS=1')
    atexit.register(close_serial)
