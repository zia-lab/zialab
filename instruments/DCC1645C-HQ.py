%pylab inline
from PIL import Image, ImageOps
from io import BytesIO
import IPython.display
import time
from IPython.display import clear_output
from instrumental import instrument, list_instruments

paramsets = list_instruments()
for index, paramset in enumerate(paramsets):
    print(index,paramset['classname'])

thorcam = instrument(paramsets[0])
thorcam.set_auto_exposure(True)

def showarray(a, fmt='jpeg'):
    f = BytesIO()
    ImageOps.autocontrast(Image.fromarray(a)).save(f, fmt)
    IPython.display.display(IPython.display.Image(data=f.getvalue()))

try:
    while(True):
        # Capture frame-by-frame
        t1 = time.time()
        #thorcam.wait_for_frame()
        frame = thorcam.grab_image()
        # Convert the image from OpenCV BGR format to matplotlib RGB format
        # to display the image
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        showarray(frame)
        t2 = time.time()
        print("%.1f FPS" % (1/(t2-t1)))
        # Display the frame until new frame is available
        clear_output(wait=True)
except KeyboardInterrupt:
    #thorcam.stop_live_video()
    print("ThorCAM stopped")
