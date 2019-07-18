import struct,time,os,sys
import numpy as np
import matplotlib.pyplot as plt
from Instruments import PicoHarp300,M687,VerdiV5,ProEM,SCT320

#instantiate all instrument objects so that their functions could be called within the following function classes.
picoharp=PicoHarp300()
stage=M687()
camera=ProEM()
spectrograph=SCT320()
laser=VerdiV5()

# Functions to open and close the instruments.
class Instrument_Functions():

    opened_instruments=[]

    def __init__(self):
        pass

    # open or close all instruments listed in the list of instruments if connection was established.
    def open_instruments(self,instruments=[picoharp,stage,camera,spectrograph,laser]):
        for i in instruments:
            try:
                i.open()
                self.opened_instruments.append(i)
            except:
                pass
    # close all instruments opened previously using the open_instruments function.
    def close_instruments(self):
        for i in self.opened_instruments:
            i.close()


# Functions that create directories and write notes that help researchers to organize their experiment data files and notes.
class Experiment_Logger():

    def __init__(self):
        self.experiment_date=''
        self.researcher_name=''
        self.project_name=''
        self.experiment_name=''
        self.experiment_date_root_dir=''

    def start_logging(self):
        self.experiment_date="%s_%s_%s" % (time.localtime()[0],time.localtime()[1],time.localtime()[2])
        self.researcher_name=raw_input("Name of researcher:")
        self.create_research_root_dir(self.researcher_name)
        self.project_name=raw_input("Name of project:")
        self.create_project_root_dir(self.researcher_name,self.project_name)
        self.experiment_name=raw_input("Name of the experiment:")
        self.create_experiment_root_dir(self.researcher_name,self.project_name,self.experiment_name)
        self.experiment_date_root_dir=self.create_experiment_date_root_dir(self.researcher_name,self.project_name,self.experiment_name,self.experiment_date)

    def end_logging(self):
        log_file=open(self.experiment_date_root_dir+"\\experiment_log(%s).txt" % self.experiment_date,"w+")
        observations_list=["Observations:\n"]
        i=0
        while not (observations_list[i] == "end" or observations_list[i] == "done"):
            i += 1
            new_observation=raw_input("Observation:")
            observations_list.append(new_observation)
        for observations in observations_list:
            log_file.write("%s \n" % observations)
        log_file.close()

    def create_research_root_dir(self,researcher_name):
        researcher_root_dir = r"D:\\Google Drive\\Zia Lab\\%s" % researcher_name
        if not os.path.exists(researcher_root_dir):
            os.makedirs(researcher_root_dir)

    def create_project_root_dir(self,researcher_name,project_name):
        project_root_dir = r"D:\\Google Drive\\Zia Lab\\%s\\%s" % (researcher_name,project_name)
        if not os.path.exists(project_root_dir):
            os.makedirs(project_root_dir)

    def create_experiment_root_dir(self,researcher_name,project_name,experiment_name):
        experiment_root_dir = r"D:\\Google Drive\\Zia Lab\\%s\\%s\\%s" % (researcher_name,project_name,experiment_name)
        if not os.path.exists(experiment_root_dir):
            os.makedirs(experiment_root_dir)

    def create_experiment_date_root_dir(self,researcher_name,project_name,experiment_name,experiment_date):
        experiment_date_root_dir = r"D:\\Google Drive\\Zia Lab\\%s\\%s\\%s\\%s" % (researcher_name,project_name,experiment_name,experiment_date)
        if not os.path.exists(experiment_date_root_dir):
            os.makedirs(experiment_date_root_dir)
        return experiment_date_root_dir


# Functions that are useful in analyzing and parsing files collected when picoharp in running in TTTR mode.
class TTTR_Functions():

    def __init__(self):
        pass

    # parse the T2 mode files read from the buffer and return the time differences between consective channels only if channel 0 get a count and channel 1 get a count right after in nanoseconds.
    def T2_parsing(self,inputfile):
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

    # parse the T3 mode files read from the buffer and return photon counts between consective marker events.
    def T3_parsing(self,inputfile):
        T3WRAPAROUND = 65536
        oflcorrection=0
        truensync=0
        T3_data=[]
        dlen=0
        data=[]
        with open(inputfile,'rb+') as inputfile:
            while True:
                try:
                    recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
                except:
                    break
                channel = int(recordData[0:4], base=2)
                dtime = int(recordData[4:16], base=2)
                nsync = int(recordData[16:32], base=2)
                if channel == 0xF:
                    if dtime == 0:
                        oflcorrection += T3WRAPAROUND
                    else:
                        marker=int(recordData[0:4],base=2)
                        truensync = oflcorrection + nsync
                else:
                    truensync = oflcorrection + nsync
                    dlen += 1
                data.append(truensync)
            for i in range(len(data)-1):
                T3_data.append(data[i+1]-data[i])
        inputfile.close()
        return T3_data


# Functions to run error-proof confocal scans by automating both the picoharp and the stage.
class Confocal_Functions():

    TTTR_functions=TTTR_Functions()

    # initialize scanning parameters to be used in the confocal scan functions below.
    def __init__(self,trigger_step,r_start,r_end,sample_region,velocity,runway_length,laser_power):
        #self.master_folder=master_folder
        self.trigger_step=trigger_step
        self.r_start=r_start
        self.r_end=r_end
        self.x_start=r_start[0]
        self.y_start=r_start[1]
        self.x_end=r_end[0]
        self.y_end=r_end[1]
        self.scan_size=[1000*(self.x_end-self.x_start),1000*(self.y_end-self.y_start)]
        self.sample_region=sample_region
        self.velocity=velocity
        self.runway_length=runway_length
        self.laser_power=laser_power
        self.dwell_time=self.trigger_step/self.velocity

    # create data stroing directories and write a metadata file that contains all scanning parameters used during a scan.
    def write_metadata(self):
        region_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s" % self.sample_region
        if not os.path.exists(region_folder):
            os.makedirs(region_folder)

        T3_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\T3_data" % self.sample_region
        if not os.path.exists(T3_folder):
            os.makedirs(T3_folder)

        ConfocalPlots_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\ConfocalPlots" % self.sample_region
        if not os.path.exists(ConfocalPlots_folder):
            os.makedirs(ConfocalPlots_folder)

        T2_folder = r"C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\T2_data" % self.sample_region
        if not os.path.exists(T2_folder):
            os.makedirs(T2_folder)

        metadata=open("C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\ConfocalPlots\\%s_metadata(%dx%d).txt" % (self.sample_region,self.sample_region,self.scan_size[0],self.scan_size[1]),"w+")
        metadata.write('Sample region: %s \n' % self.sample_region)
        metadata.write('Sample location = [%.4f, %.4f] \n\n' % (self.x_start,self.x_end))

        metadata.write('Laser power = %d uW \n' % self.laser_power)
        metadata.write('Scanning speed = %.2f um/s \n' % (self.velocity*1000))
        metadata.write('Step size = %.2f um \n' % (self.trigger_step*1000))
        metadata.write('Runway length = %.2f um \n\n' % (self.runway_length*1000))

        dwell_time=1000*self.trigger_step/self.velocity
        metadata.write('Dwell time = %.3f ms \n' % dwell_time)
        typical_max_counts=40000
        from math import sqrt
        SNR=(typical_max_counts*dwell_time/1000)/sqrt(typical_max_counts*dwell_time/1000)
        metadata.write('SNR (at 40 kcp/s) = %d ' % SNR)
        metadata.close()

    # set up stage trigger signals to be received by picoharp as markers, move the stage in one direction, then read and parse T3 files from picoharp buffer for later data processing.
    def confocal_line_scan(self,number_of_markers_expected,output_file,direction='right'):
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

    # record metadata, confocal scan a sample in the zig-zag fashion, save raw data to a txt file, rescan a row if it doesn't produce number of markers we expect and plot the confocal data everytime 10% has been completed.
    def confocal_scan(self):
        #laser.open()
        self.write_metadata()
        print('Metadata has been exported.')
        time_start=time.time()
        number_of_rows=(self.y_end-self.y_start)/self.trigger_step
        number_of_markers_expected=int(round((self.x_end-self.x_start)/self.trigger_step))
        confocal_data=[]
        ten_percent_of_number_of_rows=int(number_of_rows)/10
        bad_row=[0]*(number_of_markers_expected-1)
        bad_row_counter=0
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
        #laser.close()
        scan_size=[1000*(self.x_end-self.x_start),1000*(self.y_end-self.y_start)]
        confocal_raw_data_file=open("C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\ConfocalPlots\\%s(%dx%d)_RawData.txt" % (self.sample_region,self.sample_region,scan_size[0],scan_size[1]),'w+')
        for j in range(len(confocal_data)):
            for i in range(len(confocal_data[j])):
                confocal_raw_data_file.write('%d ' % confocal_data[j][i])
            confocal_raw_data_file.write('\n')
        confocal_raw_data_file.close()
        return confocal_data

    # produce high quality confocal plots and save them in data directories or make titles if desired.
    def confocal_plot(self,confocal_data,type='viridis',save_image=True,image_title=True):
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

    # reads the raw data wrote to the txt file during the scan and return a confoal map variable that is plt.show()-ready.
    def read_confocal_raw_data(self,inputfile):
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

    # an algorithm that finds a number of brightest pixels in a heat map(biggest value elements in a n-dimensional array) and turn that relative location on the map and the absolute position on the stage.
    def find_emitters(self,confocal_data,number_of_emitters=1):
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

    # basically combines the confocal scan function, make two confocal plots(one for reference and one for publication) and find the brightest spot in the confocal plot.
    def emitter_confocal_scan(self):
        confocal_data=self.confocal_scan()
        self.confocal_plot(confocal_data,save_image=True,image_title=True)
        self.confocal_plot(confocal_data,save_image=True,image_title=False)
        emitter_locations=self.find_emitters(confocal_data,number_of_emitters=1)
        return emitter_locations

    # first iteration scan the whole flake, second iteration scans 10um x 10um about the emitter, third iteration scans 5um x 5um about the emitter.
    def iterative_emitter_confocal_scan(self,iterations=3):
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

    # quality_factor of the emitter is defined as the factor in which it is brighter than a surrounding pixel.
    def walk_in_the_park(self,emitter_position,quality_factor=2,emitter_brightest=10000):
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

    # acquire T2 data and make the g2 plot given plot paramters like range and number of bins.
    def g2_scan(self,acq_time,counts=4,range=[0,100],bins=100):
        output_file="C:\\Users\\lab_pc_i\\Desktop\\Yang\\hBN\\Lee's Sample\\%s\\T2_data\\AutoCorrelation-%d.out" % (self.sample_region)
        picoharp.start_measurement(acq_time)
        picoharp.read_buffer(output_file,number_of_markers_expected=self.TTREADMAX)
        T2_data=self.TTTR_functions.T2_parsing(output_file)
        plt.hist(T2_data,range=[0,100],bins=100)
        plt.title("AcquisitionTime=%s Counts=%d kcps" % (acq_time,counts))
        plt.xlabel("time(ns)")
        plt.ylabel("Counts")
        return T2_data
