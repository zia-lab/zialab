#!/usr/bin/python3

import tkinter as tk
import matplotlib, sys
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import cursors
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from tkinter.filedialog import asksaveasfilename
import numpy as np
import sympy as sp
from scipy.optimize import curve_fit
import random
from scipy import spatial
from time import time
from pyperclip import copy as pypercopy

def lorentz_model(num_peaks):
    x = sp.Symbol('x')
    thef = [sp.Symbol('A_%d' % i)/(1+ 4 / sp.Symbol('w_%d' % i)**2 * (x-sp.Symbol('d_%d' % i))**2) for i in range(num_peaks)]
    Avars = tuple([sp.Symbol('A_%d' % i) for i in range(num_peaks)])
    dvars = tuple([sp.Symbol('d_%d' % i) for i in range(num_peaks)])
    wvars = tuple([sp.Symbol('w_%d' % i) for i in range(num_peaks)])
    allvars = (x,) + Avars + dvars + wvars
    fitfun = np.sum(thef)
    fitfun = sp.lambdify(allvars, fitfun, 'numpy')
    return fitfun

def gaussian_model(num_peaks):
    x = sp.Symbol('x')
    thef = [sp.Symbol('A_%d' % i) * sp.exp(-1/2/sp.Symbol('w_%d' % i)**2*(x-sp.Symbol('d_%d' % i))**2) for i in range(num_peaks)]
    Avars = tuple([sp.Symbol('A_%d' % i) for i in range(num_peaks)])
    dvars = tuple([sp.Symbol('d_%d' % i) for i in range(num_peaks)])
    wvars = tuple([sp.Symbol('w_%d' % i) for i in range(num_peaks)])
    allvars = (x,) + Avars + dvars + wvars
    fitfun = np.sum(thef)
    fitfun = sp.lambdify(allvars, fitfun, 'numpy')
    return fitfun

def jiggle(l, jig=0.05):
    jiggled = [x*(1+jig*random.random()) for x in l]
    return jiggled

csv_filename = '/Volumes/jlizaraz/ZiaLab/Log/Data/yag - 1647627190.csv'
fit_model = lorentz_model

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.wiggle = 100
        self.maxfev = 100000
        self.data = np.genfromtxt(csv_filename, delimiter=',')
        self.x = self.data[:,0]
        self.y = self.data[:,1]
        self.fit_quality = 0
        self.ranger = np.linspace(min(self.x), max(self.x), 500)
        self.ranger = self.x
        self.yranger = np.interp(self.ranger, self.x, self.y)
        self.yranger = self.y
        self.num_peaks = None
        self.landmark_h = 0.05
        self.de = 40
        self.fit_params = []
        self.fitx = self.data[:,0]
        self.fity = np.zeros(len(self.fitx))
        self.prior_centers = []
        self.prior_amps = []
        tk.Frame.__init__(self, master, **kwargs, bg='black')

        btns = tk.Frame(self, bg ='black')
        btns.configure(background="black")
        
        self.master.bind('<space>', lambda _ : self.fit())

        plt.style.use('dark_background')
        self.fig = plt.Figure(figsize=(13,8))
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.plot(self.data[:,0], self.data[:,1])
        self.ax1.set_xlabel('E/cm${}^{-1}$')
        self.fitline, = self.ax1.plot(self.ranger, [0]*len(self.ranger))
        self.difline, = self.ax1.plot(self.ranger, [0]*len(self.ranger))
        self.knots, = self.ax1.plot([],[],'d',lw=0.2)
        self.landmarks, = self.ax1.plot([],[],'w-')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.canvas.get_tk_widget().pack()
        self.fig.canvas.callbacks.connect('button_press_event',
                                          self.annotate_point1)
        
        btns3 = tk.Frame(self, bg ='black')
        btns3.pack()

        self.fitbutton = tk.Button(btns3, text='Fit', background='red', fg='red', command = self.fit)
        self.fitbutton.pack(side=tk.LEFT, pady=20)
        self.fitbutton.config(highlightbackground="black")
        self.autobutton = tk.Button(btns3, text='Auto', background='red', fg='red', command = self.auto)
        self.autobutton.pack(side=tk.LEFT, pady=20)
        self.autobutton.config(highlightbackground="black")
        self.copybutton = tk.Button(btns3, text='Copy to clipboard', background='red', fg='red', command = self.clipboard)
        self.copybutton.pack(side=tk.LEFT, pady=20)
        self.copybutton.config(highlightbackground="black")

    def auto(self):
        for i in range(10):
            self.fit()

    def clipboard(self):
        num_peaks = self.num_peaks
        fparams = self.fit_params
        export_dict = {"fit_amplitudes": fparams[:num_peaks],
        "fit_positions": fparams[num_peaks:2*num_peaks],
        "fit_widths": fparams[2*num_peaks:]
        }
        pypercopy(str(export_dict))
        print("Copied to clipboard!")


    def fit(self):
        num_peaks = len(self.prior_centers)
        if num_peaks == self.num_peaks:
            start_amplitudes = self.fit_params[:(num_peaks)]
            start_positions = jiggle(self.fit_params[(num_peaks):2*(num_peaks)])
            start_widths = jiggle(self.fit_params[2*(num_peaks):])
            start_widths = [min(x, 2*self.wiggle) for x in start_widths]
            start_params = list(start_amplitudes) + list(start_positions) + list(start_widths)
            lower_bounds = [0]*len(start_amplitudes) + [s - self.de for s in start_positions] + [0 for _ in start_widths]
            upper_bounds = [np.inf]*len(start_amplitudes) + [s + self.de for s in start_positions] + [2*self.wiggle for _ in start_widths]
            bounds = (lower_bounds, upper_bounds)
        else:
            start_amplitudes = self.fit_params[:(num_peaks-1)] + [self.prior_amps[-1]**2/num_peaks]
            start_positions = self.fit_params[(num_peaks-1):2*(num_peaks-1)] + [self.prior_centers[-1]]
            start_widths = self.fit_params[2*(num_peaks-1):] + [self.wiggle]
            start_params = start_amplitudes + start_positions + start_widths
            lower_bounds = [0]*len(start_amplitudes) + [s - self.de for s in start_positions] + [0 for _ in start_widths]
            upper_bounds = [np.inf]*len(start_amplitudes) + [s + self.de for s in start_positions] + [2*self.wiggle for _ in start_widths]
            bounds = (lower_bounds, upper_bounds)
        fitfun = fit_model(num_peaks)
        fparams, fcov = curve_fit(fitfun, self.x, self.y, start_params, maxfev=self.maxfev, bounds=bounds)
        print("fit_amplitudes", ','.join(list(map(str,fparams[:num_peaks]))))
        print("fit_positions", ','.join(list(map(str,fparams[num_peaks:2*num_peaks]))))
        print("fit_widths", ','.join(list(map(str,fparams[2*num_peaks:]))))
        self.num_peaks = num_peaks
        self.fit_params = list(fparams)
        fitted_ranger = fitfun(self.ranger, *fparams)
        self.difline.set_ydata((fitted_ranger-self.y))
        self.fitline.set_ydata(fitted_ranger)
        knots = self.fit_params[num_peaks:2*num_peaks]
        self.knots.set_data(knots,[0]*len(knots))
        landsm = [[min(self.x),0]]
        for knot in knots:
            landsm.append([knot,0])
            landsm.append([knot, self.landmark_h])
            landsm.append([knot,0])
        landsm.append([max(self.x),0])
        landsm = np.array(landsm)
        self.landmarks.set_data(landsm[:,0],landsm[:,1])
        print("#"*10)
        fit_metric = 1 - spatial.distance.cosine(fitted_ranger, self.yranger)
        self.ax1.set_title('N=%d | S=%.6f' % (num_peaks,fit_metric))
        print(num_peaks, fit_metric)
        print("#"*10)
        self.canvas.draw()
        self.num_peaks = num_peaks

    def annotate_point1(self,event):
        if event.inaxes is not None:
            stringo = '(%.2f,\n%.3f)' % (event.xdata, event.ydata)
            print(event.xdata, event.ydata)
            self.ax1.plot([event.xdata], [event.ydata],'wx')
            self.prior_centers.append(event.xdata)
            self.prior_amps.append(event.ydata)
            self.canvas.draw()
        else:
            print('Clicked ouside axes bounds but inside plot window')

root = tk.Tk()
root.resizable(height = None, width = None)
root.configure(bg='black')
root.title('Space Invaders')
root.winfo_toplevel().title = "Simple Prog"
app = App(root)
app.pack()
root.eval('tk::PlaceWindow . center')
root.mainloop()
