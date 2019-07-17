try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

import numpy as np
import time

import requests

global shutter
global power

import requests
VERDI_PI_IP='128.148.54.172'
def verdi_set_shutter(shutter):
    '''
    Open (1) or close (0) the shutter. Function returns the queried state of
    the shutter right after being set.
    '''
    return int(requests.get('http://%s:7777/setverdi/shutter?shutter=%d'%(VERDI_PI_IP,shutter)).content)

def verdi_get_shutter():
    '''
    Open (1) or close (0) the shutter. Function returns the queried state of
    the shutter right after being set.
    '''
    return int(requests.get('http://%s:7777/qverdi/shutter'%(VERDI_PI_IP)).content)

def verdi_set_power(power):
    '''
    Set the power of Verdi in W. Function returns the power queried on the
    Verdi after being set.
    '''
    return float(requests.get('http://%s:7777/setverdi/power?power=%f'%(VERDI_PI_IP,power)).content)
def verdi_get_calpower():
    '''
    Get the calibrated power in W.
    '''
    return float(requests.get('http://%s:7777/qverdi/calpower'%VERDI_PI_IP).content)
def verdi_get_regpower():
    '''
    Get the regulated power in W.
    '''
    return float(requests.get('http://%s:7777/qverdi/regpower'%VERDI_PI_IP).content)

def toggle():

    if toggle_btn.config('text')[-1] == 'Shutter is open':
        verdi_set_shutter(0)
        toggle_btn.config(text="Shutter is closed")
    else:
        verdi_set_shutter(1)
        toggle_btn.config(text="Shutter is open")
    time.sleep(0.2)

def change_power(x):
    verdi_set_power(float(entry_field.get()))
    power_display.config(text='{0:.4f} W'.format(verdi_get_regpower()))
    return None

def increasepower():
    increment = increment_field.get()
    verdi_set_power(verdi_get_regpower()+float(increment))
    increment_field.config(text=increment)
    time.sleep(0.2)
    power_display.config(text='{0:.4f} W'.format(verdi_get_regpower()))
    return None

def decreasepower():
    verdi_set_power(verdi_get_regpower()-float(increment_field.get()))
    time.sleep(0.2)
    power_display.config(text='{0:.4f} W'.format(verdi_get_regpower()))
    return None

def resetIP(x):
    global VERDI_PI_IP
    VERDI_PI_IP = ip_field.get()

root = tk.Tk()

root.title("Verdi")
root.resizable(False, False)

title = tk.Label(text='++++')
title.grid(row=0,column=1)

power_display = tk.Label(root,text='{0:.4f} W'.format(verdi_get_regpower()),font=('Courier New',40))
power_display.grid(row=1,column=0,columnspan=3)

entry_field_left = tk.Label(text='Set')
entry_field_left.grid(row=2,column=0)

entry_field = tk.Entry(root,justify='center')
#entry_field.insert(0,'set power in W')
entry_field.bind('<Return>',change_power)
entry_field.grid(row=2,column=1,columnspan=1)

entry_field_right = tk.Label(text='W')
entry_field_right.grid(row=2,column=2)

left_increment_btn = tk.Button(root,text="↓", command =  decreasepower)
left_increment_btn.grid(row=3,column=0)

increment_field = tk.Entry(root,justify='center')
increment_field.insert(0,'0.01')
increment_field.grid(row=3,column=1)

left_increment_btn = tk.Button(root,text="↑", command =  increasepower)
left_increment_btn.grid(row=3,column=2)


toggle_btn = tk.Button(root,text="", width=12, command=toggle)
if verdi_get_shutter == 1:
    toggle_btn.config(text='Shutter is open')
else:
    toggle_btn.config(text='Shutter is closed')

toggle_btn.grid(row=4,column=1)

ip_field = tk.Entry(root,justify='center')
ip_field.insert(0,VERDI_PI_IP)
ip_field.bind('<Return>',resetIP)
ip_field.grid(row=5,column=1)

bottom = tk.Label(text='++++')
bottom.grid(row=6,column=1)

root.mainloop()
