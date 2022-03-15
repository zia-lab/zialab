#/usr/bin/python3
# This is a GUI used to monitor the voltage
# across a 50 Ohm resistor using an ADC attached
# to the a Raspberry Pi.
# The output can be scaled in the GUI to give
# a calibrated optical power.
# This calibration has to be done using a powermeter.

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time

import random
import requests

global start_time

start_time=time.time()
#times = list(np.linspace(0, num_elements, num_elements))


import numpy as np
#try:
#    from zialab.instruments import ADS1x15
#except:
#    import ADS1x15

class PhotoDiodeWithADC:
    def __init__(self, settings={}):
        self.gains = {
            '0 dB': {'Hi-Z': 1.51e3,'50 Ohm': 0.75e3},
            '10 dB': {'Hi-Z': 4.75e3,'50 Ohm': 2.38e3},
            '20 dB': {'Hi-Z': 1.5e4,'50 Ohm': 0.75e4},
            '30 dB': {'Hi-Z': 4.75e4,'50 Ohm': 2.38e4},
            '40 dB': {'Hi-Z': 1.51e5,'50 Ohm': 0.75e5},
            '50 dB': {'Hi-Z': 4.75e5,'50 Ohm': 2.38e5},
            '60 dB': {'Hi-Z': 1.5e6,'50 Ohm': 0.75e6},
            '70 dB': {'Hi-Z': 4.75e6,'50 Ohm': 2.38e6}
            }
        self.responsivities = np.array([[351.597,0.0479292],[383.538,0.0483439],
            [414.84,0.0790784],[455.3,0.122153],[500.043,0.165116],
            [555.453,0.224512],[600.572,0.275834],[658.676,0.344122],
            [698.6,0.387234],[750.875,0.44838],[800.551,0.498523],
            [843.752,0.539818],[887.262,0.578865],[927.237,0.609987],
            [960.269,0.630814],[986.415,0.63086],[1009.17,0.61136],
            [1021.59,0.566442],[1033.3,0.509277],[1045.2,0.436869],
            [1055.49,0.351615],[1066.72,0.271641],[1082.39,0.204956],
            [1098.92,0.14756]]) # wavelength in nm, responsivity in A/W
        self.defaults = {
            'scale_factor': 0.5, # depends on the load resistance: 50 Ohm / (50 Ohm + R_load)
            'wavelength': 532,
            'adc_channel': 0,
            'adc_gain': 1,
            'dc_samples': 100,
            'gain': self.gains['0 dB']['50 Ohm']
            }
        if settings:
            self.settings = settings
        else:
            print("Using default settings.")
            print(self.defaults)
            self.settings = self.defaults
        self.gain = self.settings['gain']
        self.scale_factor = self.settings['scale_factor']
        self.ADC = ADS1x15.ADS1115() # create an instance of the ADC
        self.wavelength = self.settings['wavelength']
        self.responsivity = np.interp(self.wavelength, self.responsivities[:,0], self.responsivities[:,1])
        self.adc_channel = self.settings['adc_channel']
        self.adc_gain = self.settings['adc_gain']
        self.dc_samples = self.settings['dc_samples']
    def set_wavelength(self,wavelength):
        self.wavelength = wavelength
        self.responsivity = np.interp(self.wavelength, self.responsivities[:,0], self.responsivities[:,1])
    def read_cw_optical_power(self):
        '''returns optical power in W along with the uncertainty'''
        adc_voltages = [self.ADC.read_voltage(self.adc_channel, self.adc_gain) for i in range(self.dc_samples)]
        mean_voltage = np.mean(adc_voltages)
        std_voltage = np.std(adc_voltages)
        rel_uncert_in_voltage = std_voltage/mean_voltage
        optical_power = mean_voltage / (self.gain * self.responsivity * self.scale_factor)
        optical_power_uncertainty = optical_power * rel_uncert_in_voltage
        return optical_power, optical_power_uncertainty

# photodiode = PhotoDiodeWithADC()

def getcounts():
    return random.random()
#    return photodiode.read_cw_optical_power()[0]

#def get_data_old():
#    times = list(range(num_elements))
#    counts.pop(0)
#    counts.append(multiplier*getcounts())
#    return times, counts

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.running = False
        self.ani = None
        self.num_elements=500
        self.timefmt="time elapsed = %.2f min"
        self.start_multiplier = '218.07'
        self.N = 5
        self.interval = 0.1
        self.counts = [0]*self.num_elements
        self.times = list(range(self.num_elements))
        self.avg_counts=[0]*self.num_elements
        self.titlefmt='hello\n\n%.3f mW $\pm 1$ %%'
        self.btns = tk.Frame(self)
        self.btns.pack()
        self.lbl = tk.Label(self.btns, text="multiplier")
        self.lbl.pack(side=tk.LEFT)
        self.multbox = tk.Entry(self.btns, width=6)
        self.multbox.insert(0,self.start_multiplier)
        self.multbox.pack(side=tk.LEFT)
        self.lbl2 = tk.Label(self.btns, text="refresh interval / s")
        self.lbl2.pack(side=tk.LEFT)
        self.intervalbox = tk.Entry(self.btns, width=6)
        self.intervalbox.insert(0,self.interval)
        self.intervalbox.pack(side=tk.LEFT)
        self.btn = tk.Button(self.btns, text='Start', command=self.on_click)
        self.btn.pack(side=tk.LEFT)
        self.btn2 = tk.Button(self.btns, text='Reset All', command=self.on_click2)
        self.btn2.pack(side=tk.LEFT)
        self.fig = plt.Figure(figsize=(10,5))
        self.ax1 = self.fig.add_subplot(111)
        self.line, = self.ax1.plot([], [], lw=2)
        self.line2, = self.ax1.plot(self.times,self.avg_counts)
        self.line3, = self.ax1.plot([self.times[-1]],[0],'ro',ms=4)
        self.line4, = self.ax1.plot([0,self.num_elements],[0]*2,'k--')
        self.annotation = self.ax1.annotate(self.timefmt % (0), xy=(0.01,0.95),xycoords='axes fraction',ha='left')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)
        self.max_counts = 200
        self.ax1.set_ylim(0,1)
        self.ax1.set_xlim(0,self.num_elements)
        self.ax1.set_title('\n-----------',fontsize=40)
    def get_data(self):
        self.counts.pop(0)
        self.counts.append(self.multiplier*getcounts())
        return self.times, self.counts
    def on_click(self):
        '''the button is a start, pause and resume button all in one
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
            # animation is paused; resume it
            self.ani.event_source.start()
            self.btn.config(text='Pause')
        self.running = not self.running
    def on_click2(self):
        '''this button is used to reset all variables'''
        self.max_counts = 0
        self.counts = [0]*self.num_elements
        self.avg_counts = [0]*self.num_elements
    def start(self):
        #self.points = int(self.points_ent.get()) + 1
        frames=1000000
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_graph,
            frames=frames,
            interval=self.interval,
            repeat=False)
        self.running = True
        self.btn.config(text='Pause')
        self.ani._start()
        print('started animation')
    def update_graph(self, i):
        global multiplier
        print(self.ani.event_source.interval)
        if self.intervalbox.get() == '' or float(self.intervalbox.get()) == 0.:
            self.ani.event_source.interval = 100.
        else:
            self.ani.event_source.interval = float(self.intervalbox.get())*1000.            
        if self.multbox.get() != '':
            self.multiplier = float(self.multbox.get())
        self.line.set_data(*self.get_data()) # update graph
        self.ax1.set_title(self.titlefmt % (self.counts[-1]),fontsize=40)
        self.max_counts=max(max(self.counts),self.max_counts)
        self.ax1.set_ylim(0,1.1*self.max_counts)
        counts_array=np.array(self.counts)
        self.avg_counts=np.convolve(counts_array, np.ones((self.N,))/self.N, mode='valid')
        self.avg_counts=list(self.avg_counts)
        self.avg_counts=[self.avg_counts[0]]*(self.N-1)+self.avg_counts
        self.line2.set_ydata(self.avg_counts)
        self.line3.set_ydata([self.avg_counts[-1]])
        self.line4.set_ydata([self.avg_counts[-1]]*2)
        self.annotation.set_text(self.timefmt % ((time.time()-start_time)/60.))
        return self.line, self.ax1, self.line2, self.line3, self.line4, self.annotation

root = tk.Tk()
root.resizable(height = None, width = None)
app = App(root)
app.pack()
root.mainloop()
