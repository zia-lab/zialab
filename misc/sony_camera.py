#!/usr/bin/env python3

import glob
import os
import win32com

# worked alright in a notebook
# code pasted here hastily
# perhaps will not work inmmediately

class SonyCam():
    def __init__(self):
        self.device = "Sony alpha-6000"
        self.photos_dir = 'C:\\Users\\lab_pc_v\\Desktop\\Photos'
        self.shell = win32com.client.Dispatch("WScript.Shell")
    def get_latest_photo_fname(self):
        '''
        Returns the filename of the most recent JPG file in the given directory.
        '''
        if( os.path.exists(self.photos_dir)):
            files = glob.glob(self.photos_dir +'/*.JPG')
            last_jpeg = max(files, key=os.path.getctime)
        else:
            print("no such dir...")
        last_jpeg = os.path.split(last_jpeg)
        return {'dir': last_jpeg[0], 'fname': last_jpeg[1]}
    def grab_photo(self):
        '''Snap a photo, wait for it to be acquired
        and return the resulting filename.
        '''
        num_photos = len(os.listdir(self.photos_dir))
        self.shell.AppActivate('Remote')
        time.sleep(0.5)
        self.shell.SendKeys("1", 0)
        while len(os.listdir(self.photos_dir)) == num_photos:
            time.sleep(0.1)
        return get_latest_photo_fname(self.photos_dir)['fname']
