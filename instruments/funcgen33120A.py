#!/usr/bin/env python3
# Use to connect to the HP 33120A function generator
# Coded by David on March of 2023

import serial
import serial.tools.list_ports
from time import sleep
import sys
import numpy as np

class Agilent33120A():
    def list_ports():
        '''List the current computer's serial ports.'''
        ports = list(serial.tools.list_ports.comports())
        the_ports = []
        for port, desc, hwid in sorted(ports):
            the_ports.append((port,desc,hwid))
            print("{}: {} [{}]".format(port, desc, hwid))
        return the_ports
    def __init__(self, settings={}):
        self.defaults = {'port':'COM5',
            'baudrate':9600,
            'lf':'\r\n',
            'timeout': 0.5,
            'mode':'DC'}
        self.shortname = 'Function Generator'
        self.fullname = 'HP - 33120A Function Generator'
        # self.manual_fname = './zialab/man/'+self.fullname + '.pdf'
        self.platform = sys.platform
        self.notes = '''Source of all functions.'''
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
        self.wavetypes = ['SIN', 'SQU', 'TRI']
        self.max_freqs = {'SIN': 15e6, 'SQU': 15e6, 'TRI': 100e3}
        self.min_freqs = {'SIN': 1e-4, 'SQU': 1e-4, 'TRI': 1e-4}
        self.min_Vpp = 50e-3
        self.Vmax_options = {'INF': 10, '50': 5.}
        self.termination = '50'
        try:
            print("Setting up the serial connection.")
            self.serialconn = serial.Serial(port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout)
            print("Setting up the system to remote mode...")
            self.sendtodev('SYST:REMOTE')
        except:
            print("There was a problem setting up the serial connection.")
        print("Setting output termination to 50 Ohm.")
        self.set_output_termination(self.termination)
        self.max_Vpp = self.Vmax_options[self.termination]
    
    def makecmd(self,command):
        '''
        Composes command according to serial config.
        '''
        return command+self.lf

    def sendtodev(self,command):
        '''
        Sends command to device through the serial connection and return the response.
        '''
        self.serialconn.write(self.makecmd(command).encode())
        return '\n'.join([s.decode()[:-2] for s in self.serialconn.readlines()])

    def set_output_termination(self, termination):
        '''
        Parameters
        ----------
        termination : str
            Termination. Options are 50 or 1k.
        '''
        termination = str(termination)
        self.termination = termination
        assert termination in ['50', 'INF'], "Invalid termination,  has to be '50' or 'INF'."
        cmd = 'OUTPUT:LOAD %s' % termination
        try:
            rep = self.sendtodev(cmd)
            self.Vmax = self.Vmax_options[self.termination]
            return rep
        except:
           print("Error setting output termination.")
    
    def wave(self, wavetype, freq, ampl, offset):
        '''
        Sets the waveform, frequency, amplitude, and offset.
        Parameters
        ----------
        wavetype : str
            Type of waveform. Options are SIN, SQU, TRI.
        freq : float
            Frequency in Hz.
        ampl : float
            Amplitude in V.
        offset: float
            Offset in V.
        '''
        assert wavetype in self.wavetypes, "Invalid wavetype."
        assert freq >= self.min_freqs[wavetype], "Frequency too low."
        assert freq <= self.max_freqs[wavetype], "Frequency too high."
        assert ampl >= self.min_Vpp, "Amplitude too low."
        assert ampl <= self.max_Vpp, "Amplitude too high."
        cmd = "APPL:%s %f, %f, %f" % (wavetype, freq, ampl, offset)
        return self.sendtodev(cmd)
    
    def set_wavetype(self, wavetype):
        '''
        Parameters
        ----------
        wavetype : str
            Type of waveform. Options are SIN, SQU, TRI.
        '''
        assert wavetype in self.wavetypes, "Invalid wavetype."
        cmd = 'SOURCE:FUNCTION:SHAPE %s' % wavetype
        return self.sendtodev(cmd)

    def set_amplitude(self, amplitude_in_v):
        '''
        Parameters
        ----------
        amplitude_in_v : float
            Peak-to-peak amplitude in V.
        '''
        assert amplitude_in_v >= self.min_Vpp, "Amplitude too low."
        assert amplitude_in_v <= self.max_Vpp, "Amplitude too high."
        cmd = 'SOURCE:VOLT %f' % amplitude_in_v
        return self.sendtodev(cmd)

    def set_frequency(self, freq_in_Hz):
        '''
        Parameters
        ----------
        freq : float
            Frequency in Hz.
        '''
        wavetype = self.get_wavetype()
        assert freq_in_Hz >= self.min_freqs[wavetype], "Frequency too low."
        assert freq_in_Hz <= self.max_freqs[wavetype], "Frequency too high."
        cmd = 'SOURCE:FREQ %f' % freq_in_Hz
        return self.sendtodev(cmd)
    
    def set_offset(self, offset_in_v):
        '''
        Parameters
        ----------
        offset_in_v : float
            Offset in V.
        '''
        current_amp = self.get_amplitude()
        assert (abs(offset_in_v) + current_amp/2) <= self.max_Vpp, "Invalid offset."
        assert abs(offset_in_v) <= 2*current_amp, "Invalid offset."
        cmd = 'SOURCE:VOLT:OFFSET %f' % offset_in_v
        return self.sendtodev(cmd)

    def close(self):
        '''
        Close the serial connection.
        '''
        self.serialconn.close()

    def get_amplitude(self):
        '''
        Get the current peak-to-peak amplitude in V.
        '''
        cmd = 'SOURCE:VOLT?'
        ampl = self.sendtodev(cmd)
        try:
            ampl = float(ampl)
        except:
            print("Error while getting amplitude.")
            ampl = None
        return ampl

    def get_offset(self):
        '''
        Get the current offset.
        '''
        cmd = 'SOURCE:VOLT:OFFSET?'
        off = self.sendtodev(cmd)
        try:
            off = float(off)
        except:
            print("Error while getting offset.")
            off = None
        return off

    def get_frequency(self):
        '''
        Get the current frequency.
        '''
        cmd = 'SOURCE:FREQ?'
        freq = self.sendtodev(cmd)
        try:
            freq = float(freq)
        except:
            print("Error while getting frequency.")
            freq = None
        return freq

    def get_wavetype(self):
        '''
        Get the current wave form.
        '''
        cmd = 'SOURCE:FUNCTION:SHAPE?'
        return self.sendtodev(cmd)

    def smoothwave(self, wavetype, freq, ampl, offset, steps=10, duration=2):
        '''
        This function changes the wavetype to the given one, then smoothly
        changes the frequency, amplitude, and offset to the given values.
        Taking steps number of steps, for a total transition time of time_del.
        Parameters
        ----------
        wavetype : str
            Type of waveform. Options are SIN, SQU, TRI.
        freq : float
            Frequency in Hz.
        ampl : float
            Peak-to-peak amplitude in V.
        offset: float
            Offset in V.
        steps: int
            Number of steps to take.
        duration: float
            Total approx time for making change.
        Returns
        -------
        None
        '''
        self.set_wavetype(wavetype)
        current_offset = self.get_offset()
        current_amplitude = self.get_amplitude()
        current_frequency = self.get_frequency()
        if current_frequency == freq and current_amplitude == ampl and current_offset == offset:
            print("No change in parameters.")
            return None
        print("Current: freq : %f, ampl : %f, offset: %f" % (current_frequency, current_amplitude, current_offset))
        dt          = duration / steps
        offsets     = np.linspace(current_offset, offset, steps)
        amplitudes  = np.linspace(current_amplitude, ampl, steps)
        frequencies = np.linspace(current_frequency, freq, steps)
        for off, amp, freq in zip(offsets, amplitudes, frequencies):
            self.set_amplitude(amp)
            sleep(0.05)
            self.set_offset(off)
            sleep(0.05)
            self.set_frequency(freq)
            sleep(dt)
        current_offset = self.get_offset()
        current_amplitude = self.get_amplitude()
        current_frequency = self.get_frequency()
        print("Final: freq : %f, ampl : %f, offset: %f" % (current_frequency, current_amplitude, current_offset))
        return None
