#!/usr/bin/python3

import tkinter as tk
import matplotlib, time, sys
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np
import ctypes
import statistics

def getcounts():
    cr0, cr1 = getcountrate(0), getcountrate(1)
    now = float(time.time())
    return [now, cr0, cr1, cr0+cr1]

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        self.dt = 150 # refresh time interval in miliseconds
        self.start_time = float(time.time())
        self.times = []
        self.max = tk.IntVar()
        self.max.set(0)
        self.ch0counts = []
        self.ch1counts = []
        self.ch2counts = []
        self.update_data()
        tk.Frame.__init__(self, master, **kwargs)
        self.running = True
        self.ani = None

        self.varCH0 = tk.BooleanVar()
        self.varCH0.set(True)
        self.varCH1 = tk.BooleanVar()
        self.varCH1.set(True)
        self.varCH2 = tk.BooleanVar()
        self.varCH2.set(True)

        self.timewindow = tk.DoubleVar() # in minutes
        self.timewindow.set(0.5)

        plt.style.use('dark_background')
        self.fig = plt.Figure(figsize=(16,8.2))
        self.ax1 = self.fig.add_subplot(111)

        if self.varCH0.get():
            self.line0, = self.ax1.plot(self.times, self.ch0counts, 'b-', lw=2)
        if self.varCH1.get():
            self.line1, = self.ax1.plot(self.times, self.ch1counts, 'r-', lw=2)
        if self.varCH2.get():
            self.line2, = self.ax1.plot(self.times, self.ch2counts, 'w-', lw=2)
        self.text = self.ax1.text(0.025, 0.1,' ',
                                 horizontalalignment='left',
                                 verticalalignment='center',
                                 transform = self.ax1.transAxes)
        self.ax1.set_xlabel('t/s')
        self.ax1.set_ylabel('count rate / cps')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        btns = tk.Frame(self)
        btns.pack(pady=(0,50))
        btns.configure(bg = 'black')
        self.CH0box = tk.Checkbutton(btns, text='CH0', variable = self.varCH0,
                                    onvalue = True, offvalue = False,
                                    command = self.linemngr,
                                    fg = 'white',
                                    bg = 'black',
                                    selectcolor='black')
        self.CH0box.pack(side=tk.LEFT)
        self.CH1box = tk.Checkbutton(btns, text='CH1', variable = self.varCH1,
                                    onvalue = True, offvalue = False,
                                    command = self.linemngr,
                                    fg = 'white',
                                    bg = 'black',
                                    selectcolor='black')
        self.CH1box.pack(side=tk.LEFT)
        self.CH1box.configure(bg='black')

        self.CH2box = tk.Checkbutton(btns, text='CH0+CH1', variable = self.varCH2,
                                    onvalue = True, offvalue = False,
                                    command = self.linemngr,
                                    fg = 'white',
                                    bg = 'black',
                                    selectcolor='black')
        self.CH2box.pack(side=tk.LEFT)

        self.alabel = tk.Label(btns, text='Viewing window/min : ', fg='white', bg='black')
        self.alabel.pack(side=tk.LEFT)

        self.timewindowbox = tk.Scale(btns, variable = self.timewindow,
                            from_ = 0.1, to = 30, resolution = 0.1,
                            length = 200, orient = tk.HORIZONTAL, fg='white', bg='black')
        self.timewindowbox.pack(side=tk.LEFT)

        self.btn = tk.Button(btns, text='Start', command=self.on_click, width=15)
        self.btn.pack(side=tk.LEFT, padx=5)

        self.start()

    def linemngr(self):
        if self.varCH0.get():
            self.line0, = self.ax1.plot(self.times, self.ch0counts, 'b-', lw=2)
        if self.varCH1.get():
            self.line1, = self.ax1.plot(self.times, self.ch1counts, 'r-', lw=2)
        if self.varCH2.get():
            self.line2, = self.ax1.plot(self.times, self.ch2counts, 'w-', lw=2)

    def update_data(self):
        t, c0, c1, c2 = getcounts()
        self.times.append(t-self.start_time)
        self.ch0counts.append(c0)
        self.ch1counts.append(c1)
        self.ch2counts.append(c2)

    def on_click(self):
        '''the button is a start, pause and unpause button all in one
        this method sorts out which of those actions to take'''
        if self.ani is None:
            # animation is not running; start it
            return self.start()
        if self.running:
            # animation is running; pause it
            print("pausing")
            self.ani.event_source.stop()
            self.btn.config(text='Resume')
        else:
            # animation is paused; unpause it
            self.ani.event_source.start()
            self.btn.config(text='Pause')
        self.running = not self.running

    def start(self):
        frames = 1000000
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_graph,
            frames=frames,
            interval=self.dt, # refresh period in ms
            repeat=False,
            blit=False)
        self.running = True
        self.btn.config(text='Pause')
        self.ani._start()
        print('started animation')

    def update_graph(self, i):
        self.update_data()
        title = ''
        lines = []
        max_counts = 0
        viewing_indices = int((self.timewindow.get()*60) * len(self.times) / self.times[-1] )
        viewing_indices = min(viewing_indices, len(self.times))
        info_lines = []
        if self.varCH0.get():
            self.line0.set_data(self.times, self.ch0counts)
            max_counts = max(max_counts, max(self.ch0counts[-viewing_indices:]))
            lines.append(self.line0)
            stdev = statistics.pstdev(self.ch0counts[-viewing_indices:])
            mean = statistics.mean(self.ch0counts[-viewing_indices:])
            info_lines.append(r'CH0 : $%d \pm %d$' % (mean, stdev))
            title = title + (' CH0 = %d ' % self.ch0counts[-1])
        if self.varCH1.get():
            self.line1.set_data(self.times, self.ch1counts)
            max_counts = max(max_counts, max(self.ch1counts[-viewing_indices:]))
            lines.append(self.line1)
            stdev = statistics.pstdev(self.ch1counts[-viewing_indices:])
            mean = statistics.mean(self.ch1counts[-viewing_indices:])
            info_lines.append(r'CH1 : $%d \pm %d$' % (mean, stdev))
            title = title + (' CH1 = %d ' % self.ch1counts[-1])
        if self.varCH2.get():
            self.line2.set_data(self.times, self.ch2counts)
            max_counts = max(max_counts, max(self.ch2counts[-viewing_indices:]))
            lines.append(self.line2)
            stdev = statistics.pstdev(self.ch2counts[-viewing_indices:])
            mean = statistics.mean(self.ch2counts[-viewing_indices:])
            info_lines.append(r'CH1 + CH2 : $%d \pm %d$' % (mean, stdev))
            title = title + (' CH0+CH1 = %d ' % self.ch2counts[-1])
        info_text = '\n'.join(info_lines+['\n'])
        self.text.set_text(info_text)
        lines.append(self.text)
        self.max.set(max_counts)
        self.ax1.set_ylim(0.,1.1*max_counts)
        mintime = max(0, self.times[-1] - 60*self.timewindow.get())
        self.ax1.set_xlim(mintime, self.times[-1])
        self.ax1.set_title(title,fontsize=40)
        return lines

MAXDEVNUM = 8
errorString = ctypes.create_string_buffer(b"", 40)
phlib = ctypes.CDLL("phlib64.dll")
libVersion = ctypes.create_string_buffer(b"", 8)
countRate0 = ctypes.c_int()
countRate1 = ctypes.c_int()
hwSerial = ctypes.create_string_buffer(b"", 8)
dev = []

def closeDevices():
    for i in range(0, MAXDEVNUM):
        phlib.PH_CloseDevice(ctypes.c_int(i))

def getcountrate(channel):
    if channel==0:
        phlib.PH_GetCountRate(ctypes.c_int(dev[0]), ctypes.c_int(channel), ctypes.byref(countRate0))
        return countRate0.value
    if channel==1:
        phlib.PH_GetCountRate(ctypes.c_int(dev[0]), ctypes.c_int(channel), ctypes.byref(countRate1))
        return countRate1.value
    else:
        return "Invalid channel"

# initialize picoHarp
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
print("\nInitializing picoHarp...")
mode = 2
phlib.PH_Initialize(ctypes.c_int(dev[0]), ctypes.c_int(mode))

root = tk.Tk()
root.title('picoHarp')
# root.resizable(height = None, width = None)
app = App(root)
app.pack()
app.configure(bg='black')
root.mainloop()
