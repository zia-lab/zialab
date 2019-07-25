#!/usr/bin/env python

# A general purpose monitor for showing the ouput of time-dependent functions.
# Coded by David on July 25 2019.
# When running in notebooks, it isn't necessary to call the run method
# for the process detaches itself from the main execution.

import sys
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")
    import psutil

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.style.use(['dark_background'])

import tkinter as tk
import numpy as np
from time import time, sleep
from random import random

def dummy_counts():
    if sys.platform == 'darwin':
        return psutil.cpu_percent()
    else:
        return random()*2-1

class Monitor():
    '''
    Gives a Tk window that animates a function,
    at a given samplig rate. A few convenient
    display options are available.
    '''
    def __init__(self,
                y_min = np.nan,
                y_max = np.nan,
                auto_y_range = True,
                window_title='Time flies',
                plot_title = 'It does',
                get_counts = dummy_counts,
                sampling_frequency = 1,
                time_range = 10,
                horizontal_marker = False):
        self.get_counts = get_counts
        self.timerange = time_range # this is must always be given in seconds
        self.sampling_rate_Hz = sampling_frequency # this must always be given in Hz
        self.sampling_interval = 1000*1./self.sampling_rate_Hz # must be given in ms to animate function
        self.max_records = int(1.5*self.timerange*self.sampling_rate_Hz)
        self.info = "q:exit | r:reset | double_click:pause"
        
        # determine an adequate unit of time
        if self.timerange < 60: # seconds
            self.time_unit = 1
            self.time_label = 's'
        elif self.timerange <= 3600: # minutes
            self.time_unit = 60
            self.time_label = 'min'
        else:
            self.time_unit = 3600 # hours
            self.time_label = 'hour'
        
        # plot and window styling
        self.linecolor = 'red'
        self.window_title =  window_title
        self.plot_title = plot_title
        self.auto_y_range = auto_y_range
        self.tk_columns = 7
        self.horizontal_marker = horizontal_marker
        self.pause = False
        if self.auto_y_range:
            self.y_min = 'auto'
            self.y_max = 'auto'
        else:
            self.y_min = y_min
            self.y_max = y_max
        
        # giddy up the tk
        self.root = tk.Tk()
        self.root.config(bg='black')
        self.root.title(self.window_title)
        self.frame = tk.Frame(master=self.root)
        self.itercount = 0
        self.min_y_field_label = tk.Label(master=self.root,text="y_min = ",bg='black',fg='white',anchor='w')
        self.min_y_field = tk.Entry(master=self.root,highlightbackground='black', width=5)
        self.min_y_field.insert(tk.END, self.y_min)
        self.min_y_field.bind("<Return>", (lambda event: self.set_ymin()))
        self.min_y_field.bind("<KP_Enter>", (lambda event: self.set_ymin()))
        self.max_y_field_label = tk.Label(master=self.root,text="y_max = ",bg='black',fg='white',anchor='w')
        self.max_y_field = tk.Entry(master=self.root,highlightbackground='black', width=5)
        self.max_y_field.insert(tk.END, self.y_max)
        self.max_y_field.bind("<Return>", (lambda event: self.set_ymax()))
        self.max_y_field.bind("<KP_Enter>", (lambda event: self.set_ymax()))
        self.info_label = tk.Label(master=self.root,text=self.info,bg='black',fg='white',borderwidth = 2, relief='ridge')
        self.config_label = tk.Label(master=self.root,text='% 5.2f Hz' % self.sampling_rate_Hz,bg='black',fg='white')
        
        # initialize time and count lists
        self.counts = [self.get_counts()]
        self.times = [0]
        self.init_window()
        self.start_time = time()
        
    def reset(self):
        """reset all times and counts"""
        self.times = []
        self.start_time = time()
        self.counts = []
        self.ax.set_xlim(0,self.timerange)

    def init_window(self):
        def animate(i): # this is the function called at each frame of the animation
            if self.pause: # hack to pause the animation
                return None
            if len(self.times) >= self.max_records: # when it's filled up, pop the first one
                self.times.pop(0) # let one go
                self.counts.pop(0) # here, too
            self.counts.append(self.get_counts())
            if len(self.times) >2: # compute the actual refresh rate, and try and match it to target
                samp_rate = 1./(self.times[-1]-self.times[-2])
                self.config_label.config(text = "%.2f Hz" % samp_rate)
                if (samp_rate > self.sampling_rate_Hz):
                    new_interval = self.ani.event_source.interval*1.02
                else:
                    new_interval = self.ani.event_source.interval*0.98
                #print(new_interval)
                if new_interval <= 0:
                    new_interval = self.sampling_interval
                self.ani.event_source.interval = new_interval
            self.times.append((time()-self.start_time)/self.time_unit) # times are saved in the unit of time defined initially
            self.line.set_ydata(self.counts)  # update the data
            self.line.set_xdata(self.times) 
            if self.horizontal_marker: # plot, or not, a visual guide to the last value
                self.line2.set_xdata([self.times[0],self.times[-1]])
                self.line2.set_ydata([self.counts[-1],self.counts[-1]])
            self.ax.set_title('%.3f' % (self.counts[-1]), color='cyan', fontsize = 200, pad = 20)
            if self.y_min == 'auto' and self.y_max == 'auto':
                if min(self.counts) == max(self.counts):
                    self.ax.set_ylim(0,1)
                else:
                    self.ax.set_ylim(min(self.counts),max(self.counts))
            elif self.y_min == 'auto' and self.y_max != 'auto':
                self.ax.set_ylim(min(self.counts),self.y_max)
            elif self.y_min != 'auto' and self.y_max == 'auto':
                self.ax.set_ylim(self.y_min,max(self.counts))
            else:
                self.ax.set_ylim(self.y_min,self.y_max)
            if self.times[-1]*self.time_unit >= self.timerange:
                self.ax.set_xlim((self.times[-1]*self.time_unit-self.timerange)/self.time_unit, self.times[-1])
            if self.itercount == 0:
                plt.tight_layout()
            self.itercount += 1
            return self.line, self.line2 
        
        self.fig = plt.figure(figsize=(10,5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('---', color='cyan', fontsize = 200, pad = 20)
        self.ax.set_xlim(0,self.timerange/self.time_unit)
        self.ax.set_title(self.plot_title)
        self.ax.set_xlabel('t / %s' % self.time_label)
        if not self.auto_y_range:
            self.ax.set_ylim(self.y_min, self.y_max)
        self.line, = self.ax.plot([],
                                [],'o-',ms=2,
                                c=self.linecolor)
        
        self.line2, = self.ax.plot([],
                                [],
                                '--',
                                c='white')       
        self.canvas = FigureCanvasTkAgg(self.fig,
                                        master=self.frame)
        self.canvas.get_tk_widget().grid(column=0, row=0)
        self.ani = animation.FuncAnimation(self.fig,
                                animate, 
                                None, 
                                interval=self.sampling_interval, 
                                blit=False)
        
        def onClick(event):
            if event.dblclick:
                self.pause ^= True
                
        self.fig.canvas.mpl_connect('button_press_event', onClick)
        def on_key(event):
            # print('you pressed', event.key, event.xdata, event.ydata)
            if event.key == 'q':
                self.root.destroy()
                #exit()
            if event.key == 'r':
                self.reset()
        self.fig.canvas.mpl_connect('key_press_event', on_key)
        
        # pack it all up
        self.botton_row_pady = (10,40)
        self.frame.grid(row=0,column=0,columnspan=self.tk_columns,padx=20,pady=(20,0))
        self.min_y_field_label.grid(sticky='e', row=1, column=0, pady=self.botton_row_pady)
        self.min_y_field.grid(sticky='w',row=1, column=1, pady=self.botton_row_pady)
        self.max_y_field_label.grid(sticky='e', row=1, column=2, pady=self.botton_row_pady)
        self.max_y_field.grid(sticky='w', row=1, column=3, pady=self.botton_row_pady)
        self.info_label.grid(row=1, column=4, pady=self.botton_row_pady)
        self.config_label.grid(row=1, column=5, pady=self.botton_row_pady)
        
    def set_ymin(self):
        """set the minimum value in the vertical axis"""
        field_get = self.min_y_field.get()
        if field_get == 'auto':
            self.y_min = 'auto'
        else:
            self.y_min = float(field_get)
        self.canvas.get_tk_widget().focus_set()

    def set_ymax(self):
        """set the maximum value in the vertical axis"""
        field_get = self.max_y_field.get()
        if field_get == 'auto':
            self.y_max = 'auto'
        else:
            self.y_max = float(field_get)
        self.canvas.get_tk_widget().focus_set()
        
    def run(self):
        """run it all"""
        #self.root.geometry("1000x200")
        self.root.resizable(False,False)
        self.root.mainloop()
