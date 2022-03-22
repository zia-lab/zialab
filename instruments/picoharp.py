#!/usr/bin/env python3

# coded by Yang Wang circa 2019

import sys
import ctypes
from ctypes import *
import struct
import numpy as np
from time import sleep

class PH300():
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
    flags = ctypes.c_int32()
    nactual = ctypes.c_int()
    ctcDone = ctypes.c_int()
    warnings = ctypes.c_int()
    warningstext = ctypes.create_string_buffer(b"", 16384)

    def __init__(self):
        self.shortname = 'picoharp'
        self.fullname = 'PicoQuant - PicoHarp 300'
        self.manual_fname = './zialab/man/' + self.fullname + '.pdf'
        self.platform = sys.platform

    def open(self,mode='T3'):
        '''
        Search for and open the connected Picoharp device.
        Initalize and set it up in the given mode.
        '''
        for i in range(self.MAXDEVNUM):
            if self.ph.PH_OpenDevice(i,self.serial)==0:
                self.device=self.device+[i]
                self.device_found+=1
                print('PicoHarp300:\nPicoharp device found with device index of %d.' % (self.device[0]))
            else:
                pass
        if self.ph.PH_Initialize(self.device[0],int(mode[1]))==0:
            self.ph.PH_Calibrate(self.device[0])
            print('Picoharp successfully intialized in T%d mode.\n' % int(mode[1]))

    def start_measurement(self,acq_time):
        '''
        Tell picoharp to start a measurement and record data into its buffer.
        acq_time given in seconds
        '''
        if self.ph.PH_StartMeas(self.device[0], int(acq_time*1000))==0:
            pass
        else:
            print("error in starting measurement")

    def stop_measurement(self):
        '''
        Tell Picoharp to stop recording events into the physical buffer.
        '''
        if self.ph.PH_StopMeas(self.device[0])==0:
            pass
        else:
            print("error stopping measurement")

    def get_flag(self):
        '''
        Flags are basically error codes for Picoharp, there is no
        description of all the flag values in the manual but
        we know few of the flags that are definitely bad. ?????????
        '''
        if self.ph.PH_GetFlags(self.device[0],byref(self.flags)) == 0:
            return self.flags.value

    def close(self):
        '''
        Close Picoharp
        '''
        if self.ph.PH_CloseDevice(self.device[0])==0:
            print('Picoharp is DISCONNECTED.')

    def get_counts(self,channel_0=True,channel_1=True):
        '''
        Get countrates in channels.
        '''
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

    def read_fifo(self, num_records=TTREADMAX):
        '''
        read the buffer and return a numpy array with its data
        '''
        buffer = np.zeros(num_records, dtype=np.uint32)
        actual_num_records = ctypes.c_int32()
        self._dll.PH_ReadFiFo(self.device[0], buffer.ctypes.data,
                            num_records, ctypes.byref(actual_num_records))
        return (buffer, actual_num_records)

    def read_buffer(self,output_file,number_of_markers_expected):
        '''
        read the data/events recorded and stored in the buffer and write the results to an output file.
        '''
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

    def open(self,mode='T3'):
        '''
        Search for and open the connected Picoharp device.
        Initalize and set it up in the given mode.
        '''
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

    def start_measurement(self,acq_time):
        '''
        Tell picoharp to start a measurement and record data into its buffer.
        '''
        if self.ph.PH_StartMeas(self.device[0],int(acq_time*1000))==0:
            pass
        else:
            print("problem starting measurement")

    def stop_measurement(self):
        '''
        Tell Picoharp to stop recording events into the physical buffer.
        this also clears the buffer.
        '''
        if self.ph.PH_StopMeas(self.device[0]) == 0:
            pass
        else:
            print("Problem stopping measurement.")

    def get_error_msg(self, error_code):
        '''
        Flags are basically error codes for Picoharp, there is no
        description of all the flag values in the manual but
        we know few of the flags that are definitely bad. ?????????
        '''
        self.ph.PH_GetErrorString(byref(errorString), error_code)
        return erroString.value

    def get_flag(self):
        '''
        Flags are basically error codes for Picoharp, there is no
        description of all the flag values in the manual but
        we know few of the flags that are definitely bad. ?????????
        '''
        if self.ph.PH_GetFlags(self.device[0],byref(self.flags))==0:
            return self.flags.value;

    def close(self):
        '''
        Close Picoharp
        '''
        if self.ph.PH_CloseDevice(self.device[0])==0:
            print('PicoHarp300:\nPicoharp is DISCONNECTED.\n')

    def get_counts(self,channel_0=True,channel_1=True):
        '''
        Get countrates in channels.
        '''
        self.ph.PH_GetCountRate(self.device[0],0,byref(self.countRate0))
        self.ph.PH_GetCountRate(self.device[0],1,byref(self.countRate1))
        if channel_0==True:
            if channel_1==True:
                # print('Channel 0: %d counts/s \nChannel 1: %d counts/s\n' % (self.countRate0.value,self.countRate1.value))
                return self.countRate0.value,self.countRate1.value
            else:
                # print('Channel 0: %d counts/s' % (self.countRate0.value))
                return self.countRate0.value
        else:
            if channel_1==True:
                # print('Channel 1: %d counts/s' % (self.countRate1.value))
                return self.countRate1.value
            else:
                pass

    def buffer_read(self):
        # read flags
        self.ph.PH_GetFlags(self.device[0], byref(self.flags))
        if self.flags.value == 48:
            # print("Flag 48")
            return None
        self.ph.PH_ReadFiFo(self.device[0],
                        byref(self.buffer),
                        self.TTREADMAX,
                        byref(self.nactual))
        if self.nactual.value > 0:
            return (ctypes.c_uint*self.nactual.value)(*self.buffer[0:self.nactual.value])
        else:
            return None

    def read_buffer(self,output_file):
        '''
        read the data/events recorded and stored in the buffer and write the results to an output file.
        '''
        with open(output_file,'wb+') as outputfile:
            sentinel = 0
            while True:
                self.ph.PH_GetFlags(self.device[0], byref(self.flags))
                if self.flags.value == 48:
                    print("flag 48")
                    break
                if sentinel >= 2:
                    print("flag 60 break")
                    break
                if self.flags.value == 60:
                    sentinel = sentinel + 1
                read_val = self.ph.PH_ReadFiFo(self.device[0],
                                byref(self.buffer),
                                self.TTREADMAX,
                                byref(self.nactual))
                print(self.flags.value, self.nactual.value, read_val)
                sleep(0.5)
                if self.nactual.value > 0:
                    print("writing")
                    outputfile.write((ctypes.c_uint*self.nactual.value)(*self.buffer[0:self.nactual.value]))

    # def read_buffer(self,output_file,number_of_markers_expected):
    #     '''
    #     read the data/events recorded and stored in the buffer and write the results to an output file.
    #     '''
    #     with open(output_file,'wb+') as outputfile:
    #         read_values=0
    #         while read_values < number_of_markers_expected:
    #             self.ph.PH_GetFlags(self.device[0], byref(self.flags))
    #
    #             if self.flags.value == 48:# or flags.value == 8:
    #                 print("flag 48")
    #                 break
    #
    #             self.ph.PH_ReadFiFo(self.device[0],
    #                             byref(self.buffer),
    #                             self.TTREADMAX,
    #                             byref(self.nactual))
    #
    #             read_values=self.nactual.value
    #             print(read_values)
    #
    #             if self.nactual.value > 0:
    #                 print("writing")
    #                 outputfile.write((ctypes.c_uint*self.nactual.value)(*self.buffer[0:self.nactual.value]))

# Functions that are useful in analyzing and parsing files collected when picoharp in running in TTTR mode.
class TTTR_Functions():

    def __init__(self):
        pass

    # parse the T2 mode files read from the buffer and return the time differences between consective channels only if channel 0 get a count and channel 1 get a count right after in nanoseconds.
    def T2_parsing(self,inputfile):
        '''
        Input : T2 file.
        Output: Time differences (in ns) between consecutive channels only if chanel 0 gets a count and channel 1 gets another count right after.
        '''
        inputfile = open(inputfile,'rb')
        T2WRAPAROUND = 210698240
        oflcorrection=0
        truetime=0
        data=[]
        while True:
            try:
                recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
            except:
                print('\nData parsing complete.')
                break
            channel = int(recordData[0:4], base=2)
            time = int(recordData[4:32], base=2)
            if channel == 0xF:
                markers = int(recordData[28:32], base=2)
                if markers == 0:
                    oflcorrection += T2WRAPAROUND
                else:
                    truetime = oflcorrection + time
            else:
                truetime = oflcorrection + time
                data.append([channel,truetime])
        T2_data=[]
        for i in range(len(data)-1):
            #original time tags have units of 4 picoseconds(default bin width specified in manual).
            if data[i]==0:
                if data[i+1]==1:
                    T2_data.append((data[i+1][1]-data[i][1])*(4e-3))
        return T2_data


    def T3_parsing(self, inputfile):
        '''
        Input:  T3 mode file read from the buffer
        Output: Photon counts between consecutive marker events.
        '''
        # PicoHarp T3 Format (for analysis and interpretation):
        # The bit allocation in the record for the 32bit event is, starting
        # from the MSB:
        #       channel:     4 bit
        #       dtime:      12 bit
        #       nsync:      16 bit
        # The channel code 15 (all bits ones) marks a special record.
        # Special records can be overflows or external markers. To
        # differentiate this, dtime must be checked:
        #
        #     If it is zero, the record marks an overflow.
        #     If it is >=1 the individual bits are external markers.
        T3WRAPAROUND = 65536
        oflcorrection=0
        truensync=0
        T3_data=[]
        dlen=0
        data=[]
        counter = 0
        with open(inputfile,'rb+') as inputfile:
            while True:
                try:
                    recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
                except:
                    print("wups")
                    break
                channel = int(recordData[0:4], base=2)
                dtime = int(recordData[4:16], base=2)
                nsync = int(recordData[16:32], base=2)
                if channel == 0xF:
                    if dtime == 0:
                        oflcorrection += T3WRAPAROUND
                    else:
                        truensync = oflcorrection + nsync
                else:
                    truensync = oflcorrection + nsync
                    dlen += 1
                print(counter,channel, dtime, nsync, truensync)
                counter = counter+1
                data.append([counter,channel, dtime, nsync, truensync])
                # if channel == 15:
                    # print(counter,channel, dtime, nsync, truensync)
                    # data.append(truensync)
                    # data.append([counter,channel, dtime, nsync, truensync])
            # for i in range(len(data)-1):
            #     T3_data.append(data[i+1]-data[i])
        inputfile.close()
        return data

# Functions to run error-proof confocal scans by automating both the picoharp and the stage.
class Confocal_Functions():

    TTTR_functions = TTTR_Functions()

    def __init__(self, trigger_step, r_start, r_end,
                 sample_region, velocity, runway_length,
                 laser_power):
        '''
        Initialize scanning parameters to be used in the confocal scan functions below.
        '''
        self.trigger_step = trigger_step
        self.r_start = r_start
        self.r_end = r_end
        self.x_start = r_start[0]
        self.y_start = r_start[1]
        self.x_end = r_end[0]
        self.y_end = r_end[1]
        self.scan_size = [1000*(self.x_end-self.x_start),1000*(self.y_end-self.y_start)]
        self.sample_region = sample_region
        self.velocity = velocity
        self.runway_length = runway_length
        self.laser_power = laser_power
        self.dwell_time = self.trigger_step/self.velocity

    # def write_metadata(self):
    #     '''
    #     Create data storing directories and write a metadata file that contains
    #     all scanning parameters used during a scan.
    #     Deprecated in favour of David's preferred data logging routines.
    #     '''
    #     region_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s" % self.sample_region
    #     if not os.path.exists(region_folder):
    #         os.makedirs(region_folder)
    #
    #     T3_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\T3_data" % self.sample_region
    #     if not os.path.exists(T3_folder):
    #         os.makedirs(T3_folder)
    #
    #     ConfocalPlots_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\ConfocalPlots" % self.sample_region
    #     if not os.path.exists(ConfocalPlots_folder):
    #         os.makedirs(ConfocalPlots_folder)
    #
    #     T2_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\T2_data" % self.sample_region
    #     if not os.path.exists(T2_folder):
    #         os.makedirs(T2_folder)
    #
    #     metadata=open("C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\ConfocalPlots\\%s_metadata(%dx%d).txt" % (self.sample_region,self.sample_region,self.scan_size[0],self.scan_size[1]),"w+")
    #     metadata.write('Sample region: %s \n' % self.sample_region)
    #     metadata.write('Sample location = [%.4f, %.4f] \n\n' % (self.x_start,self.x_end))
    #
    #     metadata.write('Laser power = %d uW \n' % self.laser_power)
    #     metadata.write('Scanning speed = %.2f um/s \n' % (self.velocity*1000))
    #     metadata.write('Step size = %.2f um \n' % (self.trigger_step*1000))
    #     metadata.write('Runway length = %.2f um \n\n' % (self.runway_length*1000))
    #
    #     dwell_time=1000*self.trigger_step/self.velocity
    #     metadata.write('Dwell time = %.3f ms \n' % dwell_time)
    #     typical_max_counts=40000
    #     from math import sqrt
    #     SNR=(typical_max_counts*dwell_time/1000)/sqrt(typical_max_counts*dwell_time/1000)
    #     metadata.write('SNR (at 40 kcp/s) = %d ' % SNR)
    #     metadata.close()

    def confocal_line_scan(self,number_of_markers_expected,output_file,direction='right'):
        '''
        Set up stage trigger signals to be received by picoharp as markers,
        move the stage in one direction, then read and parse T3 files from
        the Picoharp buffer for later data processing.
        '''
        if direction=='right':
            stage.TRO_OFF()
            time.sleep(0.01)
            stage.move_x(self.x_start-self.runway_length)
            time.sleep(0.01)
            stage.setCTO(**{'StartThreshold':self.x_start,'StopThreshold':self.x_end,'velocity':self.velocity,'TriggerStep':self.trigger_step})
            time.sleep(0.01)
            picoharp.start_measurement(100)
            time.sleep(0.01)
            stage.move_x(self.x_end+self.runway_length)
            time.sleep(0.01)
            picoharp.read_buffer(output_file,number_of_markers_expected)
            T3_data=self.TTTR_functions.T3_parsing(output_file)
            return T3_data
        elif direction=='left':
            stage.TRO_OFF()
            time.sleep(0.01)
            stage.move_x(self.x_end+self.runway_length)
            time.sleep(0.01)
            stage.setCTO(**{'StartThreshold':self.x_end,'StopThreshold':self.x_start,'velocity':self.velocity,'TriggerStep':self.trigger_step})
            time.sleep(0.01)
            picoharp.start_measurement(100)
            time.sleep(0.01)
            stage.move_x(self.x_start-self.runway_length)
            time.sleep(0.01)
            picoharp.read_buffer(output_file,number_of_markers_expected)
            reversed_T3_data=self.TTTR_functions.T3_parsing(output_file)
            return reversed_T3_data
        else:
            raise ValueError('No such direction is allowed.')

    def confocal_scan(self):
        '''
        Record metadata, confocal scan a sample in the zig-zag fashion,
        save raw data to a txt file, rescan a row if it doesn't produce number
        of markers we expect and plot the confocal data everytime 10% has been completed.
        '''
        time_start = time.time()
        number_of_rows = (self.y_end-self.y_start)/self.trigger_step
        number_of_markers_expected = int(round((self.x_end-self.x_start)/self.trigger_step))
        confocal_data = []
        ten_percent_of_number_of_rows=int(number_of_rows)/10
        bad_row = [0]*(number_of_markers_expected-1)
        bad_row_counter = 0
        stage.move_x(self.x_start)
        time.sleep(0.01)
        stage.move_y(self.y_start)

        for i in range(int(number_of_rows)):
            output_file="C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\T3_data\\line_scan-%d.out" % (self.sample_region,i)
            picoharp.stop_measurement()
            time.sleep(0.01)
            stage.TRO_OFF()
            time.sleep(0.01)
            stage.move_y(self.y_start+i*self.trigger_step)

            if i%2==0:
                T3_data=[]
                while not (len(T3_data)==number_of_markers_expected or len(T3_data)==(number_of_markers_expected-1)):
                    T3_data=self.confocal_line_scan(number_of_markers_expected,output_file,direction='right')
                    #print(len(T3_data))
                    if not (len(T3_data)==number_of_markers_expected or len(T3_data)==(number_of_markers_expected-1)):
                        bad_row_counter+=1
                        print('Bad rows: %d.' % bad_row_counter)
                    else:
                        pass
                T3_data=T3_data[0:(number_of_markers_expected-1)]
                confocal_data.append(T3_data)
            else:
                T3_data=[]
                while not (len(T3_data)==number_of_markers_expected or len(T3_data)==(number_of_markers_expected-1)):
                    T3_data=self.confocal_line_scan(number_of_markers_expected,output_file,direction='left')
                    #print(len(T3_data))
                    if not (len(T3_data)==number_of_markers_expected or len(T3_data)==(number_of_markers_expected-1)):
                        bad_row_counter+=1
                        print('Bad rows: %d.' % bad_row_counter)
                    else:
                        pass
                reversed_T3_data=T3_data[0:(number_of_markers_expected-1)]
                T3_data2=[]
                for j in range(len(reversed_T3_data)):
                    T3_data2.append(reversed_T3_data[len(reversed_T3_data)-j-1])
                confocal_data.append(T3_data2)

            if i%ten_percent_of_number_of_rows==0 and not i==0:
                percentage=(100*i)/float(number_of_rows)
                print('%.2f percent completed.' % percentage)
                plt.figure()
                plt.imshow(confocal_data,cmap='viridis')
                plt.colorbar(label='cps')
                plt.show()

        time_end=time.time()
        print('The scan took %.2f seconds.\n' % (time_end-time_start))
        print('There was %.2f percent of bad rows.' % (100*bad_row_counter/number_of_rows))
        scan_size=[1000*(self.x_end-self.x_start),1000*(self.y_end-self.y_start)]
        # I dunno what Yang was doing with these lines below (David, Sep 2020)
        # confocal_raw_data_file=open("C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\ConfocalPlots\\%s(%dx%d)_RawData.txt" % (self.sample_region,self.sample_region,scan_size[0],scan_size[1]),'w+')
        # for j in range(len(confocal_data)):
        #     for i in range(len(confocal_data[j])):
        #         confocal_raw_data_file.write('%d ' % confocal_data[j][i])
        #     confocal_raw_data_file.write('\n')
        # confocal_raw_data_file.close()
        return confocal_data

    def confocal_plot(self,confocal_data,type='viridis',save_image=True,image_title=True):
        '''
        Produce high quality confocal plots and save them in data directories or make titles if desired.
        '''
        import matplotlib
        matplotlib.rc('xtick', labelsize=10)
        matplotlib.rc('ytick', labelsize=10)
        from matplotlib.ticker import MaxNLocator
        fig=plt.figure(figsize=(8,3)).gca()
        fig.xaxis.set_major_locator(MaxNLocator(integer=True))
        fig.yaxis.set_major_locator(MaxNLocator(integer=True))
        conversion_factor=1/self.dwell_time
        confocal_plot=confocal_data[:]
        for j in range(len(confocal_plot)):
            confocal_plot[j]=[i*conversion_factor/1000 for i in confocal_plot[j]]
        scan_size=[1000*(self.x_end-self.x_start),1000*(self.y_end-self.y_start)]
        plt.imshow(confocal_plot,cmap=type,extent=[0,scan_size[0],scan_size[1],0])
        #plt.suptitle('Confocal Scan of h-BN', fontsize=40, fontweight='bold')
        plt.xlabel('x (${\mu}$m)',fontsize=10)
        plt.ylabel('y (${\mu}$m)',fontsize=10)
        if image_title==True:
            plt.title('Region:%s, Resolution:%dnm \n LaserPower:%d${\mu}W$, ScanSpeed:%d${\mu}$m/s, Origin:[%.4f,%.4f] \n' % (self.sample_region,int(self.trigger_step*1000000),self.laser_power,self.velocity*1000,self.x_start,self.y_start),fontsize=6)
        plt.colorbar(label='kcps')
        fig.invert_yaxis()
        plt.tight_layout()
        ConfocalPlots_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\ConfocalPlots" % self.sample_region
        save_location_png=ConfocalPlots_folder+'\\%s(%dx%d).png' % (self.sample_region,scan_size[0],scan_size[1])
        save_location_png_clean=ConfocalPlots_folder+'\\%s(%dx%d)-clean.png' % (self.sample_region,scan_size[0],scan_size[1])
        save_location_pdf_clean=ConfocalPlots_folder+'\\%s(%dx%d)-clean.pdf' % (self.sample_region,scan_size[0],scan_size[1])
        if save_image==True:
            if image_title==False:
                plt.savefig(save_location_png_clean,dpi=400)
                plt.savefig(save_location_pdf_clean)
            else:
                plt.savefig(save_location_png,dpi=400)
        plt.show()

    def read_confocal_raw_data(self,inputfile):
        '''
        Reads the raw data wrote to the txt file during the scan and returns
        a confocal map variable that is plt.show()-ready.
        '''
        def read_confocal_raw_data(inputfile):
            raw_data=[]
            raw_data_line=[]
            with open(inputfile,'r') as inputfile:
                for line in inputfile:
                    for number in line:
                        if number=='\n':
                            break
                        else:
                            raw_data_line.append(int(number))
                    raw_data.append(raw_data_line)
                    raw_data_line=[]
            inputfile.close()
            return raw_data

    def find_emitters(self,confocal_data,number_of_emitters=1):
        '''
        an algorithm that finds a number of brightest pixels in a heat map
        (biggest value elements in a n-dimensional array) and turn that relative
        location on the map and the absolute position on the stage.
        '''
        np_confocal_data=np.array(confocal_data)
        number_of_rows=np_confocal_data.shape[0]
        number_of_columns=np_confocal_data.shape[1]
        flattened=np_confocal_data.flatten()
        sorted=flattened.argsort()[-number_of_emitters:]
        row_index=[]
        column_index=[]
        emitter_locations=[]
        for i in range(1,number_of_emitters+1):
            remainder=sorted[-i]%number_of_columns
            row_index.append((sorted[-i]-remainder)/number_of_columns)
            column_index.append(remainder)
            emitter_locations.append([column_index[i-1]*self.trigger_step+self.x_start,row_index[i-1]*self.trigger_step+self.y_start])
            print("\n No.%d brightest spot on image: [%.1f,%.1f]" % (i,column_index[i-1]*self.trigger_step*1000,row_index[i-1]*self.trigger_step*1000))
            print("\n No.%d brightest spot on stage: [%.4f,%.4f]" % (i,column_index[i-1]*self.trigger_step+self.x_start,row_index[i-1]*self.trigger_step+self.y_start))
        return emitter_locations

    def emitter_confocal_scan(self):
        '''
        Basically combines the confocal scan function, make two confocal plots
        (one for reference and one for publication) and find the brightest spot
        in the confocal plot.
        '''
        confocal_data=self.confocal_scan()
        self.confocal_plot(confocal_data,save_image=True,image_title=True)
        self.confocal_plot(confocal_data,save_image=True,image_title=False)
        emitter_locations=self.find_emitters(confocal_data,number_of_emitters=1)
        return emitter_locations

    def iterative_emitter_confocal_scan(self,iterations=3):
        '''
        First iteration scan the whole flake, second iteration scans 10um x 10um about the emitter, third iteration scans 5um x 5um about the emitter.
        '''
        emitter_locations_iteration1=self.emitter_confocal_scan()
        if iterations>3 or iterations==0:
            raise ValueError('Maximum of three iterations is allowed.')
        elif iterations==1:
            pass
        else:
            self.x_start=emitter_locations_iteration1[0][0]-0.005
            self.y_start=emitter_locations_iteration1[0][1]-0.005
            self.x_end=emitter_locations_iteration1[0][0]+0.005
            self.y_end=emitter_locations_iteration1[0][1]+0.005
            emitter_locations_iteration2=self.emitter_confocal_scan()
            if iterations==3:
                self.x_start=emitter_locations_iteration2[0][0]-0.003
                self.y_start=emitter_locations_iteration2[0][1]-0.003
                self.x_end=emitter_locations_iteration2[0][0]+0.003
                self.y_end=emitter_locations_iteration2[0][1]+0.003
                emitter_locations_iteration3=self.emitter_confocal_scan()
            else:
                pass
        if iterations>0:
            print('\nEmitter location(1st iteration):\n %s' % emitter_locations_iteration1[0])
            if iterations==1:
                return emitter_locations_iteration1[0]
            else:
                print('Emitter location(2nd iteration):\n %s' % emitter_locations_iteration2[0])
                if iterations==2:
                    return emitter_locations_iteration2[0]
                else:
                    print('Emitter location(3rd iteration):\n %s' % emitter_locations_iteration3[0])
                    return emitter_locations_iteration3[0]

    def walk_in_the_park(self,emitter_position,quality_factor=2,emitter_brightest=10000):
        '''
        Quality_factor of the emitter is defined as the factor in which it is brighter than a surrounding pixel.
        '''
        walk_x_start=emitter_position[0]-0.002
        walk_x_end=emitter_position[0]+0.002
        walk_y_start=emitter_position[1]-0.002
        walk_y_end=emitter_position[1]+0.002
        stage.move_x(walk_x_start)
        time.sleep(0.01)
        stage.move_y(walk_y_start)
        time.sleep(0.01)
        base_rate=picoharp.get_counts(channel_0=True,channel_1=False)+1
        number_of_markers=int((walk_x_end-walk_x_start)/self.trigger_step)
        number_of_rows=int((walk_y_end-walk_y_start)/self.trigger_step)
        for row_index in range(number_of_rows):
            stage.move_y(walk_y_start+row_index*self.trigger_step)
            for marker_index in range(number_of_markers):
                stage.move_x(walk_x_start+marker_index*self.trigger_step)
                new_rate=picoharp.get_counts(channel_0=True,channel_1=False)+1
                #we consider we found an emitter if it is much brighter than the next pixel and the count itself is high.
                if new_rate/base_rate>quality_factor and new_rate>emitter_brightest:
                    return new_rate
                else:
                    base_rate=new_rate

    def g2_scan(self,acq_time,counts=4,range=[0,100],bins=100):
        '''
        Acquire T2 data and make the g2 plot given plot paramters like range and number of bins.
        '''
        output_file="C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\T2_data\\AutoCorrelation-%d.out" % (self.sample_region)
        picoharp.start_measurement(acq_time)
        picoharp.read_buffer(output_file,number_of_markers_expected=self.TTREADMAX)
        T2_data=self.TTTR_functions.T2_parsing(output_file)
        plt.hist(T2_data,range=[0,100],bins=100)
        plt.title("AcquisitionTime=%s Counts=%d kcps" % (acq_time,counts))
        plt.xlabel("time(ns)")
        plt.ylabel("Counts")
        return T2_data
