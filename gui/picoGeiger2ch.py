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
mode=2
phlib.PH_Initialize(ctypes.c_int(dev[0]), ctypes.c_int(mode))

#print("Plot shows moving average, title shows current counts.")

num_elements=1000
counts0=[0]*num_elements
counts1=[0]*num_elements
latency_time=0.

timefmt="time elapsed = %.2f min"
titlefmt="CH0=%d, CH1=%d"

fig, ax = plt.subplots()
initial_counts0,initial_counts1=getcountrates()
max_counts0, max_counts1 = initial_counts0, initial_counts1
max_counts=max(max_counts0,max_counts1)
ax.set_title(titlefmt % (initial_counts0,initial_counts1),fontsize=40)
times = list(np.linspace(0, num_elements, num_elements))
#line1, = ax.plot(times,counts,alpha=0.4)
line_ch0, = ax.plot(times,counts0)
line_ch1, = ax.plot(times,counts1)
#line5, = ax.plot([0,num_elements],[initial_counts]*2,'r--')
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
    #line1.set_ydata(counts)  # update the data
    #counts_array=np.array(counts)
    # do a moving average
    #N=20
    #avg_counts=np.convolve(counts_array, np.ones((N,))/N, mode='valid')
    #avg_counts=list(avg_counts)
    #avg_counts=[avg_counts[0]]*(N-1)+avg_counts

    line_ch0.set_ydata(counts0)
    line_ch1.set_ydata(counts1)

    annotation.set_text(timefmt % ((time.time()-start_time)/60.))
    max_counts0=max(max(counts0),max_counts0)
    max_counts1=max(max(counts1),max_counts1)
    max_counts=max(max(counts0),max(counts1),max_counts0,max_counts1)
    ax.set_ylim(0,max_counts)
    ax.set_xlim(0,num_elements*1.05)
    ax.set_title(titlefmt % (counts0[-1],counts1[-1]),fontsize=40)
    time.sleep(latency_time)
    #ax.annotate(current_counts,xy=(0.5,0.9),xycoords='axes fraction')


    return line_ch0,line_ch1,annotation#,line5


ani = animation.FuncAnimation(fig, animate, np.arange(1, 200),
                              interval=10, blit=False)
plt.show()
print("Closing picoHarp ...")
closeDevices()
