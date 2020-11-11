#!/usr/bin/python3

'''Optical power plot.

    Usage : voltmeterGUI.py num_minutes fig_width fig_height

    Makes a continously updating plot of the voltage registered
    by the photodiode at the input port of the microscope. Three
    optional parameters may be given, but if either fig_width or
    fig_height are given, then all the other ones must also be given.

    This script is meant to run locally on the Raspberry Pi attached to the
    photodiode, where the records table is stored.

    This was coded in Nov 2020 by David.

'''

import tkinter as tk
import matplotlib, time, subprocess, sys
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np

log_fname = '/home/pi/Log/volt.log'

def getcounts(num_recs, skip):
    result = subprocess.run(['tail','-n%s' % num_recs,log_fname],
                            stdout=subprocess.PIPE)
    data = result.stdout.decode().split('\n')[::-int(skip)][1:]
    data = np.array([list(map(float,l.split(','))) for l in data])
    return data

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        self.dt = 2 # time resolution of records table, in seconds
        self.units = {'sec':1, 'min':60, 'hr': 3600, 'day': 3600*24}
        if len(sys.argv) > 1:
            self.num_mins = int(sys.argv[1])
        else:
            self.num_mins = 60
        if self.num_mins <= 1:
            self.time_unit = 'sec'
        elif self.num_mins <= 60:
            self.time_unit = 'min'
        elif self.num_mins <= 1440:
            self.time_unit = 'hr'
        else:
            self.time_unit = 'day'
        self.unit = self.units[self.time_unit]
        self.num_recs = int(self.num_mins * 60. / self.dt)
        self.skip = 1
        self.multiplier = 1.0 # use to convert ADC reading into optical power
        self.data = getcounts(self.num_recs, self.skip)

        tk.Frame.__init__(self, master, **kwargs)
        self.running = True
        self.ani = None

        btns = tk.Frame(self)
        btns.pack()
        lbl = tk.Label(btns, text="multiplier")
        lbl.pack(side=tk.LEFT)
        self.multbox = tk.Entry(btns, width=6)
        self.multbox.insert(0,str(self.multiplier))
        self.multbox.pack(side=tk.LEFT)

        lbl2 = tk.Label(btns, text="skip")
        lbl2.pack(side=tk.LEFT)
        self.skipbox = tk.Entry(btns, width=6)
        self.skipbox.insert(0,str(self.skip))
        self.skipbox.pack(side=tk.LEFT)

        lbl3 = tk.Label(btns, text="minutes")
        lbl3.pack(side=tk.LEFT)
        self.numrecsbox = tk.Entry(btns, width=6)
        self.numrecsbox.insert(0,str(self.num_mins))
        self.numrecsbox.pack(side=tk.LEFT)
        self.btn = tk.Button(btns, text='Start', command=self.on_click)
        self.btn.pack(side=tk.LEFT)

        plt.style.use('dark_background')
        if len(sys.argv) > 2:
            self.fig = plt.Figure(figsize=(float(sys.argv[2]),float(sys.argv[3])))
        else:
            self.fig = plt.Figure(figsize=(10,6.2))
        self.ax1 = self.fig.add_subplot(111)
        self.times = self.data[:,0]
        self.times = (self.times - self.times[0])/self.unit
        self.counts = self.data[:,1]*self.multiplier
        self.line, = self.ax1.plot(self.times, self.counts, 'c-', lw=2)
        self.line2, = self.ax1.plot([self.times[0],self.times[-1]],
                        [self.counts[0]]*2,'r--')
        max_counts = max(self.counts)
        min_counts = min(self.counts)
        self.ax1.set_ylim(0.9*min_counts,1.1*max_counts)
        self.ax1.set_title('\n{:.3e} mW'.format(self.counts[0]),fontsize=40)
        self.ax1.set_xlim(min(self.times), max(self.times))
        self.ax1.set_ylabel('P/mW')
        self.ax1.set_xlabel('t/%s' % self.time_unit)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        self.start()

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
            repeat=False)
        self.running = True
        self.btn.config(text='Pause')
        self.ani._start()
        print('started animation')

    def update_graph(self, i):
        # update GUI params
        if self.multbox.get() != '':
            self.multiplier = float(self.multbox.get())
        if self.skipbox.get() != '':
            self.skip = int(self.skipbox.get())
        if self.numrecsbox.get() != '':
            self.num_mins = int(self.numrecsbox.get())
        self.num_recs = max(10,int(self.num_mins * 60. / self.dt))
        if self.num_mins <= 1:
            self.time_unit = 'sec'
        elif self.num_mins <= 60:
            self.time_unit = 'min'
        elif self.num_mins <= 1440:
            self.time_unit = 'hr'
        else:
            self.time_unit = 'day'
        self.unit = self.units[self.time_unit]

        # reload data
        self.data = getcounts(self.num_recs, self.skip)
        self.times = self.data[:,0]
        self.times = (self.times - self.times[0])/self.unit
        self.counts = self.data[:,1]*self.multiplier

        # update the graph
        self.line.set_data(self.times, self.counts)
        max_counts = max(self.counts)
        min_counts = min(self.counts)
        self.ax1.set_ylim(0.9*min_counts,1.1*max_counts)
        self.ax1.set_xlim(min(self.times), max(self.times))
        self.ax1.set_title('\n{:.3e} mW'.format(self.counts[0]),
                            fontsize=40)
        self.ax1.set_xlabel('t/%s' % self.time_unit)
        self.line2.set_data([self.times[0],self.times[-1]],
                        [self.counts[0]]*2)
        return self.line, self.line2

root = tk.Tk()
root.resizable(height = None, width = None)
root.title = 'Lasing'
app = App(root)
app.pack()
root.mainloop()
