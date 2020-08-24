# Imports
import clr, ctypes, sys, os, glob, time, pickle
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import numpy as np
import untangle
from io import StringIO
from scipy.optimize import curve_fit
from scipy.signal import medfilt
from matplotlib.colors import LogNorm
from ..misc.sugar import wav2RGB
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

zlab_dir = 'D:/Google Drive/Zia Lab/'

platform = sys.platform
if platform == 'win32':
    try:
        from System import *
        from System.Threading import AutoResetEvent
        from System.Collections.Generic import List
        from System.Runtime.InteropServices import Marshal
        from System.Runtime.InteropServices import GCHandle, GCHandleType

        # Add needed dll references
        sys.path.append(os.environ['LIGHTFIELD_ROOT'])
        sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
        clr.AddReference('PrincetonInstruments.LightFieldViewV5')
        clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
        clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')
        # Not sure if these are necessary
        clr.AddReference('System.Collections')
        clr.AddReference('System.Runtime')
        clr.AddReference('System.Runtime.InteropServices')
        clr.AddReference('PrincetonInstruments.LightField.Automation')
        clr.AddReference('System.Threading')

        # PI imports
        from PrincetonInstruments.LightField.Automation import *
        from PrincetonInstruments.LightField.AddIns import *
    except:
        print("LF not here")

# constants
trigger_responses = {
    'Readout Per Trigger': 2,
    'No Response': 1,
    'Start On Single Trigger': 5,
    'Shift Per Trigger': 3,
    'Expose During Trigger Pulse': 4}
allowed_storage_shift_rates = [0.6, 0.45, 2., 5] # in micro_seconds
codebase_dir = os.path.join(zlab_dir,'Codebase')
log_dir = os.path.join(zlab_dir,'Log')
data_dir = os.path.join(log_dir,'Data')
graphs_dir = os.path.join(log_dir,'Graphs')
platform = sys.platform

pixel_sizes = {'proEM': 16}

resolutions = {
    'proEM': {
        '150g':[[10,20,25,50,100,150,200,300],
               [0.553,0.553,0.553,0.9875,1.975,2.9625,3.95,5.925]],
        '300g':[[10,20,25,50,100,150,200,300],
               [0.2734,0.2734,0.2734,0.4883,0.9765,1.4648,1.953,2.9295]],
        '50g':[[10,20,25,50,100,150,200,300],
               [1.6691,1.6691,1.6691,2.9805,5.961,8.9415,11.922,17.8831]],
    }
}
def slit_to_resolution(grating, slit_width):
    return np.interp(slit_width,resolutions['proEM'][grating][0],resolutions['proEM'][grating][1])

def get_latest_spe_fname(directory):
    '''
    Returns the filename of the most recent spe file in the given directory.
    '''
    if(os.path.exists(directory)):
        files = glob.glob(directory +'/*.spe')
        last_spe = max(files, key=os.path.getctime)
    else:
        print("no such dir...")
    last_spe = os.path.split(last_spe)
    return {'dir': last_spe[0], 'fname': last_spe[1]}

class LField():
    lf_settings = pickle.load(open(os.path.join(codebase_dir,'zialab',
              'softwarecontrol','LF_settings.pkl'),'rb'))
    def __init__(self):
        self.automat = Automation(True, List[String]())
        self.application = self.automat.LightFieldApplication
        self.experiment = self.application.Experiment
        self.lf_dir = self.experiment.GetValue(ExperimentSettings.FileNameGenerationDirectory)
    def find_setting(self,search):
        '''
        Search for a setting in the Lightfield API.
        '''
        search = search.lower()
        return {'cam_settings' : [s for s in self.lf_settings['camera_settings']
                                  if search in s.lower()],
        'exp_settings': [s for s in self.lf_settings['experiment_settings']
                         if search in s.lower()],
        'spec_settings': [s for s in self.lf_settings['spectrometer_settings']
                          if search in s.lower()]}
    def get_frame_rate(self,storage_shift_rate, window_height, exposure_time):
        assert type(window_height) == int, "window height must be int"
        assert window_height < 40, "Nutty window height."
        assert exposure_time > 0, "Nutty exposure time"
        assert self.experiment.GetValue(CameraSettings.ReadoutControlMode) == 4, "Mode not right"
        assert storage_shift_rate in allowed_storage_shift_rates, "not allowed storage shift rate"
        self.experiment.SetValue(CameraSettings.ReadoutControlKineticsWindowHeight,
                        window_height)
        self.experiment.SetValue(CameraSettings.ReadoutControlStorageShiftRate,
                       storage_shift_rate)
        self.set_exposure(exposure_time)
        return self.experiment.GetValue(CameraSettings.AcquisitionFrameRate)

    def set_readout_mode(self,mode):
        self.mode = mode
        if mode == 'Full Frame':
            mode = 1
        elif mode == 'Frame Transfer':
            mode = 2
        elif mode == 'Kinetics':
            mode = 3
        elif mode == 'Spectra Kinetics':
            mode = 4
        self.experiment.SetValue(CameraSettings.ReadoutControlMode, mode)
    def set_EM_gain(self,em_gain):
        assert em_gain <= 1000, "ERROR: EM gain too high"
        assert type(em_gain) == int, "ERROR: EM gain must be an integer number"
        if(self.experiment.GetValue(CameraSettings.AdcQuality) != 3):
            print("Camera not in EM_gain mode")
            print("Setting ADC quality mode to EM...")
            self.experiment.SetValue(CameraSettings.AdcQuality,3)
        self.experiment.SetValue(CameraSettings.AdcEMGain, em_gain)
        self.em_gain = em_gain
    def set_exposure(self,exposure_in_ms):
        self.exposure_in_ms = float(np.round(exposure_in_ms,4))
        self.experiment.SetValue(CameraSettings.ShutterTimingExposureTime,
                            self.exposure_in_ms)
    def set_slit_width(self,slit_width_in_um):
        self.slit_width_in_um = slit_width_in_um
        self.experiment.SetValue(SpectrometerSettings.OpticalPortEntranceSideWidth,
                                slit_width_in_um)
    def set_center_wavelength(self,center_lambda_in_nm):
        self.center_lambda_in_nm = center_lambda_in_nm
        self.experiment.SetValue(SpectrometerSettings.GratingCenterWavelength,
                                self.center_lambda_in_nm)
    def background_subraction_off(self):
        self.experiment.SetValue(ExperimentSettings.OnlineCorrectionsBackgroundCorrectionEnabled,
                       False)
    def background_subraction_on(self):
        self.experiment.SetValue(ExperimentSettings.OnlineCorrectionsBackgroundCorrectionEnabled,
                       True)
    def set_discard_frames(self,num_frames):
        self.num_frames =  int(num_frames)
        self.experiment.SetValue(ExperimentSettings.AcquisitionFramesToInitiallyDiscard,
                            (self.num_frames))
    def set_exposures_per_frame(self,num_frames, combine_by):
        self.experiment.SetValue(ExperimentSettings.FrameSettingsFramesCombined,
                           int(num_frames))
        self.combine_by = combine_by.lower()
        self.combine_mode = {'sum': 1, 'average': 2}[combine_by]
        self.experiment.SetValue(ExperimentSettings.FrameSettingsAverage,
                           combine_mode)
    def set_filename(self,radix):
        '''
        Set the filename of the file to be saved using a provided basename
        and attaching the epoch time with the last digit at 10^-7 s.
        '''
        fname = '%s-%s' % (radix, str(time.time()).ljust(18,'0').replace('.',''))
        self.experiment.SetValue(ExperimentSettings.FileNameGenerationBaseFileName,
                           fname)
    def set_shutter_mode(self,mode):
        mode = mode.lower()
        self.shutter_mode = mode
        modes = {'normal':1,
                'always_closed':2,
                'always_open':3,
                'open_before_trigger':4}
        if mode in modes.keys():
            self.experiment.SetValue(CameraSettings.ShutterTimingMode,modes[mode])
        else:
            print('Mode not valid.')
    def experiment_completed(self, sender, event_args):
        # Sets the state of the event to signaled.
        self.acquireCompleted.Set()
    def acquire_and_wait(self):
        self.acquireCompleted = AutoResetEvent(False)
        self.experiment.ExperimentCompleted += self.experiment_completed
        self.experiment.Acquire()
        self.acquireCompleted.WaitOne()
        self.experiment.ExperimentCompleted -= self.experiment_completed
    def configure_kinetics(self,spectra_kin_config):
        self.readout_mode = self.experiment.GetValue(CameraSettings.ReadoutControlMode)
        if self.readout_mode not in [3,4]:
            return "Camera not in a Kinetics mode."
        assert spectra_kin_config['storage_shift_rate_in_us'] in allowed_storage_shift_rates, "not allowed storage shift rate"
        assert type(spectra_kin_config['window_height']) == int, "window height must be int"
        assert spectra_kin_config['trigger_response'] in trigger_responses.keys(), "trigger response not available"
        assert spectra_kin_config['trigger_determined_by'] in ['Rising Edge', 'Falling Edge'], "invalid trigger det by"
        assert spectra_kin_config['frames_to_save'] % 528 == 0, "Frames to save not an integer multiple of 528."
        self.set_readout_mode(spectra_kin_config['readout_mode'])
        # set the exposure time
        self.set_exposure(spectra_kin_config['exposure_in_ms'])
        # set the window height
        self.experiment.SetValue(CameraSettings.ReadoutControlKineticsWindowHeight,
                            spectra_kin_config['window_height'])
        # set the storage shift rate
        self.experiment.SetValue(CameraSettings.ReadoutControlStorageShiftRate,
                           spectra_kin_config['storage_shift_rate_in_us'])
        # set the trigger reponse
        self.experiment.SetValue(CameraSettings.HardwareIOTriggerResponse,
                           trigger_responses[spectra_kin_config['trigger_response']])
        # set the trigger determined by
        self.experiment.SetValue(CameraSettings.HardwareIOTriggerDetermination,
          {'Rising Edge': 3,'Falling Edge': 4}[spectra_kin_config['trigger_determined_by']])
        # set the number of frames to save
        self.experiment.SetValue(ExperimentSettings.AcquisitionFramesToStore,
                                spectra_kin_config['frames_to_save'])
        # query the resulting frame rate
        spectra_kin_config['frame_rate'] = self.experiment.GetValue(CameraSettings.AcquisitionFrameRate)
        spectra_kin_config['temporal_resolution_in_ms'] = 1e3/spectra_kin_config['frame_rate']
        self.spectra_kin_config = spectra_kin_config
        return spectra_kin_config

def TRPL_HR(spectrumHR, lf, sig_gen, laser):
    spectrum1 = dict(spectrumHR)
    spectrum2 = dict(spectrumHR)
    spectrum1['cam_delay_in_s'] = 0.
    spectrum1 = TRPL(spectrum1, lf, sig_gen, laser)
    spectrum2 = TRPL(spectrum2, lf, sig_gen, laser)
    return [spectrum1, spectrum2]

def resolution_test_HR(spectrumHR, lf, sig_gen, laser):
    spectrum1 = dict(spectrumHR)
    spectrum2 = dict(spectrumHR)
    spectrum1['cam_delay_in_s'] = 0.
    spectrum1 = resolution_test(spectrum1, lf, sig_gen, laser)
    spectrum2 = resolution_test(spectrum2, lf, sig_gen, laser)
    return [spectrum1, spectrum2]


def TRPL(spectrum, lf, sig_gen, laser):
    '''This function receives the configuration for an experiment
    and runs it. The first argument is a dictionary with configuration
    parameters, the second one is the LF handle, the third one is
    for the signal generator and the final one is for the laser.'''
    frate = lf.get_frame_rate(spectrum['storage_shift_rate_in_us'],
            spectrum['window_height'], spectrum['exposure_in_ms'])
    spectrum['frames_to_save'] = spectrum['frames_per_rep']*spectrum['reps']
    spectrum['sig_gen_rate'] = int(0.95*frate/spectrum['frames_per_rep'])
    spectrum['approx_rep_period'] = 1/spectrum['sig_gen_rate']
    spectrum['excitation_duration_in_s'] = spectrum['fraction_of_excitation']*spectrum['approx_rep_period']

    print("Enforcing preferred naming scheme ...")
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachDate,False)
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachTime,False)
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationSaveRawData,False)
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachIncrement,False)
    if 'em_gain' in spectrum.keys():
        print("Setting AdC Quality to EM at 10 MHz...")
        lf.experiment.SetValue(CameraSettings.AdcQuality,3)
        lf.experiment.SetValue(CameraSettings.AdcSpeed,10.0)
        print("Setting the EM gain to %d ..." % spectrum['em_gain'])
        lf.set_EM_gain(spectrum['em_gain'])
    elif 'low_noise' in spectrum.keys():
        print("Setting AdC Quality to Low Noise at 5 MHz...")
        lf.experiment.SetValue(CameraSettings.AdcQuality,1)
        lf.experiment.SetValue(CameraSettings.AdcSpeed,5.0)
    print("Disabling automatic background subraction ...")
    lf.background_subraction_off()

    print("Setting the shutter mode...")
    lf.set_shutter_mode(spectrum['shutter_mode'])

    print("Configuring the signal generator...")
    if 'cam_delay_in_s' in spectrum.keys():
        if spectrum['cam_delay_in_s'] == -1:
            spectrum['cam_delay_in_s'] = 0.5 / frate
        sig_gen.set_pulseCD(spectrum['sig_gen_rate'],
                          spectrum['excitation_duration_in_s'],
                          spectrum['cam_delay_in_s'])
    else:
        sig_gen.set_pulseCD(spectrum['sig_gen_rate'],
                          spectrum['excitation_duration_in_s'],
                          0.)

    if 'laser_delay_in_s' in spectrum.keys():
        sig_gen.set_pulseAB(spectrum['sig_gen_rate'],
                          spectrum['excitation_duration_in_s'],
                          spectrum['laser_delay_in_s'])
    else:
        sig_gen.set_pulseAB(spectrum['sig_gen_rate'],
                          spectrum['excitation_duration_in_s'],
                          0)

    print("Configuring and turning on the laser...")
    laser.set_mode('pulsed')
    laser.on()
    sleep(0.1)
    laser.set_pulsed_power(spectrum['laser_power_in_mW'])
    sleep(0.1)

    print("Configuring the readout mode...")
    spectrum = lf.configure_kinetics(spectrum)

    print("Setting the number of frames to discard to %d ..." % int(spectrum['frames_to_discard']))
    lf.set_discard_frames(int(spectrum['frames_to_discard']))

    print("Configuring Isoplane...")
    print("--Setting the slit width to %.0f um ..." % spectrum['slit_width_in_um'])
    lf.set_slit_width(spectrum['slit_width_in_um'])
    print("--Moving the center wavelength to %.1f nm..." % spectrum['center_wavelength_in_nm'])
    lf.set_center_wavelength(spectrum['center_wavelength_in_nm'])
    sleep(0.1)

    lf.set_filename(spectrum['experiment_name']+'-cnt')
    while lf.experiment.GetValue(CameraSettings.SensorTemperatureReading) != spectrum['set_temp']:
        print("Waiting for sensor to cool down...")
        sleep(1)
    else:
        sleep(5)
    print("Acquiring data for background...")
    print("Acquiring data...")
    spectrum['start_time'] = int(time.time())
    lf.acquire_and_wait()
    spectrum['end_time'] = int(time.time())
    print("Turning off the laser...")
    lf.set_filename(spectrum['experiment_name']+'-bkg')
    laser.off()
    spectrum['counts'] = {}
    spectrum['counts']['spe'] = get_latest_spe_fname(lf.lf_dir)
    sleep(2)

    while lf.experiment.GetValue(CameraSettings.SensorTemperatureReading) != spectrum['set_temp']:
        print("Waiting for sensor to cool down...")
        sleep(1)
    else:
        sleep(5)
    print("Acquiring data for background...")
    lf.acquire_and_wait()
    spectrum['bkg'] = {}
    spectrum['bkg']['spe'] = get_latest_spe_fname(lf.lf_dir)

    if 'em_gain' in spectrum.keys():
        print("Bringing EM gain back home...")
        lf.set_EM_gain(10)

    spectrum['pkl_name'] = '{experiment_name}-{start_time}.pkl'.format(**spectrum)
    print(spectrum['pkl_name'])
    print("Saving pkl to %s" % lf.lf_dir)
    pickle.dump(spectrum,open(os.path.join(lf.lf_dir,spectrum['pkl_name']),'wb'))
    return spectrum

def resolution_test(spectrum, lf, sig_gen, laser):
    '''This function receives the configuration for an experiment
    and runs it. The first argument is a dictionary with configuration
    parameters, the second one is the LF handle, the third one is
    for the signal generator and the final one is for the laser.'''
    spectrum['frames_to_save'] = spectrum['frames_per_rep']*spectrum['reps']
    spectrum['cam_rate'] = int(0.9*lf.get_frame_rate(spectrum['storage_shift_rate_in_us'],
            spectrum['window_height'], spectrum['exposure_in_ms'],)/spectrum['frames_per_rep'])
    spectrum['comb_rate'] = 50*spectrum['cam_rate']
    spectrum['excitation_duration_in_s'] = 0.5/spectrum['comb_rate']
    #spectrum['approx_rep_period'] = 1/spectrum['sig_gen_rate']
    #spectrum['excitation_duration_in_s'] = spectrum['fraction_of_excitation']*spectrum['approx_rep_period']

    print("Enforcing preferred naming scheme ...")
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachDate,False)
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachTime,False)
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationSaveRawData,False)
    lf.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachIncrement,False)
    if 'em_gain' in spectrum.keys():
        print("Setting AdC Quality to EM at 10 MHz...")
        lf.experiment.SetValue(CameraSettings.AdcQuality,3)
        lf.experiment.SetValue(CameraSettings.AdcSpeed,10.0)
        print("Setting the EM gain to %d ..." % spectrum['em_gain'])
        lf.set_EM_gain(spectrum['em_gain'])
    elif 'low_noise' in spectrum.keys():
        print("Setting AdC Quality to Low Noise at 5 MHz...")
        lf.experiment.SetValue(CameraSettings.AdcQuality,1)
        lf.experiment.SetValue(CameraSettings.AdcSpeed,5.0)
    print("Disabling automatic background subraction ...")
    lf.background_subraction_off()

    print("Setting the shutter mode...")
    lf.set_shutter_mode(spectrum['shutter_mode'])

    # this one is for the laser
    sig_gen.set_pulseAB(spectrum['comb_rate'],
                       spectrum['excitation_duration_in_s'],0.)
    # this one goes to trigger the camera
    sig_gen.set_pulseCD(20*spectrum['comb_rate'],
                      0.5/spectrum['cam_rate'],spectrum['cam_delay_in_s'])

    print("Configuring and turning on the laser...")
    laser.set_mode('pulsed')
    laser.on()
    sleep(0.1)
    laser.set_pulsed_power(spectrum['laser_power_in_mW'])
    sleep(0.1)

    print("Configuring the readout mode...")
    spectrum = lf.configure_kinetics(spectrum)

    print("Setting the number of frames to discard to %d ..." % int(spectrum['frames_to_discard']))
    lf.set_discard_frames(int(spectrum['frames_to_discard']))

    print("Configuring Isoplane...")
    print("--Setting the slit width to %.0f um ..." % spectrum['slit_width_in_um'])
    lf.set_slit_width(spectrum['slit_width_in_um'])
    print("--Moving the center wavelength to %.1f nm..." % spectrum['center_wavelength_in_nm'])
    lf.set_center_wavelength(spectrum['center_wavelength_in_nm'])
    sleep(0.1)

    lf.set_filename(spectrum['experiment_name']+'-cnt')
    while lf.experiment.GetValue(CameraSettings.SensorTemperatureReading) != spectrum['set_temp']:
        print("Waiting for sensor to cool down...")
        sleep(1)
    else:
        sleep(5)
    print("Acquiring data for background...")
    print("Acquiring data...")
    spectrum['start_time'] = int(time.time())
    lf.acquire_and_wait()
    spectrum['end_time'] = int(time.time())
    print("Turning off the laser...")
    lf.set_filename(spectrum['experiment_name']+'-bkg')
    laser.off()
    spectrum['counts'] = {}
    spectrum['counts']['spe'] = get_latest_spe_fname(lf.lf_dir)
    sleep(2)

    while lf.experiment.GetValue(CameraSettings.SensorTemperatureReading) != spectrum['set_temp']:
        print("Waiting for sensor to cool down...")
        sleep(1)
    else:
        sleep(5)
    print("Acquiring data for background...")
    lf.acquire_and_wait()
    spectrum['bkg'] = {}
    spectrum['bkg']['spe'] = get_latest_spe_fname(lf.lf_dir)

    if 'em_gain' in spectrum.keys():
        print("Bringing EM gain back home...")
        lf.set_EM_gain(10)

    spectrum['pkl_name'] = '{experiment_name}-{start_time}.pkl'.format(**spectrum)
    print(spectrum['pkl_name'])
    print("Saving pkl to %s" % lf.lf_dir)
    pickle.dump(spectrum,open(os.path.join(lf.lf_dir,spectrum['pkl_name']),'wb'))
    return spectrum
