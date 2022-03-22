#!/usr/bin/env python3

#   ╔═════════════════════════════════════════════════╗
#   ║                                                 ║
#   ║                    26444444444444444822         ║
#   ║                   2222222222222222    6         ║
#   ║              644444444444444444882  68  4       ║
#   ║            62 222222222           8  2  8       ║
#   ║         2  6 6        666666646    8 24         ║
#   ║        844                     4   8  4         ║
#   ║       6  6                      8  2  4         ║
#   ║      24 2                       4  2  4         ║
#   ║      2  2                       24 2  4         ║
#   ║      2  2                        4 2  4         ║
#   ║      2  2                        4 2  4         ║
#   ║      2  2         attocube       4 2  4 4       ║
#   ║      2  2      nanopositioners   4 2  4 4       ║
#   ║      2  6                        4 2  4         ║
#   ║      2   4                       4 2  6         ║
#   ║      2   4                       42             ║
#   ║      2   8                       44             ║
#   ║      62  68                                     ║
#   ║       4    84444444444444444444                 ║
#   ║       8                      26                 ║
#   ║        6862222222222222222284                   ║
#   ║                                                 ║
#   ╚═════════════════════════════════════════════════╝
#

#                         based on
#                 PyANC350 written by Rob Heath
#                      rob@robheath.me.uk
#                         24-Feb-2015
#                       robheath.me.uk
#
#                 PyANC350v4 by Brian Schaefer
#                      bts72@cornell.edu
#                         5-Jul-2016
#              http://nowack.lassp.cornell.edu/
#
#             https://github.com/Laukei/pyanc350

import ctypes, math, os
from time import sleep, time
from tqdm.notebook import tqdm

anc350v3 = ctypes.windll.LoadLibrary('D:\\Google Drive\\Zia Lab\\Codebase\\zialab\\instruments\\DLLs\\anc350v3.dll')

# aliases for the functions in the dll

###############################
#### Aliases for dll funcs ####

discover = getattr(anc350v3,"ANC_discover")
getDeviceInfo = getattr(anc350v3,"ANC_getDeviceInfo")
connect = getattr(anc350v3,"ANC_connect")
disconnect = getattr(anc350v3,"ANC_disconnect")

getDeviceConfig = getattr(anc350v3,"ANC_getDeviceConfig")
getAxisStatus = getattr(anc350v3,"ANC_getAxisStatus")
setAxisOutput = getattr(anc350v3,"ANC_setAxisOutput")
setAmplitude = getattr(anc350v3,"ANC_setAmplitude")

setFrequency = getattr(anc350v3,"ANC_setFrequency")
setDcVoltage = getattr(anc350v3,"ANC_setDcVoltage")
getAmplitude = getattr(anc350v3,"ANC_getAmplitude")
getFrequency = getattr(anc350v3,"ANC_getFrequency")

startSingleStep = getattr(anc350v3,"ANC_startSingleStep")
startContinousMove = getattr(anc350v3,"ANC_startContinousMove")
startAutoMove = getattr(anc350v3,"ANC_startAutoMove")
setTargetPosition = getattr(anc350v3,"ANC_setTargetPosition")

setTargetRange = getattr(anc350v3,"ANC_setTargetRange")
getPosition = getattr(anc350v3,"ANC_getPosition")
getFirmwareVersion = getattr(anc350v3,"ANC_getFirmwareVersion")
configureExtTrigger = getattr(anc350v3,"ANC_configureExtTrigger")

configureAQuadBIn = getattr(anc350v3,"ANC_configureAQuadBIn")
configureAQuadBOut = getattr(anc350v3,"ANC_configureAQuadBOut")
configureRngTriggerPol = getattr(anc350v3,"ANC_configureRngTriggerPol")
configureRngTrigger = getattr(anc350v3,"ANC_configureRngTrigger")

configureRngTriggerEps = getattr(anc350v3,"ANC_configureRngTriggerEps")
configureNslTrigger = getattr(anc350v3,"ANC_configureNslTrigger")
configureNslTriggerAxis = getattr(anc350v3,"ANC_configureNslTriggerAxis")
selectActuator = getattr(anc350v3,"ANC_selectActuator")

getActuatorName = getattr(anc350v3,"ANC_getActuatorName")
getActuatorType = getattr(anc350v3,"ANC_getActuatorType")
measureCapacitance = getattr(anc350v3,"ANC_measureCapacitance")
saveParams = getattr(anc350v3,"ANC_saveParams")

#### Aliases for dll funcs ####
###############################

###############################
##### List of error types #####

ANC_Ok = 0                      # No error
ANC_Error = -1                  # Unknown / other error
ANC_Timeout = 1                 # Timeout during data retrieval
ANC_NotConnected = 2            # No contact with the Nanocube via USB
ANC_DriverError = 3             # Error in the driver response
ANC_DeviceLocked = 7            # A connection attempt failed because the device is already in use
ANC_Unknown = 8                 # Unknown error.
ANC_NoDevice = 9                # Invalid device number used in call
ANC_NoAxis = 10                 # Invalid axis number in function call
ANC_OutOfRange = 11             # Parameter in call is out of range
ANC_NotAvailable = 12           # Function not available for device type

##### List of error types #####
###############################

def checkError(code,func,args):
    '''checks the errors returned from the dll'''
    if code == ANC_Ok:
        return
    elif code == ANC_Error:
        raise Exception("Error: unspecific in"+str(func.__name__)+"with parameters:"+str(args))
    elif code == ANC_Timeout:
        raise Exception("Error: comm. timeout in"+str(func.__name__)+"with parameters:"+str(args))
    elif code == ANC_NotConnected:
        raise Exception("Error: not connected")
    elif code == ANC_DriverError:
        raise Exception("Error: driver error")
    elif code == ANC_DeviceLocked:
        raise Exception("Error: device locked")
    elif code == ANC_NoDevice:
        raise Exception("Error: invalid device number")
    elif code == ANC_NoAxis:
        raise Exception("Error: invalid axis number")
    elif code == ANC_OutOfRange:
        raise Exception("Error: parameter out of range")
    elif code == ANC_NotAvailable:
        raise Exception("Error: function not available")
    else:
        raise Exception("Error: unknown in"+str(func.__name__)+"with parameters:"+str(args))
    return code

###############################
#set error checking & handling#

discover.errcheck = checkError
connect.errcheck = checkError
disconnect.errcheck = checkError
getDeviceConfig.errcheck = checkError

getAxisStatus.errcheck = checkError
setAxisOutput.errcheck = checkError
setAmplitude.errcheck = checkError
setFrequency.errcheck = checkError

setDcVoltage.errcheck = checkError
getAmplitude.errcheck = checkError
getFrequency.errcheck = checkError
startSingleStep.errcheck = checkError

startContinousMove.errcheck = checkError
startAutoMove.errcheck = checkError
setTargetPosition.errcheck = checkError
setTargetRange.errcheck = checkError

getPosition.errcheck = checkError
getFirmwareVersion.errcheck = checkError
configureExtTrigger.errcheck = checkError
configureAQuadBIn.errcheck = checkError

configureAQuadBOut.errcheck = checkError
configureRngTriggerPol.errcheck = checkError
configureRngTrigger.errcheck = checkError
configureRngTriggerEps.errcheck = checkError

configureNslTrigger.errcheck = checkError
configureNslTriggerAxis.errcheck = checkError
selectActuator.errcheck = checkError
getActuatorName.errcheck = checkError

getActuatorType.errcheck = checkError
measureCapacitance.errcheck = checkError
saveParams.errcheck = checkError

#set error checking & handling#
###############################

class Nanocube:

    def __init__(self, config_params):
        self.discover()
        self.device = self.connect()
        self.y_lim = config_params['y_lim'] # approx 5000 - thickness_of_sample
        self.sample_thickness = config_params['sample_thickness']
        self.rough_focus = 4720 - config_params['sample_thickness']
        print("x-axis = horizontal axis; y-axis = optical axis; z-axis = up-down")

    def configureAQuadBIn(self, axisNo: int, enable: int, resolution: float) -> None:
        '''
        Enables and configures the A-Quad-B (quadrature) input for the target position.

        Args:
            axisNo:     Axis number (0 ... 2)
            enable:     Enable (1) or disable (0) A-Quad-B input
            resolution: A-Quad-B step width in m. Internal resolution is 1 nm.

        Returns:
            None
        '''
        configureAQuadBIn(self.device, axisNo, enable, ctypes.c_double(resolution))

    def configureAQuadBOut(self, axisNo: int, enable: int, resolution: float, clock: float) -> None:
        '''
        Enables and configures the A-Quad-B output of the current position.

        Args:
            axisNo:     Axis number (0 ... 2)
            enable:     Enable (1) or disable (0) A-Quad-B output
            resolution: A-Quad-B step width in m; internal resolution is 1 nm
            clock:      Clock of the A-Quad-B output [s].
                        Allowed range is 40ns ... 1.3ms; internal resulution is 20ns.

        Returns:
            None
        '''
        configureAQuadBOut(self.device, axisNo, enable, ctypes.c_double(resolution), ctypes.c_double(clock))

    def configureExtTrigger(self, axisNo: int, mode: int) -> None:
        '''
        Enables the input trigger for steps.

        Args:
            axisNo:	Axis number (0 ... 2)
            mode:	Disable (0), Quadrature (1), Trigger(2) for external triggering

        Returns:
            None
        '''
        configureExtTrigger(self.device, axisNo, mode)

    def configureNslTrigger(self, enable: int) -> None:
        '''
        Enables NSL Input as Trigger Source.

        Args:
            enable:	disable(0), enable(1)

        Returns:
            None
        '''
        configureNslTrigger(self.device, enable)

    def configureNslTriggerAxis(self, axisNo: int) -> None:
        '''
        Selects Axis for NSL Trigger.

        Args:
            axisNo:	Axis number (0 ... 2)

        Returns:
            None
        '''
        configureNslTriggerAxis(self.device, axisNo)

    def configureRngTrigger(self, axisNo: int, lower: float, upper: float) -> None:
        '''
        Configure lower position for range Trigger.

        Args:
            axisNo:	Axis number (0 ... 2)
            lower:	Lower position for range trigger (nm)
            upper:	Upper position for range trigger (nm)

        Returns:
            None
        '''
        configureRngTrigger(self.device, axisNo, lower, upper)

    def configureRngTriggerEps(self, axisNo: int, epsilon: float) -> None:
        '''
        Configure hysteresis for range Trigger.

        Args:
            axisNo:	    Axis number (0 ... 2)
            epsilon:	hysteresis in nm / mdeg

        Returns:
            None
        '''
        configureRngTriggerEps(self.device, axisNo, epsilon)

    def configureRngTriggerPol(self, axisNo: int, polarity: int):
        '''
        Configure lower position for range Trigger.

        Args:
            axisNo:	    Axis number (0 ... 2)
            polarity:	Polarity of trigger signal when position is between
                        lower and upper low(0) and high(1)
        Returns:
            None
        '''
        configureRngTriggerPol(self.device, axisNo, polarity)

    def connect(self, devNo=0):
        '''
        Initializes and connects the selected device. This has to be done
        before any access to control variables or measured data.

        Args:
            devNo (int):	Sequence number of the device. Must be smaller
                            than the devCount from the last ANC_discover call.
                            Default: 0

        Returns:
            device (ctypes_c_void_p):   Handle to the opened device,
                NULL on error
        '''
        device = ctypes.c_void_p()
        connect(devNo, ctypes.byref(device))
        return device

    def close(self) -> None:
        '''
        Closes the connection to the device. The device handle becomes invalid.

        Args:
            None

        Returns:
            None
        '''
        disconnect(self.device)

    def discover(self, ifaces: int = 3) -> int:
        '''
        The function searches for connected ANC350RES devices on USB
        and LAN and initializes internal data structures per device.
        Devices that are in use by another application or PC are not found.
        The function must be called before connecting to a device and must
        not be called as long as any devices are connected.

        The number of devices found is returned. In subsequent functions,
        devices are identified by a sequence number that must be less than
        the number returned.

        Args:
            ifaces:	Interfaces where devices are to be searched.
                {0 -> None, 1 -> USB, 2 -> ethernet, 3 -> all}

        Returns:
            devCount:	number of devices found
        '''
        devCount = ctypes.c_int()
        discover(ifaces, ctypes.byref(devCount))
        return devCount.value

    def getActuatorName(self, axisNo: int) -> str:
        '''
        Get the name of the currently selected actuator

        Args:
            axisNo:	Axis number (0 ... 2)

        Returns:
            name:	Name of the actuator
        '''
        name = ctypes.create_string_buffer(20)
        getActuatorName(self.device, axisNo, ctypes.byref(name))
        return name.value.decode('utf-8').strip()

    def getActuatorType(self, axisNo: int) -> str:
        '''
        Get the type of the currently selected actuator

        Args:
            axisNo:	Axis number (0 ... 2)
        Returns:
            type:	Type of the actuator {0: linear, 1: goniometer, 2: rotator}
        '''
        type_ = ctypes.c_int()
        getActuatorType(self.device, axisNo, ctypes.byref(type_))
        return {0:'linear', 1:'goniometer', 2:'rotator'}[type_.value]

    def getAmplitude(self, axisNo:int) -> float:
        '''
        Reads back the amplitude parameter of an axis.

        Args:
            axisNo:	    Axis number (0 ... 2)
        Returns:
            amplitude:	Amplitude [V]
        '''
        amplitude = ctypes.c_double()
        getAmplitude(self.device, axisNo, ctypes.byref(amplitude))
        return amplitude.value

    def getAxisStatus(self, axisNo: int) -> tuple:
        '''
        Reads status information about an axis of the device.

        Args:
            axisNo:	Axis number (0 ... 2)

        Returns: (connected, enabled, moving, target, eotFwd, eotBwd, error)
            connected:  If the axis is connected to a sensor.
            enabled:    If the axis voltage output is enabled.
            moving:     If the axis is moving.
            target:     If the target is reached in automatic positioning
            eotFwd:     If end of travel detected in forward direction.
            eotBwd:     If end of travel detected in backward direction.
            error:      If the axis' sensor is in error state.
        '''
        stat_names = ['connected','enabled','moving','target','eotFwd','eotBwd','error']
        connected, enabled = ctypes.c_int(), ctypes.c_int()
        moving = ctypes.c_int()
        target, eotFwd = ctypes.c_int(), ctypes.c_int()
        eotBwd, error = ctypes.c_int(), ctypes.c_int()
        getAxisStatus(self.device, axisNo, ctypes.byref(connected),
                      ctypes.byref(enabled), ctypes.byref(moving),
                      ctypes.byref(target), ctypes.byref(eotFwd),
                      ctypes.byref(eotBwd), ctypes.byref(error))
        stat_values = (bool(connected.value), bool(enabled.value),
            bool(moving.value), bool(target.value), bool(eotFwd.value),
            bool(eotBwd.value), bool(error.value))
        status_dict = {stat: stat_value for stat, stat_value in zip(stat_names,stat_values)}

        return status_dict

    def getDeviceConfig(self) -> dict:
        '''
        Reads static device configuration data

        Args:
            None
        Returns:
            featureSync	"Sync":         Ethernet enabled (1) or disabled (0)
            featureLockin	"Lockin":   Low power loss measurement enabled (1) or disabled (0)
            featureDuty	"Duty":         Duty cycle enabled (1) or disabled (0)
            featureApp	"App":          Control by IOS app enabled (1) or disabled (0)
        '''
        features = ctypes.c_int()
        getDeviceConfig(self.device, features)

        featureSync = {1:'enabled',0:'disabled'}[int(0x01&features.value)]
        featureLockin = {1:'enabled',0:'disabled'}[int((0x02&features.value)/2)]
        featureDuty = {1:'enabled',0:'disabled'}[int((0x04&features.value)/4)]
        featureApp = {1:'enabled',0:'disabled'}[int((0x08&features.value)/8)]

        return {'sync':featureSync, 'lock-in': featureLockin,
                'duty': featureDuty, 'app': featureApp}

    def getDeviceInfo(self, devNo: int = 0) -> dict:
        '''
        Returns: available information about a device.The function cannot be
        called before ANC_discover but the devices don't have to be connected.
        All Pointers to output parameters may be zero to ignore the respective
        value.

        Args:
            devNo:      Sequence number of the device. Must be smaller than the
            devCount:   From the last ANC_discover call. Default: 0
        Returns:
            devType	Output: Type of the ANC350 device.
                            {0: Anc350Res, 1:Anc350Num, 2:Anc350Fps, 3:Anc350None}
            id:             Programmed hardware ID of the device
            serialNo:       The device's serial number. The string buffer should
                            be NULL or at least 16 bytes long.
            address:        The device's interface address if applicable.
                            Returns the IP address in dotted-decimal notation or the string "USB", respectively. The string buffer should be NULL or at least 16 bytes long.
            connected:      If the device is already connected
        '''
        devType = ctypes.c_int()
        id_ = ctypes.c_int()
        serialNo = ctypes.create_string_buffer(16)
        address = ctypes.create_string_buffer(16)
        connected = ctypes.c_int()

        getDeviceInfo(devNo, ctypes.byref(devType), ctypes.byref(id_),
                      ctypes.byref(serialNo), ctypes.byref(address),
                      ctypes.byref(connected))
        return {'devType': devType.value,
                'devID': id_.value,
                'serialNo': serialNo.value.decode('utf-8'),
                'address': address.value.decode('utf-8'),
                'connected': connected.value}

    def getFirmwareVersion(self) -> int:
        '''
        Retrieves the version of currently loaded firmware.

        Args:
            None
        Returns:
            version:    Version number
        '''
        version = ctypes.c_int()
        getFirmwareVersion(self.device, ctypes.byref(version))
        return version.value

    def getFrequency(self, axisNo: int) -> float:
        '''
        Reads back the frequency parameter of an axis.

        Args:
            axisNo:     Axis number (0 ... 2)
        Returns:
            frequency:  Frequency in Hz
        '''
        frequency = ctypes.c_double()
        getFrequency(self.device, axisNo, ctypes.byref(frequency))
        return frequency.value

    def getPosition(self, axisNo: int) -> float:
        '''
        Retrieves the current actuator position in um.

        Args:
            axisNo:     Axis number (0 ... 2)
        Returns:
            position:   Current position [um].
        '''
        position = ctypes.c_double()
        getPosition(self.device, axisNo, ctypes.byref(position))
        return 1e6*position.value

    def getAllPositions(self):
        return self.getPosition(0), self.getPosition(1), self.getPosition(2)

    def measureCapacitance(self, axisNo: int) -> float:
        '''
        Performs a measurement of the capacitance of the piezo motor and
        returns the result. If no motor is connected, the result will be 0.
        The function doesn't return before the measurement is complete;
        this will take a few seconds of time.

        Args:
            axisNo:     Axis number (0 ... 2)
        Returns:
            cap:        Capacitance [uF]
        '''
        cap = ctypes.c_double()
        measureCapacitance(self.device, axisNo, ctypes.byref(cap))
        return 1e6*cap.value

    def saveParams(self):
        '''
        Saves parameters to persistent flash memory in the device.
        They will be present as defaults after the next power-on.
        The following parameters are affected: Amplitude, frequency,
        actuator selections as well as Trigger and quadrature settings.

        Args:
            None
        Returns:
            None
        '''
        saveParams(self.device)

    def selectActuator(self, axisNo: int, actuator: int) -> None:
        '''
        Selects the actuator to be used for the axis from actuator presets.

        Args:
            axisNo:     Axis number (0 ... 2)
            actuator:   Actuator selection (0 ... 255)
                0: ANPg101res
                1: ANGt101res
                2: ANPx51res
                3: ANPx101res
                4: ANPx121res
                5: ANPx122res
                6: ANPz51res
                7: ANPz101res
                8: ANR50res
                9: ANR51res
                10: ANR101res
                11: Test
        Returns:
            None
        '''
        selectActuator(self.device, axisNo, actuator)

    def setAmplitude(self, axisNo: int, amplitude: float) -> None:
        '''
        Sets the amplitude voltage fir the given axis

        Args:
            axisNo      (int):     Axis number (0 ... 2)
            amplitude (float):  Amplitude in V, internal resolution is 1 mV
        Returns:
            None
        '''
        setAmplitude(self.device, axisNo, ctypes.c_double(amplitude))

    def setAxisOutput(self, axisNo: int, enable: int, autoDisable: int):
        '''
        Enables or disables the voltage output of an axis.

        Args:
            axisNo:         Axis number (0 ... 2)
            enable:         Enable (1) or disable (0) the voltage output.
            autoDisable:    If the voltage output is to be deactivated
                            automatically when end of travel is detected.
        Returns:
            None
        '''
        setAxisOutput(self.device, axisNo, enable, autoDisable)

    def setDcVoltage(self, axisNo: int, voltage: float) -> None:
        '''
        Sets the DC level on the voltage output when no sawtooth based motion is active.

        Args:
            axisNo:         Axis number (0 ... 2)
            voltage:    	DC output voltage [V], internal resolution is 1 mV
        Returns:
            None
        '''
        setDcVoltage(self.device, axisNo, ctypes.c_double(voltage))

    def setFrequency(self, axisNo: int, frequency: float) -> None:
        '''
        Sets the frequency parameter for an axis

        Args:
            axisNo:     Axis number (0 ... 2)
            frequency	Frequency [Hz], internal resolution is 1 Hz
        Returns:
            None
        '''
        setFrequency(self.device, axisNo, ctypes.c_double(frequency))

    def setTargetPosition(self, axisNo: int, target_in_um: float) -> None:
        '''
        Sets the target position for automatic motion, see ANC_startAutoMove.
        Target unit is um.

        Args:
            axisNo:     Axis number (0 ... 2)
            target:	    Target position [um]. Internal resulution is 1 nm.

        Returns:
            None
        '''
        assert target_in_um > 0, 'Positioners are unipolar, pos must be > 0.'
        setTargetPosition(self.device, axisNo, ctypes.c_double(target_in_um*1e-6))

    def setTargetRange(self, axisNo: int, targetRg_in_um: float) -> None:
        '''
        Defines the range around the target position where the target is considered to be reached.

        Args:
            axisNo:     Axis number (0 ... 2)
            targetRg	Target range [um]. Internal resulution is 0.001 um.
        Returns:
            None
        '''
        setTargetRange(self.device, axisNo, ctypes.c_double(targetRg_in_um*1e-6))

    def startAutoMove(self, axisNo: int, enable: int, relative: int) -> None:
        '''
        Switches automatic moving (i.e. following the target position) on or off

        Args:
            axisNo:     Axis number (0 ... 2)
            enable:     Enables (1) or disables (0) automatic motion
            relative:   If the target position is to be interpreted absolute
                        (0) or relative to the current position (1)
        Returns:
            None
        '''
        startAutoMove(self.device, axisNo, enable, relative)

    # no real reason to ever use this
    # def startContinuousMove(self, axisNo: int, start: int, backward:int) -> None:
    #     '''
    #     Starts or stops continous motion in the given direction.
    #     Other kinds of motions are stopped.
    #
    #     Args:
    #         axisNo:     Axis number (0 ... 2)
    #         start:      Start (1) or stop (0) motion
    #         backward:   If the move direction is forward (0) or backward (1)
    #
    #     Returns:
    #         None
    #     '''
    #     startContinousMove(self.device, axisNo, start, backward)

    def startSingleStep(self, axisNo: int, backward: int) -> None:
        '''
        Triggers a single step in desired direction.

        Args:
            axisNo:     Axis number (0 ... 2)
            backward:   If the step direction is forward (0) or backward (1)
        Returns:
            None
        '''
        startSingleStep(self.device, axisNo, backward)

    def moveto(self,
               axisNo: int,
               target_position: float,
               target_range: float = 0.1,
               frequency: float = 400.,
               amplitude: float = 45.,
               block: bool = False) -> None:
        '''
        Enable closed-loop motion after settting target position, and target range.
        If the axis is the y-axis, the target has to be <= y_lim

        Args:
            axisNo:             Axis number (0 ... 2)
            target_position:    Target position in um.
            target_range:       Range within which target is considered as reached.
            frequency:          Frequency of operation [Hz]
            amplitude:          Amplitude of operation [V]
            block:              If function blocks until target is reached.
        Returns:
            None
        '''
        if axisNo == 1:
            assert target_position <= self.y_lim, 'y out of range'
        self.setFrequency(axisNo,frequency)
        self.setAmplitude(axisNo,amplitude)
        self.setAxisOutput(axisNo, 1, 1)
        self.setTargetPosition(axisNo, target_position)
        self.setTargetRange(axisNo, target_range)
        self.startAutoMove(axisNo, 1, 0)
        sleep(0.5)
        stuck_gap = 50.
        if block:
            bar_fmt = '{percentage:.1f}%{bar}({n:.1f}/{total:.1f}) [{elapsed}<{remaining}]'
            current_position = self.getPosition(axisNo)
            gap = abs(current_position-target_position)
            pbar = tqdm(total = gap, bar_format = bar_fmt)
            positions = [current_position]
            times = [time()]
            stuck = False
            while (not self.getAxisStatus(axisNo)['target']):
                current_position = self.getPosition(axisNo)
                positions.append(current_position)
                times.append(time())
                dif = abs(target_position - current_position)
                newgap = gap - dif
                pbar.n = newgap
                pbar.display()
                if (len(positions) > 10) & (dif < stuck_gap) & (not stuck):
                    stuck = True
                    print("Stuck?...")
                    stuck_time = time()
                if stuck:
                    ds = abs(positions[-10] - positions[-1])
                    dt = abs(times[-10] - times[-1])
                    speed =  ds / dt
                    time_stuck = time() - stuck_time
                    if (time_stuck > 60) and speed < 1:
                        print("Stuck, stopping Automove ...")
                        self.startAutoMove(axisNo, 0, 0)
                        break
                sleep(0.05)
            pbar.close()

    def disengange_all(self):
        '''
        Disable output on all axes.
        '''
        self.setAxisOutput(0,0,1)
        self.setAxisOutput(1,0,1)
        self.setAxisOutput(2,0,1)

    def voyageto(self, axisNo, target_position, target_precision=0.5, verbose=False):
        '''
        Moves the given axis to the given target position within
        a given precision.
        If the target position is at a larger distance than rough_precision
        the target is initially approached with autoMove,
        once the target is reached within this range, single steps are used
        to get within 3 um,
        after this the DC bias is used to fine tune the position to within
        a precision of target_precision.

        Parameters:

        axisNo              (int): 0 -> x, 1-> y, 2-> z
        target_position   (float): given in um
        target_precision  (float): given in um
        verbose            (bool): if verbose prints or not

        Returns:

        trajectory (list): [positions during mid and fine tuning]

        If at any point the y-axis goes beyond its safe range
        the axis is disengaged.
        If at any time the function is interrupted
        the axis is disengaged.
        '''
        rough_precision = 50 # how close to target with automoving
        mid_range = 3.0 # distance to target for single step approach
        frequency_in_Hz = 200
        mid_amplitude = 30. # voltage amplitude for mid steps
        dc_voltage = 30. # dc voltage for fine tune

        # get close using autoMove
        print("automoving ...")
        self.moveto(axisNo, target_position, rough_precision, block = True)
        self.startAutoMove(axisNo, 0, 0)
        self.setAxisOutput(axisNo, 1, True)
        self.setFrequency(axisNo, frequency_in_Hz)
        self.setDcVoltage(axisNo, dc_voltage)
        trajectory = []

        try:
            # get closer using single steps
            print("mid stepping ...")
            gap = abs(self.getPosition(axisNo) - target_position)
            newgap = gap
            bar_fmt = '{percentage:.1f}%{bar}({n:.1f}/{total:.1f}) [{elapsed}<{remaining}]'
            pbar = tqdm(total = gap, bar_format = bar_fmt)
            while newgap >= mid_range:
                current_position = self.getPosition(axisNo)
                newgap = abs(current_position - target_position)
                pbar.n = gap - newgap
                pbar.display()
                if axisNo == 1:
                    if current_position > self.y_lim:
                        raise Exception("reached y-axis limit")
                trajectory.append(current_position)
                if current_position > target_position:
                    direction = 1 # backward
                else:
                    direction = 0 # forward
                self.setAmplitude(axisNo, mid_amplitude)
                self.startSingleStep(axisNo, direction)
                sleep(0.05)

            print("fine tuning ...")
            # fine tune the DC voltage, and use single steps here and there
            while abs(self.getPosition(axisNo) - target_position) >= target_precision:
                current_position = self.getPosition(axisNo)
                newgap = abs(current_position - target_position)
                pbar.n = gap - newgap
                pbar.display()
                if axisNo == 1:
                    if current_position > self.y_lim:
                        raise Exception("reached y-axis limit")
                if verbose:
                    print(".", end='')
                trajectory.append(current_position)
                if current_position > target_position:
                    dc_voltage = dc_voltage - 1
                else:
                    dc_voltage = dc_voltage + 1
                if dc_voltage < 0:
                    dc_voltage = 30
                    print("leaping")
                    self.startSingleStep(axisNo, 1)
                if dc_voltage > 60:
                    dc_voltage = 30
                    print("leaping")
                    self.startSingleStep(axisNo, 0)
                self.setDcVoltage(axisNo, dc_voltage)
                sleep(0.05)
            pbar.close()
        except Exception as e:
            print(e)
            self.setAxisOutput(axisNo,0,1)
            return trajectory
        return trajectory

    # def travelto(self, axisNo, target_position, target_precision = 0.5):
    #     '''
    #     Moves the given axis to the given target position within
    #     a given precision by using a mixture of continous motions
    #     and single steps. Fine-stepping is regulated by changing
    #     the single-step voltage accordingly.
    #
    #     Parameters:
    #
    #     axisNo              (int): 0 -> x, 1-> y, 2-> z
    #     target_position   (float): given in um
    #     target_precision  (float): given in um
    #
    #     Retruns:
    #
    #     trajectory (list): [[step_idx_0, position_0] ... []]
    #
    #     If at any point the axis goes beyond its safe range
    #     motion is immediately stopped.
    #     If at any time the function is interrupted
    #     the axis is stopped.
    #     '''
    #     big_range = 3000./2. # distance to target that enforces continous motion
    #     mid_range = 20./2. # distance to target that enforces single steps
    #     fine_range = 5./2. # distance to target that hones in using DC voltage
    #     max_voltage = 60 # this is the maximum voltage that can be set
    #     dc_voltage = 0. # this is the starting voltage for fine stepping
    #     frequency_in_Hz = 200
    #     min_coarse = 20 # for big stepping voltage shan't be smaller than this
    #     dc_delta = 1 # initial step size for finding fine step voltage
    #     coarse_amplitude = 50.
    #     coarse_delta = 1 # amount by which the continouse motion is increased/decreased
    #     current_position = self.getPosition(axisNo)
    #     delta = self.getPosition(axisNo) - target_position
    #     previous_position = current_position
    #     self.setAxisOutput(axisNo, 1, True)
    #     self.setFrequency(axisNo, frequency_in_Hz)
    #     start_time = time.time()
    #     trajectory = []
    #     try:
    #         while abs(delta) >= target_precision:
    #             current_position = self.getPosition(axisNo)
    #             trajectory.append([time.time()-start_time, current_position])
    #             if ((-fine_range) < (current_position-target_position) < 0) : # target must be approached from below
    #                 print("fine stepping...", end='|')
    #                 if dc_voltage >= max_voltage:
    #                     dc_voltage = 0
    #                     print("mid stepping out of snag...", end='|')
    #                     if current_position > target_position:
    #                         direction = 1 # backward
    #                     else:
    #                         direction = 0 # forward
    #                     self.setAmplitude(axisNo, coarse_amplitude)
    #                     self.startSingleStep(axisNo,direction)
    #                     if (target_position-current_position)*(target_position-self.getPosition(axisNo)) < 0:
    #                         coarse_amplitude = coarse_amplitude - coarse_delta
    #                         if coarse_amplitude < min_coarse:
    #                             coarse_amplitude = min_coarse
    #                 self.setDcVoltage(axisNo,dc_voltage)
    #                 # fine tuning mode
    #                 if (previous_position - target_position)*(current_position - target_position) < 0:
    #                     dc_delta = dc_delta/2.
    #                 if current_position > target_position:
    #                     dc_voltage = abs(dc_voltage - dc_delta)
    #                     self.setDcVoltage(axisNo, dc_voltage)
    #                     # print("V="+str(dc_voltage))
    #                 else:
    #                     dc_voltage = dc_voltage + dc_delta
    #                     self.setDcVoltage(axisNo, dc_voltage)
    #                     # print("V="+str(dc_voltage))
    #             elif abs(current_position-target_position) <= mid_range:
    #                 print("mid stepping...", end='|')
    #                 if current_position > target_position:
    #                     direction = 1 # backward
    #                 else:
    #                     direction = 0 # forward
    #                 self.setAmplitude(axisNo, coarse_amplitude)
    #                 self.startSingleStep(axisNo,direction)
    #                 if (target_position-current_position)*(target_position-self.getPosition(axisNo)) < 0:
    #                     coarse_amplitude = coarse_amplitude - coarse_delta
    #                     if coarse_amplitude < min_coarse:
    #                         coarse_amplitude = min_coarse
    #             elif abs(current_position-target_position) <= big_range:
    #                 # if very far away, approach target with
    #                 # a continous move using the coarse_amplitied voltage
    #                 print("big stepping...", end='|')
    #                 self.setAmplitude(axisNo, coarse_amplitude)
    #                 if current_position > target_position:
    #                     direction = 1 # backward
    #                 else:
    #                     direction = 0 # forward
    #                 self.startContinuousMove(axisNo,1,direction)
    #                 while (target_position-current_position)*(target_position-self.getPosition(axisNo)) > 0:
    #                     # keep moving until the target has been crossed
    #                     pass
    #                 else:
    #                     coarse_amplitude = coarse_amplitude - coarse_delta
    #                     if coarse_amplitude < min_coarse:
    #                         coarse_amplitude = min_coarse
    #                 self.startContinuousMove(axisNo,0,direction)
    #             previous_position = current_position
    #             delta = current_position - target_position
    #             time.sleep(0.1)
    #         else:
    #             print("Target reached!")
    #         if abs(self.getPosition(axisNo) - target_position) > target_precision:
    #             print("Repeating...")
    #             self.travelto(axisNo, target_position)
    #     except:
    #         print("stopping the axis")
    #         self.startContinuousMove(axisNo,0,direction)
    #         return trajectory
    #     return trajectory
