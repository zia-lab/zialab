import ctypes,time,struct,requests,sys,os
#from System.IO import *
#from System import string
#from System.Collections.Generic import List
from ctypes import *
import pyPICommands as gcs
# from PrincetonInstruments.LightField.Automation import Automation
# from PrincetonInstruments.LightField.AddIns import ExperimentSettings
# from PrincetonInstruments.LightField.AddIns import DeviceType

# Functions that control the Verdi-V5 532 CW laser, by initiating web requests to a Ras.Pi that talks to the laser.
class VerdiV5():

    VERDI_PI_IP='128.148.54.172'

    def __init__(self):
        pass

    # open or close the shutter.
    def set_shutter(self,shutter):
        '''
        Open (1) or close (0) the shutter. Function returns the queried state of
        the shutter right after being set.
        '''
        return int(requests.get('http://%s:7777/setverdi/shutter?shutter=%d'%(self.VERDI_PI_IP,shutter)).content)

    # open the laser shutter.
    def open(self):
        self.set_shutter(1)
        print('Verdi-V5:\nLaser is ON.\n')

    # close the laser shutter.
    def close(self):
        self.set_shutter(0)
        print('Verdi-V5:\nLaser is OFF.\n')

    # get the status of shutter.
    def get_shutter(self):
        '''
        Open (1) or close (0) the shutter. Function returns the queried state of
        the shutter right after being set.
        '''
        return int(requests.get('http://%s:7777/qverdi/shutter'%(self.VERDI_PI_IP)).content)

    # set the output power of laser.
    def set_power(self,power):
        '''
        Set the power of Verdi in W. Function returns the power queried on the
        Verdi after being set.
        '''
        return float(requests.get('http://%s:7777/setverdi/power?power=%f'%(self.VERDI_PI_IP,power)).content)

    def get_calpower(self):
        '''
        Get the calibrated power in W.
        '''
        return float(requests.get('http://%s:7777/qverdi/calpower'%self.VERDI_PI_IP).content)

    # return the current output power of the lasre.
    def get_power(self):
        '''
        Get the regulated power in W.
        '''
        return float(requests.get('http://%s:7777/qverdi/regpower'%self.VERDI_PI_IP).content)


# Functions to control PicoHarp300 single photon counting module, by directly loading and using the functions in the dll.
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
        pass

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


# Functions to control Physik M687 stage, by directly loading and using the functions in the dll.
class M687():

    pi = gcs.pyPICommands("PI_GCS2_DLL_x64.dll","PI_")

    def __init__(self):
        pass

    # write any of the allowed gcs commands to the controller.
    def gcs_cmd(self,cmd):
        self.pi.GcsCommandset(cmd)

    # establish connection to the stage by connecting through a virtual serial port(usb masked as RS232) with specific baunt rate.
    #       it also performs a maintanence run(moving both x and y for 10mm) to spread out the lubricant and achieve optimal performance.
    def open(self):
        if self.pi.ConnectRS232(13,115200)==True:
            print('M687:\nStage is CONNECTED.')
            #print('Checking servo states and reference modes...')
            self.gcs_cmd('SVO x 1')
            time.sleep(0.1)
            self.gcs_cmd('SVO y 1')
            #print('servo states: ON.')
            self.gcs_cmd('RON x 1')
            time.sleep(0.1)
            self.gcs_cmd('RON y 1')
            time.sleep(0.1)
            print('reference mode: REFERENCED.')
            # self.gcs_cmd('VEL x 1')
            # time.sleep(0.1)
            # self.gcs_cmd('VEL y 1')
            time.sleep(0.1)
            print('Stage is performing a maintanence run....')
            self.move_x(5)
            time.sleep(1)
            self.move_x(-5)
            time.sleep(1)
            self.move_x(0)
            time.sleep(1)
            self.move_y(5)
            time.sleep(1)
            self.move_y(-5)
            time.sleep(1)
            self.move_y(0)
            print('Maintanence run finished. Stage is now READY.\n')
        else:
            raise TypeError('Stage was not found.')

    # close the connection with the stage.
    def close(self):
        self.pi.CloseConnection()
        print('M687:\nStage is DISCONNECTED.\n')

    # get the answer string of any gcs command that were sent to the stage. (e.g. returns the velocity if one used a command to query the velocity)
    def gcs_answer(self):
        answer=''
        answer_size=self.pi.GcsGetAnswerSize()
        while answer_size!='':
            answer+=self.pi.GcsGetAnswer()
            answer_size=self.pi.GcsGetAnswerSize()
        return answer

    # determines whether either of the axes have reached target position for at least a pre-set amount of the settling time.
    def is_on_target(self,axis):
        self.pi.GcsCommandset('ONT? '+axis)
        if self.pi.GcsGetAnswer()[2]=='1':
            return True
        else:
            return False

    # query both x and y positions of the stage.
    def qPOS(self):
        self.pi.GcsCommandset(chr(5))
        while self.pi.GcsGetAnswer()=='1':
            pass
        position=self.pi.qPOS('x y')
        return [position['x'],position['y']]

    # move the stage in the x-axis.
    def move_x(self,x):
        t0_x=time.time()
        self.pi.GcsCommandset('MOV x '+str(x))
        while not (self.is_on_target('x')) and (time.time()-t0_x<10):
            pass

    # move the stage in the y-axis.
    def move_y(self,y):
        t0_y=time.time()
        self.pi.GcsCommandset('MOV y '+str(y))
        while not self.is_on_target('y') and (time.time()-t0_y<10):
            pass

    # configure the CTO setting so that the stage sends out trigger signals with a specific trigger step size, range, velocity etc.)
    def setCTO(self,StartThreshold,StopThreshold,velocity,TriggerStep,Axis='x',Polarity=1,TriggerMode=0): # Configure the CTO
        self.gcs_cmd('TRO 2 1')
        self.gcs_cmd('CTO 2 1 '+str(TriggerStep))
        self.gcs_cmd('CTO 2 2 '+Axis)
        self.gcs_cmd('CTO 2 3 '+str(TriggerMode))
        self.gcs_cmd('CTO 2 8 '+str(StartThreshold))
        self.gcs_cmd('CTO 2 9 '+str(StopThreshold))
        self.gcs_cmd('CTO 2 10 '+str(StartThreshold))
        self.gcs_cmd('VEL x '+str(velocity))
        self.gcs_cmd('VEL y '+str(velocity))

    # turn on the TRO trigger output channel 2 on the controller.
    def TRO_ON(self):
        self.gcs_cmd('TRO 2 1')

    # turn off the TRO trigger output channel 2 on the controller.
    def TRO_OFF(self):
        self.gcs_cmd('TRO 2 0')

    # set the velocity of the stage.
    def setvel(self,v_x,v_y): # Set the velocity of the stage
        gcscmd('VEL x '+str(v_x))
        gcscmd('VEL y '+str(v_y))


class ProEM():

    def __init__(self):
        pass


class SCT320():
    pass
