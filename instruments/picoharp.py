# coded by Yang Wang circa 2019

import sys
import ctypes
from ctypes import *

class PicoHarp300():
    ph = ctypes.CDLL("phlib64.dll")
    T2WRAPAROUND = 210698240
    device=[]
    device_found=0
    MAXDEVNUM = 8
    serial='12345678'
    TTREADMAX = 131072
    FLAG_OVERFLOW = 0x0040
    FLAG_FIFOFULL = 0x0003
    binning = 0 # you can change this, meaningful only in T3 mode
    offset = 0 # you can change this, meaningful only in T3 mode
    syncDivider = 1 # you can change this, observe mode! READ MANUAL!
    CFDZeroCross0 = 10 # you can change this (in mV)
    CFDLevel0 = 50 # you can change this (in mV)
    CFDZeroCross1 = 10 # you can change this (in mV)
    CFDLevel1 = 150 # you can change this (in mV)
    ###############################################
    # Variables to store information read from DLLs
    buffer = (ctypes.c_uint * TTREADMAX)()
    hwSerial = ctypes.create_string_buffer(b"", 8)
    hwPartno = ctypes.create_string_buffer(b"", 8)
    hwVersion = ctypes.create_string_buffer(b"", 8)
    hwModel = ctypes.create_string_buffer(b"", 16)
    errorString = ctypes.create_string_buffer(b"", 40)
    resolution = ctypes.c_double()
    countRate0 = ctypes.c_int()
    countRate1 = ctypes.c_int()
    flags = ctypes.c_int()
    nactual = ctypes.c_int()
    ctcDone = ctypes.c_int()
    warnings = ctypes.c_int()
    warningstext = ctypes.create_string_buffer(b"", 16384)
    def __init__(self):
        self.shortname = 'picoharp'
        self.fullname = 'PicoQuant - PicoHarp 300'
        self.manual_fname = './zialab/man/' + self.fullname + '.pdf'
        self.platform = sys.platform
    # search for and open the connected picoharp device. Also initalize and calibrate the setting.
    def open(self,mode='T3'):
        for i in range(self.MAXDEVNUM):
            if self.ph.PH_OpenDevice(i,self.serial)==0:
                self.device=self.device+[i]
                self.device_found+=1
                print('PicoHarp300:\nPicoharp device found with device index of %d.' % (self.device[0]))
                print('Initializing...')
            else:
                pass
        if self.ph.PH_Initialize(self.device[0],int(mode[1]))==0:
            self.ph.PH_Calibrate(self.device[0])
            print('Picoharp successfully intialized in T%d mode.\n' % int(mode[1]))
    # ask the picoharp to start a measurement.(i.e. picoharp will start to record data into its buffer.)
    def start_measurement(self,acq_time):
        if self.ph.PH_StartMeas(self.device[0],acq_time*1000)==0:
            pass
    # stop measurement(stop recording events into the physical buffer.)
    def stop_measurement(self):
        if self.ph.PH_StopMeas(self.device[0])==0:
            pass
    # flags are basically error codes for picoharp, there is no description of all the flag values in the manual but
    #       we know few of the flags that are definitely bad.
    def get_flag(self):
        if self.ph.PH_GetFlags(self.device[0],byref(self.flags))==0:
            return self.flags.value;
    # close the picoharp device.
    def close(self):
        if self.ph.PH_CloseDevice(self.device[0])==0:
            print('PicoHarp300:\nPicoharp is DISCONNECTED.\n')
    # use the get counts function to get counts in either or both channels.
    def get_counts(self,channel_0=True,channel_1=True):
        self.ph.PH_GetCountRate(self.device[0],0,byref(self.countRate0))
        self.ph.PH_GetCountRate(self.device[0],1,byref(self.countRate1))
        if channel_0==True:
            if channel_1==True:
                print('Channel 0: %d counts/s \nChannel 1: %d counts/s\n' % (self.countRate0.value,self.countRate1.value))
                return self.countRate0.value,self.countRate1.value;
            else:
                print('Channel 0: %d counts/s' % (self.countRate0.value))
                return self.countRate0.value
        else:
            if channel_1==True:
                print('Channel 1: %d counts/s' % (self.countRate1.value))
                return self.countRate1.value
            else:
                pass
    # read the data/events recorded and stored in the buffer and write the results to an output file.
    def read_buffer(self,output_file,number_of_markers_expected):
        with open(output_file,'wb+') as outputfile:
            read_values=0
            counter=0
            while read_values<number_of_markers_expected and counter<5:
                self.ph.PH_GetFlags(self.device[0], byref(self.flags))

                if self.flags.value == 48:# or flags.value == 8:
                    break

                self.ph.PH_ReadFiFo(self.device[0], byref(self.buffer), self.TTREADMAX, byref(self.nactual))

                read_values=self.nactual.value
                counter+=1

                if self.nactual.value > 0:
                    outputfile.write((ctypes.c_uint*self.nactual.value)(*self.buffer[0:self.nactual.value]))
