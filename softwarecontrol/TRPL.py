#!/usr/bin/env python3


def find_setting(search):
    '''
    Search for a setting in the Lightfield API.
    '''
    search = search.lower()
    return {'cam_settings' : [s for s in lf_settings['camera_settings']
                              if search in s.lower()],
    'exp_settings': [s for s in lf_settings['experiment_settings']
                     if search in s.lower()],
    'spec_settings': [s for s in lf_settings['spectrometer_settings']
                      if search in s.lower()]}
def experiment_completed(sender, event_args):
    # Sets the state of the event to signaled,
    # allowing one or more waiting threads to proceed.
    acquireCompleted.Set()
def get_latest_spe_fname(directory):
    '''
    Returns the filename of the most recent spe file in the given directory.
    '''
    if( os.path.exists(directory)):
        files = glob.glob(directory +'/*.spe')
        last_spe = max(files, key=os.path.getctime)
    else:
        print("no such dir...")
    last_spe = os.path.split(last_spe)
    return {'dir': last_spe[0], 'fname': last_spe[1]}
def bell():
    winsound.PlaySound(os.path.join(codebase_dir,'sounds','bell.wav'),
                   winsound.SND_ASYNC)
def acquire_and_wait():
    def experiment_completed(sender, event_args):
        # Sets the state of the event to signaled.
        acquireCompleted.Set()
    acquireCompleted = AutoResetEvent(False)
    experiment.ExperimentCompleted += experiment_completed
    experiment.Acquire()
    acquireCompleted.WaitOne()
    experiment.ExperimentCompleted -= experiment_completed
def set_exposure(exposure_in_ms):
    exposure_in_ms = float(np.round(exposure_in_ms,4))
    experiment.SetValue(CameraSettings.ShutterTimingExposureTime,
                        exposure_in_ms)
def set_slit_width(slit_width_in_um):
    experiment.SetValue(SpectrometerSettings.OpticalPortEntranceSideWidth,
                            slit_width_in_um)
def set_center_wavelength(center_lambda_in_nm):
    experiment.SetValue(SpectrometerSettings.GratingCenterWavelength,
                            center_lambda_in_nm)
def background_subraction_off():
    experiment.SetValue(ExperimentSettings.OnlineCorrectionsBackgroundCorrectionEnabled,
                   False)
def background_subraction_on():
    experiment.SetValue(ExperimentSettings.OnlineCorrectionsBackgroundCorrectionEnabled,
                   True)
def discard_frames(num_frames):
    experiment.SetValue(ExperimentSettings.AcquisitionFramesToInitiallyDiscard,
                        int(num_frames))
def exposures_per_frame(num_frames, combine_by):
    experiment.SetValue(ExperimentSettings.FrameSettingsFramesCombined,
                       int(num_frames))
    combine_by = combine_by.lower()
    combine_mode = {'sum': 1, 'average': 2}[combine_by]
    experiment.SetValue(ExperimentSettings.FrameSettingsAverage,
                       combine_mode)
def set_filename(radix):
    '''
    Set the filename of the file to be saved using a provided basename
    and attaching the epoch time with the last digit at 10^-7 s.
    '''
    fname = '%s-%s' % (radix, str(time.time()).ljust(18,'0').replace('.',''))
    experiment.SetValue(ExperimentSettings.FileNameGenerationBaseFileName,
                       fname)
def wait(wait_duration=0.1):
    time.sleep(wait_duration)
def set_shutter_mode(mode):
    mode = mode.lower()
    modes = {'normal':1,
            'always_closed':2,
            'always_open':3,
            'open_before_trigger':4}
    if mode in modes.keys():
        experiment.SetValue(CameraSettings.ShutterTimingMode,modes[mode])
    else:
        print('Mode not valid.')
