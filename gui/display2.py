#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A general-purpose display for showing the a time-varying value.

import sys
if sys.platform == 'darwin':  # kind of neccesary to import this here
    import matplotlib
    matplotlib.use("TkAgg")
    import psutil
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
import numpy as np
from time import time, sleep
from random import random
import colorsys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

print("Press (r) to reset, press (q) to quit.")
plt.style.use(['dark_background'])

def dummy_counts():
    if sys.platform == 'darwin':
        return psutil.cpu_percent()
    else:
        return random()*2-1


def pad(num):
    str_num = '{:0>.2e}'.format(num)
    return str_num


class Monitor():
    '''
    Gives a Tk window that gives the time-dependent
    output of a function, and shows a little trendline
    in the background. Color changes with order of magnitude.
    '''
    def __init__(self,
                 window_title='ClickClack',
                 get_counts=dummy_counts,
                 sampling_frequency=1):
        self.get_counts = get_counts  # the counts function
        self.sampling_rate_Hz = sampling_frequency  # in Hz
        self.sampling_interval = 1000*1./self.sampling_rate_Hz  # in ms

        # plot and window styling
        self.window_title = window_title
        self.pause = False
        self.fontsize = 65
        self.width = 1
        self.height = 0.25
        self.maxtime = 60  # in seconds

        # giddy up the tk
        self.root = tk.Tk()
        self.root.config(bg='black')
        self.root.title(self.window_title)
        self.frame = tk.Frame(master=self.root)

        # initialize counts
        self.counts = [self.get_counts()]
        self.start_time = time()
        self.times = [0]
        self.init_window()
        self.start_time = time()
        self.itercount = 0

    def init_window(self):
        def animate(i):
            # hack to pause the animation
            if self.pause:
                return None
            # update the times and counts
            self.times.append(time())
            self.counts.append(self.get_counts())
            # update the text
            count_text = pad(self.counts[-1])
            self.text.set_text(count_text)
            exponent = (int(count_text.split('e')[-1]))
            color = colorsys.hsv_to_rgb(exponent/10+0.5, 1, 1)
            self.text.set_color(color)
            # update the lineplot
            self.array_times = np.array(self.times)
            good_times = self.array_times > (time() - self.maxtime)
            self.good_times = self.array_times[good_times]
            self.good_counts = np.array(self.counts)[good_times]
            self.plot.set_xdata(np.linspace(0, self.width,
                                len(self.good_times)))
            self.plot.set_ydata(((self.good_counts) / max(self.good_counts) *
                                  self.height))
            # keep only what is needed
            self.times = self.times[-len(self.array_times):]
            self.counts = self.counts[-len(self.array_times):]
            self.itercount += 1
            return None

        self.fig = plt.figure(figsize=(5 * self.width, 5 * self.height))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.axis('off')
        self.text = self.ax.text(x=-self.height*0.1, y=self.height*0.25,
                                 s=pad(self.counts[-1]),
                                 fontsize=self.fontsize, va='center',
                                 ha='left', color='red', family='monospace')
        self.plot, = self.ax.plot(self.times, self.counts, c='red')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().grid(column=0, row=0)
        self.ani = animation.FuncAnimation(self.fig, animate, None,
                                           interval=self.sampling_interval,
                                           blit=False)
        plt.tight_layout()

        def onClick(event):
            if event.dblclick:
                self.pause ^= True
        self.fig.canvas.mpl_connect('button_press_event', onClick)

        def on_key(event):
            # print('you pressed', event.key, event.xdata, event.ydata)
            if event.key == 'q':
                self.root.destroy()
            if event.key == 'r':
                self.reset()
        self.fig.canvas.mpl_connect('key_press_event', on_key)

        # pack it all up
        self.frame.grid(row=0, column=0)

    def reset(self):
        self.counts = [self.get_counts()]
        self.start_time = time()
        self.times = [self.start_time]

    def run(self):
        """run it all"""
#        self.root.geometry("1000x200")
        self.root.resizable(False, False)
        self.root.mainloop()

Monitor().run()
