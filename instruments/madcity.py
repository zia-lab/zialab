#!/usr/bin/env python3
# ╔═══════════════════════╗
# ║   __  __  ____ _      ║
# ║  |  \/  |/ ___| |     ║
# ║  | |\/| | |   | |     ║
# ║  | |  | | |___| |___  ║
# ║  |_|  |_|\____|_____| ║
# ║                       ║
# ║    mad city labs      ║
# ╚═══════════════════════╝

# Edited by David on 2020
# based on Yang's old code
# where he based that from is not known

from ctypes import Structure, CDLL, pointer, c_long, c_char
from ctypes import c_ubyte, c_double, c_uint, c_int, c_short, byref
from time import sleep
import sys, os, atexit

class Product_Information(Structure):
    '''''''''''''''''''''''''''''''''''''''''
    Struct pointer that stores product info.
    '''''''''''''''''''''''''''''''''''''''''
    _fields_ = [('axis_bitmap', c_char), ('ADC_resolution', c_short), ('DAC_resolution', c_short),
                ('Product_id', c_short), ('FirmwareVersion', c_short), ('FirmwareProfile', c_short)]
# C:\Users\lab_pc_v\Desktop\MCL-LP300\program files\Mad City Labs\NanoDrive
class MadPiezo:

    # MCL = CDLL('D://Google Drive//Zia Lab//Codebase//zialab//instruments//DLLs//Madlib.dll')
    MCL = CDLL('C://Program Files//Mad City Labs//NanoDrive//Madlib.dll')
    # MCL = CDLL('C://Users//lab_pc_v//Desktop//MCL-LP300//program files//Mad City Labs//NanoDrive//Madlib.dll')

    '''''''''''''''''''''
    Function Definitions
    '''''''''''''''''''''
    # handle management functions.
    _open                     = MCL['MCL_InitHandle']
    _close                    = MCL['MCL_ReleaseAllHandles']
    _get_serial               = MCL['MCL_GetSerialNumber']
    _get_version              = MCL['MCL_DLLVersion']
    _get_calibration          = MCL['MCL_GetCalibration']
    _current_handles          = MCL['MCL_NumberOfCurrentHandles']
    _read_axis                = MCL['MCL_SingleReadN']
    _write_axis               = MCL['MCL_SingleWriteN']
    _monitor_axis             = MCL['MCL_MonitorN']
    _get_product              = MCL['MCL_GetProductInfo']
    _open.restype             = c_int
    _get_serial.restype       = c_int
    _current_handles.restype  = c_int
    _get_calibration.restype  = c_double
    _read_axis.restype        = c_double
    _write_axis.restype       = c_int
    _monitor_axis.restype     = c_double
    _get_product.restype      = c_int
    # ISS functions.
    _bind_clock               = MCL['MCL_IssBindClockToAxis']
    _pixel_clock              = MCL['MCL_PixelClock']
    _line_clock               = MCL['MCL_LineClock']
    _frame_clock              = MCL['MCL_FrameClock']
    _aux_clock                = MCL['MCL_AuxClock']
    _reset_iss                = MCL['MCL_IssBindClockToAxis']
    _bind_clock.restype       = c_int
    _pixel_clock.restype      = c_int
    _line_clock.restype       = c_int
    _frame_clock.restype      = c_int
    _aux_clock.restype        = c_int
    _reset_iss.restype        = c_int
    # waveform acquisition functions.
    _read_waveform            = MCL['MCL_ReadWaveFormN']
    _load_waveform            = MCL['MCL_LoadWaveFormN']
    _trigger_wfread           = MCL['MCL_Trigger_ReadWaveFormN']
    _trigger_wfload           = MCL['MCL_Trigger_LoadWaveFormN']
    _setup_wfread             = MCL['MCL_Setup_ReadWaveFormN']
    _setup_wfload             = MCL['MCL_Setup_LoadWaveFormN']
    _waveform_acquire         = MCL['MCL_TriggerWaveformAcquisition']
    _setup_wfma               = MCL['MCL_WfmaSetup']
    _trigger_wfma             = MCL['MCL_WfmaTrigger']
    _read_wfma                = MCL['MCL_WfmaRead']
    _trigger_read_wfma        = MCL['MCL_WfmaTriggerAndRead']
    _stop_wfma                = MCL['MCL_WfmaStop']
    _read_waveform.restype    = c_int
    _load_waveform.restype    = c_int
    _trigger_wfread.restype   = c_int
    _trigger_wfload.restype   = c_int
    _setup_wfread.restype     = c_int
    _setup_wfload.restype     = c_int
    _waveform_acquire.restype = c_int
    _setup_wfma.restype       = c_int
    _trigger_wfma.restype     = c_int
    _stop_wfma.restype        = c_int
    _read_wfma.restype        = c_int
    _trigger_read_wfma.restype= c_int

    '''''''''''''''''''''''''''''''''''
    Basic Functions (Handle Management)
    '''''''''''''''''''''''''''''''''''
    def __init__(self):
        '''
        load the madlib dll and check whether any existing device connections.
        '''
        self.connected = False
        self.version, self.revision = c_short(0), c_short(0)
        self.home_pos = 0. # all axes are moved to this position when closing
        self.platform = sys.platform
        assert self.platform == 'win32', "Only runs on Windows."
        self.shortname = 'MCL stage'
        self.fullname = 'MCL - Nano-LPXXX'
        self.notes = ''
        print(self.notes)
        self._get_version(pointer(self.version), pointer(self.revision))
        print('DLL Version:{}.{}'.format(self.version.value, self.revision.value))
        current_handles = self._current_handles()
        # print('Current Handles:{}'.format(current_handles))
        if current_handles != 0:
            print('Releasing all handles...')
            self.close()
            current_handles = self._current_handles()
            print('Current Handles:{}'.format(current_handles))
        self.open()
        print(self.qPOS())
        atexit.register(self.close)

    def get_calibration(self):
        '''
        get the travel ranges for all three axes.
        '''
        if self.connected:
            self.x_cal = self._get_calibration(c_uint(1), self.handle)
            self.y_cal = self._get_calibration(c_uint(2), self.handle)
            self.z_cal = self._get_calibration(c_uint(3), self.handle)
            print('X_Range:{}um, Y_Range:{}um, Z_Range:{}um'.format(self.x_cal, self.y_cal, self.z_cal))
        else:
            print('Missing device handle.')

    def get_product_info(self):
        '''
        Retrieve product information from the firmware.
        '''
        product_info = Product_Information(0, 0, 0, 0, 0, 0)
        if self.connected:
            if self._get_product(byref(product_info), self.handle)!=0:
                raise Exception('Retrive product information failed.')
            self.axis_bitmap      = product_info.axis_bitmap
            # print('Bitmap:{}{}{}{}{}'.format(self.axis_bitmap&1, self.axis_bitmap&2, self.axis_bitmap&3, self.axis_bitmap&4, self.axis_bitmap&5))
            self.ADC_res          = product_info.ADC_resolution
            self.DAC_res          = product_info.DAC_resolution
            self.product_id       = product_info.Product_id
            self.firmware_version = product_info.FirmwareVersion
            self.firmware_profile = product_info.FirmwareProfile
            self.serial = self._get_serial(self.handle)
            print('Axis Bitmap:{}, Product ID:{}\nADC Resolution:{}, DAC Resolution:{}\nFirmware Version:{}, Firmware Profile:{}, Serial Number:{}'.format(self.axis_bitmap, self.product_id, self.ADC_res, self.DAC_res,
                  self.firmware_version, self.firmware_profile, self.serial))
        else:
            print('Device is NOT CONNECTED.')

    def open(self):
        '''
        Connect to the device.
        '''
        self.handle = self._open()
        if self.handle != 0:
            print('Stage is CONNECTED.\nHandle:{}\n'.format(self.handle))
            self.connected = True
            self.get_calibration()
        else:
            print('Stage is NOT CONNECTED. Check connections and handlers.')

    def close(self):
        '''
        Disconnect the device.
        '''
        self.move('x', self.home_pos)
        self.move('y', self.home_pos)
        self.move('z', self.home_pos)
        self._close()
        print('Stage is DISCONNECTED.')
        current_handles = self._current_handles()
        print('Current Handles:{}\n'.format(current_handles))

    '''''''''''''''''''''
    Movement Functions
    '''''''''''''''''''''
    def read_axis(self, axis):
        '''
        Read the position of a given axis.
        '''
        if axis in ['x', 'X', 1]:
            x_pos = self._read_axis(c_uint(1), self.handle)
            return x_pos
        elif axis in ['y', 'Y', 2]:
            y_pos = self._read_axis(c_uint(2), self.handle)
            return y_pos
        elif axis in ['z', 'Z', 3]:
            z_pos = self._read_axis(c_uint(3), self.handle)
            return z_pos
        else:
            print('Unkown axis.')

    def qPOS(self):
        '''
        Query the x-y-z positions of the stage.
        '''
        x_pos = self._read_axis(c_uint(1), self.handle)
        y_pos = self._read_axis(c_uint(2), self.handle)
        z_pos = self._read_axis(c_uint(3), self.handle)
        return x_pos, y_pos, z_pos

    def move(self, axis, pos):
        '''
        move an axis to a given position within the travel range.
        '''
        if axis in ['x', 'X', 1]:
            assert 0 <= pos < self.x_cal, 'Position outside of travel range.'
            self._write_axis(c_double(pos), c_uint(1), self.handle)
            sleep(0.1)
            self.qPOS()
        elif axis in ['y', 'Y', 2]:
            assert 0 <= pos < self.y_cal, 'Position outside of travel range.'
            self._write_axis(c_double(pos), c_uint(2), self.handle)
            sleep(0.1)
            self.qPOS()
        elif axis in ['z', 'Z', 3]:
            assert 0 <= pos < self.z_cal, 'Position outside of travel range.'
            self._write_axis(c_double(pos), c_uint(3), self.handle)
            sleep(0.1)
            self.qPOS()
        else:
            print('Unkown axis.')

    def monitor_axis(self, axis, pos):
        '''
        Move and read an axis.
        '''
        if axis in ['x', 'X', 1]:
            x_pos = self._monitor_axis(c_double(pos), c_uint(1), self.handle)
            return x_pos
        elif axis in ['y', 'Y', 2]:
            y_pos = self._monitor_axis(c_double(pos), c_uint(2), self.handle)
            return y_pos
        elif axis in ['z', 'Z', 3]:
            z_pos = self._monitor_axis(c_double(pos), c_uint(3), self.handle)
            return z_pos
        else:
            print('Invalid axis.')


    '''''''''''''''''''''''''''''''''
    ISS Functions (Clock Management)
    '''''''''''''''''''''''''''''''''
    def reset_iss(self):
        '''
        Reset the iss option to the default values. No axis binding, low-high polarity, pixel clock is bound to waveform read.
        '''
        if self.connected:
            self._reset_iss(self.handle)
        else:
            print('Device is NOT CONNECTED.')

    def bind_clock(self, axis=1, mode=2, clock=1):
        '''
        Default is to bind a low-high pixel clock to the x-axis.

        clock (c_int):
            1=Pixel, 2=Line, 3=Frame, 4=Aux
        mode (c_int):
            2=low to high pulse, 3=high to low pulse, 4=unbind the axis
        axis (c_uint):
            1=X-axis, 2=Y-axis, 3=Z-axis, 4=Aux-axis, 5=Waveform Read, 6=Waveform Write
        '''
        self._bind_clock(c_int(clock), c_int(mode), c_int(axis), self.handle)

    def pixel_clock(self):
        '''
        Triggers a TTL pulse from the pixel clock.
        '''
        self._pixel_clock(self.handle)

    def line_clock(self):
        '''
        Triggers a TTL pulse from the line clock.
        '''
        self._line_clock(self.handle)

    def frame_clock(self):
        '''
        Triggers a TTL pulse from the frame clock.
        '''
        self._frame_clock(self.handle)

    def aux_clock(self):
        '''
        Triggers a TTL pulse from the aux clock.
        '''
        self._aux_clock(self.handle)

    '''''''''''''''''''''
    Waveform Functions
    '''''''''''''''''''''
    def setup_wfload(self, axis, npoints, dwell_time, waveform):
        '''
        Sets up a waveform load on a specific axis.

        dwell_time is in miliseconds. npoints should correspond to the size of the waveform.
        '''
        wf = (c_double*npoints)(*waveform)
        error_code = self._setup_wfload(c_uint(axis), c_uint(npoints), c_double(dwell_time), pointer(wf), self.handle)
        if error_code!=0:
            print('Error Code:{}'.format(error_code))

    def setup_wfread(self, axis, npoints, dwell_time):
        '''
        sets up a waveform read on an axis.

        note that dwell_time is fed into a dictionary with only few allowed values.
        dwell_time: 3->267us, 4->500us, 5->1ms, 6->2ms (for our 20-bit communication)
        '''
        assert dwell_time in [3, 4, 5, 6], print('Invalid dwell_time. Check doc string.')
        error_code = self._setup_wfread(c_uint(axis), c_uint(npoints), c_double(dwell_time), self.handle)
        if error_code!=0:
            print('Error Code:{}'.format(error_code))

    def waveform_acquire(self, axis, npoints, waveform):
        '''
        Triggers a synchronous waveform read and load on an axis.
        '''
        wf = (c_double*npoints)(*waveform)
        error_code = self._waveform_acquire(c_uint(axis), c_uint(npoints), pointer(wf), self.handle)
        if error_code!=0:
            print('Error Code:{}'.format(error_code))

    def read_waveform(self, axis, npoints, dwell_time):
        '''
        Sets up and triggers a waveform read on an axis.

        note that dwell_time is fed into a dictionary with only few allowed values.
        dwell_time: 3->267us, 4->500us, 5->1ms, 6->2ms (for our 20-bit communication)
        '''
        assert dwell_time in [3, 4, 5, 6], print('Invalid dwell_time. Check doc string.')
        waveform = [0]*npoints
        wf = (c_double*npoints)(*waveform) # a waveform returned by the firmware, not an input.
        error_code = self._read_waveform(c_uint(axis), c_uint(npoints), c_double(dwell_time), pointer(wf), self.handle)
        if error_code==0:
            print('Waveform read COMPLETE.')
            return wf
        else:
            print('Error Code:{}'.format(error_code))

    def load_waveform(self, axis, npoints, dwell_time, waveform):
        '''
        sets up and triggers a waveform read on an axis.
        '''
        wf = (c_double*npoints)(*waveform) # a waveform that we provide the firmware with, an input.
        error_code = self._load_waveform(c_uint(axis), c_uint(npoints), c_double(dwell_time), pointer(wf), self.handle)
        if error_code!=0:
            print('Error Code:{}'.format(error_code))
        else:
            print('Waveform load COMPLETE.')

    def trigger_wfread(self, axis, npoints):
        '''
        triggers a waveform read on an axis.
        '''
        waveform = [0]*npoints
        wf = (c_double*npoints)(*waveform) # a waveform returned by the firmware, not an input.
        error_code = self._trigger_wfread(self, c_uint(axis), c_uint(npoints), pointer(wf), self.handle)
        if error_code==0:
            print('Waveform read Triggered.')
            return wf
        else:
            print('Error Code:{}'.format(error_code))

    def trigger_wfload(self, axis):
        '''
        trigger a waveform load on an axis.
        '''
        error_code = self._trigger_wfload(c_uint(axis), self.handle)
        if error_code==0:
            print('Waveform load triggered.')
        else:
            print('Error Code:{}'.format(error_code))

    '''''''''''''''''''''''''''''''''
    Multi-axis Waveform Functions
    '''''''''''''''''''''''''''''''''
    def setup_wfma(self, waveformx, waveformy, waveformz, npoints, dwell_time, iterations):
        '''
        sets up a multi-axis waveform.

        for 20-bit systems, the maximum number of data points per axis is 2,222.
                            the dwell time is fed into a dictionary with keys 3, 4, 5, or 6.
        '''
        assert npoints<2222, print('Too many data points per axis.')
        assert dwell_time in [3, 4, 5, 6], print('Invalid dwell_time. Check doc string.')
        wfx = (c_double*npoints)(*waveformx)
        wfy = (c_double*npoints)(*waveformy)
        wfz = (c_double*npoints)(*waveformz)
        error_code = self._setup_wfma(pointer(wfx), pointer(wfy), pointer(wfz), c_uint(npoints), c_double(dwell_time), c_short(iterations), self.handle)
        if error_code==0:
            print('Multi-axis waveform SET.')
        else:
            print('Error Code:{}'.format(error_code))

    def trigger_read_wfma(self, waveformx, waveformy, waveformz, npoints):
        '''
        triggers an multi-axis waveform and waits for it to finish.
        '''
        wfx = (c_double*npoints)(*waveformx)
        wfy = (c_double*npoints)(*waveformy)
        wfz = (c_double*npoints)(*waveformz)
        error_code = self._trigger_read_wfma(pointer(wfx), pointer(wfy), pointer(wfz), self.handle)
        if error_code==0:
            print('Multi-axis waveform triggered and running...')
        else:
            print('Error Code:{}'.format(error_code))

    def trigger_wfma(self):
        '''
        trigger a multi-axis waveform.
        '''
        error_code = self._trigger_wfma(self.handle)
        if error_code==0:
            print('Multi-axis waveform TRIGGERED.')
        else:
            print('Error Code:{}'.format(error_code))

    def _read_wfma(self, waveformx, waveformy, waveformz):
        '''
        reads a multi-axis waveform.
        '''
        wfx = (c_double*npoints)(*waveformx)
        wfy = (c_double*npoints)(*waveformy)
        wfz = (c_double*npoints)(*waveformz)
        error_code = self._read_wfma(pointer(wfx), pointer(wfy), pointer(wfz), self.handle)
        if error_code==0:
            print('Multi-axis waveform READ.')
        else:
            print('Error Code:{}'.format(error_code))

    def stop_wfma(self):
        '''
        stop a multi-axis waveform.
        '''
        error_code = self._stop_wfma(self.handle)
        if error_code==0:
            print('Multi-axis waveform STOPPED.')
        else:
            print('Error Code:{}'.format(error_code))
