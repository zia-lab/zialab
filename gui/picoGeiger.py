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
        phlib.PH_GetCountRate(ctypes.c_int(dev[0]), ctypes.c_int(channel), byref(countRate0))
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
mode=2
phlib.PH_Initialize(ctypes.c_int(dev[0]), ctypes.c_int(mode))


print("Plot shows moving average, title shows current counts.")

#def getcountrate():
#    return np.random.random()
global ax
global max_counts

num_elements=1000
counts=[0]*num_elements
avg_counts=[0]*num_elements
latency_time=0.

timefmt="time elapsed = %.2f min"
titlefmt="%d, max=%d, average = %d"

fig, ax = plt.subplots(figsize=(10,5))
initial_counts=getcountrate(0)
max_counts=initial_counts
ax.set_title(titlefmt % (initial_counts,initial_counts,initial_counts),fontsize=40)
times = list(np.linspace(0, num_elements, num_elements))
line1, = ax.plot(times,counts,'b-')
line2, = ax.plot(times,avg_counts,'b--',alpha=0.4)
line3, = ax.plot([times[-1]],[initial_counts],'ro',ms=4)
line4, = ax.plot([0,num_elements],[initial_counts]*2,'k--')
#line5, = ax.plot([0,num_elements],[initial_counts]*2,'r--')
global start_time
start_time=time.time()
plt.tight_layout()

annotation = ax.annotate(timefmt % (0), xy=(0.01,0.95),xycoords='axes fraction',ha='left')


def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def animate(i):
    global counts
    global max_counts
    current_counts=getcountrate(0)
    counts.pop(0) # pop one out
    counts.append(current_counts) # put one in
    try:
        counts = counts[-num_elements:]
    except:
        pass
    line1.set_ydata(counts)  # update the data
    counts_array=np.array(counts)
    # do a moving average
    N=20
    avg_counts=np.convolve(counts_array, np.ones((N,))/N, mode='valid')
    avg_counts=list(avg_counts)
    avg_counts=[avg_counts[0]]*(N-1)+avg_counts
    line2.set_ydata(avg_counts)
    #line4.set_ydata([np.mean(counts_array[:int(num_elements*0.2)])]*2)
    line4.set_ydata([avg_counts[-1]]*2)
    #line5.set_ydata([np.mean(counts_array[-int(num_elements*0.2):])]*2)
    annotation.set_text(timefmt % ((time.time()-start_time)/60.))

    max_counts=max(max(avg_counts),max_counts)
    ax.set_ylim(0,max_counts)
    ax.set_xlim(0,num_elements*1.05)
    ax.set_title(titlefmt % (current_counts,max_counts,sum(counts)/len(counts)),fontsize=30)
    time.sleep(latency_time)
    #ax.annotate(current_counts,xy=(0.5,0.9),xycoords='axes fraction')

    line3.set_ydata([avg_counts[-1]])
    return line2,annotation,line3,line4#,line5


ani = animation.FuncAnimation(fig, animate, np.arange(1, 200),
                              interval=10, blit=False)
plt.show()
print("Closing picoHarp ...")
closeDevices()
