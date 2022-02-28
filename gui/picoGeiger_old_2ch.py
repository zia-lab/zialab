#!/usr/bin/env python3

import time
import ctypes
import struct
from ctypes import byref, POINTER
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

MAXDEVNUM = 8
errorString = ctypes.create_string_buffer(b"", 40)
phlib = ctypes.CDLL("phlib64.dll")
libVersion = ctypes.create_string_buffer(b"", 8)
countRate0 = ctypes.c_int()
countRate1 = ctypes.c_int()
hwSerial = ctypes.create_string_buffer(b"", 8)
dev = []

global counts
global times

def closeDevices():
    for i in range(0, MAXDEVNUM):
        phlib.PH_CloseDevice(ctypes.c_int(i))

def getcountrate(channel):
    if channel==0:
        phlib.PH_GetCountRate(ctypes.c_int(dev[0]), ctypes.c_int(channel), byref(countRate0))
        return countRate0.value
    if channel==1:
        phlib.PH_GetCountRate(ctypes.c_int(dev[0]), ctypes.c_int(channel), byref(countRate1))
        return countRate1.value
    else:
        return "Invalid channel"

def getcountrates():
    return getcountrate(0), getcountrate(1)

for i in range(0, MAXDEVNUM):
    retcode = phlib.PH_OpenDevice(ctypes.c_int(i), hwSerial)
    if retcode == 0:
        print("  %1d        S/N %s" % (i, hwSerial.value.decode("utf-8")))
        dev.append(i)
    else:
        if retcode == -1: # ERROR_DEVICE_OPEN_FAIL
            print("  %1d        no device" % i)
        else:
            phlib.PH_GetErrorString(errorString, ctypes.c_int(retcode))
            print("  %1d        %s" % (i, errorString.value.decode("utf8")))

if len(dev) < 1:
    print("No device available.")
    closeDevices()
print("Using device #%1d" % dev[0])
print("\nInitializing the device...")
mode = 2
phlib.PH_Initialize(ctypes.c_int(dev[0]), ctypes.c_int(mode))

num_elements = 1000
counts0 = [0]*num_elements
counts1 = [0]*num_elements
latency_time = 0.

timefmt = "time elapsed = %.2f min"
titlefmt = "CH0=%s | CH1=%s"

fig, ax = plt.subplots(figsize=(10,5))
initial_counts0, initial_counts1 = getcountrates()
max_counts0, max_counts1 = initial_counts0, initial_counts1
max_counts = max(max_counts0,max_counts1)
ax.set_title(titlefmt % (initial_counts0,initial_counts1),fontsize=40)
times = list(np.linspace(0, num_elements, num_elements))
line_ch0, = ax.plot(times,counts0, label='CH0')
line_ch1, = ax.plot(times,counts1, label='CH1')
ax.set_xlim(0,num_elements)
plt.legend(loc='lower left')
plt.tight_layout()
global start_time
start_time=time.time()

annotation = ax.annotate(timefmt % (0), xy=(0.01,0.95),xycoords='axes fraction',ha='left')

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def animate(i):
    global counts0
    global counts1
    global max_counts1
    global max_counts0
    current_counts=getcountrates()
    counts0.pop(0) # pop one out
    counts0.append(current_counts[0]) # put one in
    counts1.pop(1) # pop one out
    counts1.append(current_counts[1]) # put one in
    try:
        counts0 = counts0[-num_elements:]
        counts1 = counts1[-num_elements:]
    except:
        pass

    line_ch0.set_ydata(counts0)
    line_ch1.set_ydata(counts1)

    annotation.set_text(timefmt % ((time.time()-start_time)/60.))
    max_counts0 = max(max(counts0),max_counts0)
    max_counts1 = max(max(counts1),max_counts1)
    max_counts = max(max(counts0),max(counts1),max_counts0,max_counts1) # max to the all-time max
    max_counts = max(max(counts0),max(counts1)) # max of just the current view
    ax.set_ylim(0,max_counts)
    ax.set_xlim(0,num_elements*1.01)
    cr1 = str(counts0[-1]).zfill(5)
    cr2 = str(counts1[-1]).zfill(5)
    ax.set_title(titlefmt % (cr1, cr2),fontsize=40)
    time.sleep(latency_time)
    #ax.annotate(current_counts,xy=(0.5,0.9),xycoords='axes fraction')

    return line_ch0, line_ch1, annotation


ani = animation.FuncAnimation(fig, animate, np.arange(1, 200),
                              interval=10, blit=False)
plt.show()
print("Closing picoHarp ...")
closeDevices()
