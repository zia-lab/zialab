# Import the .NET class library
import clr, ctypes
# Import python sys module
import sys, os
# Import c compatible List and String
from System import *
from System.Collections.Generic import List
from System.Runtime.InteropServices import Marshal
from System.Runtime.InteropServices import GCHandle, GCHandleType

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import *
from PrincetonInstruments.LightField.AddIns import *

# Create the LightField Application (true for visible)
# The 2nd parameter forces LF to load with no experiment
automat = Automation(True, List[String]())
# Get LightField Application object
application = automat.LightFieldApplication
# Get experiment object
experiment = application.Experiment

def validate_camera():
    camera = None
    # Find connected device
    for device in experiment.ExperimentDevices:
        if (device.Type == DeviceType.Camera & experiment.IsReadyToRun):
            camera = device
    if (camera == None):
        print("This sample requires a camera.")
        return False
    if (not experiment.IsReadyToRun):
        print("The system is not ready for acquisition, is there an error?")
    return True

# Creates a numpy array from our acquired buffer
def convert_buffer(net_array, image_format):
    src_hndl = GCHandle.Alloc(net_array, GCHandleType.Pinned)
    try:
        src_ptr = src_hndl.AddrOfPinnedObject().ToInt64()

        # Possible data types returned from acquisition
        if (image_format==ImageDataFormat.MonochromeUnsigned16):
            buf_type = ctypes.c_ushort*len(net_array)
        elif (image_format==ImageDataFormat.MonochromeUnsigned32):
            buf_type = ctypes.c_uint*len(net_array)
        elif (image_format==ImageDataFormat.MonochromeFloating32):
            buf_type = ctypes.c_float*len(net_array)

        cbuf = buf_type.from_address(src_ptr)
        resultArray = np.frombuffer(cbuf, dtype=cbuf._type_)

    # Free the handle
    finally:
        if src_hndl.IsAllocated: src_hndl.Free()

    # Make a copy of the buffer
    return np.copy(resultArray)

exposures = np.linspace(0,200,21)
frames = []
sensor_size = (1024,1024)
for exposure in exposures:
    experiment.SetValue(CameraSettings.ShutterTimingExposureTime, int(exposure))
    experiment.SetValue(ExperimentSettings.AcquisitionFramesToStore, 1)
    dataset = experiment.Capture(1)
    image_data = dataset.GetFrame(0, 0).GetData()
    image_frame = dataset.GetFrame(0,0)
    frame = convert_buffer(dataset.GetFrame(0,0).GetData(), dataset.GetFrame(0,0).Format).reshape(sensor_size)
    frames.append(frame)
