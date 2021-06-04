
# modified from https://picamera.readthedocs.io/en/release-1.13/recipes2.html
# so that it simply serves the video feed to be seen with VLC
# feed can be found at <PI IP>:8000
# David, June 2021

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from fractions import Fraction
import time
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import datetime as dt

# for other resolutions see
# https://picamera.readthedocs.io/en/release-1.12/fov.html
resolution = (640,480)
frate = Fraction(5,1)
grid_spacing = 52 # how many pixels to a mm
iso = 1600
exp_mode = 'night'
font = ImageFont.truetype("/usr/share/fonts/truetype/inconsolata/Inconsolata.otf", 18)
color = 'rgb(255,255,255)' # for test info overlay on stream
#bar = Image.open("scale_bar.png").convert('RGBA')

dot_color = (255,255,255,100)

image_width, image_height = resolution
s = 2
bar = Image.new(mode='RGBA', size=(image_width,image_height), color=(0,0,0,0))
draw = ImageDraw.Draw(bar)
num_v = int(image_height/grid_spacing)
num_h = int(image_width/grid_spacing)
pad_h = (image_width - num_h*grid_spacing)/2
pad_v = (image_height - num_v*grid_spacing)/2
for i in range(num_h+1):
    for j in range(num_v+1):
        x, y = i*grid_spacing + pad_h, j*grid_spacing+pad_v
        line = ((x-s,y), (x+s, y))
        draw.line(line, fill=dot_color)
        line = ((x,y-s), (x, y+s))
        draw.line(line, fill=dot_color)
margin = ((pad_h,pad_v),
          (image_width-pad_h,pad_v),
          (image_width-pad_h,image_height-pad_v),
          (pad_h,image_height-pad_v),(pad_h,pad_v))
draw.line(margin, fill=(255,255,255,255), width=1)

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)



class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/stream.mjpg')
            self.end_headers()
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                        # now add timestamp to jpeg
                        # Convert to PIL Image
                        cv2.CV_LOAD_IMAGE_COLOR = 1 # set flag to 1 to give colour image
                        npframe = np.frombuffer(frame, dtype=np.uint8)
                        pil_frame = cv2.imdecode(npframe,cv2.CV_LOAD_IMAGE_COLOR)
                        cv2_im_rgb = cv2.cvtColor(pil_frame, cv2.COLOR_BGR2RGB)
                        pil_im = Image.fromarray(cv2_im_rgb)

                        draw = ImageDraw.Draw(pil_im)
                        infotext = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        # Draw the text

                        # get text size
                        text_size = font.getsize(infotext)

                        # set button size + 10px margins
                        frame_size = (text_size[0]+20, text_size[1]+10)

                        # create image with correct size and black background
                        frame_img = Image.new('RGBA', frame_size, "black")
                        
                        # put text on button with 10px margins
                        frame_draw = ImageDraw.Draw(frame_img)
                        frame_draw.text((10, 5), infotext, fill = color, font=font)

                        # put overlay on source image in position (0, 0)
                        pil_im.paste(frame_img, (int((640-frame_size[0])/2), int(1.5*pad_v)))
                        pil_im.paste(bar,(0,0), bar)

                        # Save the image
                        buf = io.BytesIO()
                        pil_im.save(buf, format= 'JPEG')
                        frame = buf.getvalue()
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera() as camera:
    camera.resolution = resolution
    camera.framerate = frate
    camera.iso = iso
    camera.exposure_mode = exp_mode
    camera.shutter_speed = int(1/camera.framerate*1e6) # in microseconds
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        counter = 0
        server.serve_forever()
    finally:
        camera.stop_recording()
