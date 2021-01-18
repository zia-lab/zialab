#!/usr/bin/python3

'''GUI for configuring filters.

   X The first three filters are multiplied for the combo.
   X The fourth filter is meant to represent the excitation filter.
   X Cliking on the graph annotates it with the corresponding coordinates.
   X For adding filters to the database, open and inspect Filters.ipynb.
   X In all cases the polarization behaviour is suspect.

   This was coded in Nov 2020 by David.
'''

import tkinter as tk
import sys
from time import sleep
import matplotlib, time, subprocess, sys
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import cursors
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from tkinter.filedialog import asksaveasfilename
import numpy as np
import pickle

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.dt = 1
        self.scale_types = ['linear','log']
        self.filters = pickle.load(open('filters.pkl','rb'))
        self.filter_names = list(sorted(self.filters.keys()))
        self.filter_names.insert(0,'---')
        self.wavemin = 400
        self.wavemax = 1600

        self.filter0 = tk.StringVar()
        self.filter0.set(self.filter_names[1])
        self.filter1 = tk.StringVar()
        self.filter1.set(self.filter_names[0])
        self.filter2 = tk.StringVar()
        self.filter2.set(self.filter_names[0])
        self.filter3 = tk.StringVar()
        self.filter3.set(self.filter_names[0])
        self.filtervars = [self.filter0, self.filter1, self.filter2]
        self.scale_type = tk.StringVar()
        self.scale_type.set(self.scale_types[0])
        tk.Frame.__init__(self, master, **kwargs, bg='black')

        btns = tk.Frame(self, bg ='black')
        btns.pack()
        btns.configure(background="black")
        self.filterbox0 = tk.OptionMenu(btns, self.filter0,
                        *self.filter_names[1:], command=self.update_graph)
        self.filterbox1 = tk.OptionMenu(btns, self.filter1,
                        *self.filter_names, command=self.update_graph)
        self.filterbox2 = tk.OptionMenu(btns, self.filter2,
                        *self.filter_names, command=self.update_graph)
        self.filterbox3 = tk.OptionMenu(btns, self.filter3,
                        *self.filter_names, command=self.update_graph)
        self.scale_box = tk.OptionMenu(btns, self.scale_type,
                        *self.scale_types, command=self.update_graph)

        if sys.platform == 'darwin':
            self.filterbox0.config(background="black")
            self.filterbox1.config(background="black")
            self.filterbox2.config(background="black")
            self.filterbox3.config(background="black")
            self.scale_box.config(background="black")

        self.filterbox0.pack(side=tk.LEFT)
        self.filterbox1.pack(side=tk.LEFT, pady=20)
        self.filterbox2.pack(side=tk.LEFT)
        self.scale_box.pack(side=tk.LEFT)
        self.filterbox3.pack(side=tk.LEFT)

        self.master.bind('<Return>', lambda _ : self.set_lims())
        self.master.bind('<KP_Enter>', lambda _: self.set_lims())
        self.master.bind('<Escape>', lambda _: root.destroy())

        plt.style.use('dark_background')
        self.fig = plt.Figure(figsize=(10,6.2))
        self.ax1 = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.canvas.get_tk_widget().pack()
        self.fig.canvas.callbacks.connect('button_press_event',
                                          self.annotate_point)
        btns2 = tk.Frame(self, bg ='black')
        btns2.pack()
        self.minwlabel = tk.Label(btns2, text='min wave / nm', background="black", fg='white')
        self.laserlabel = tk.Label(btns2, text='excitation / nm', background="black", fg='white')
        self.waveminbox = tk.Entry(btns2, width=4, justify='center')
        self.waveminbox.insert(0,str(self.wavemin))
        self.laserbox = tk.Entry(btns2, width=4, justify='center')
        self.laserbox.insert(0,str(532))
        self.maxwlabel = tk.Label(btns2, text='max wave / nm', background="black", fg='white')
        self.wavemaxbox = tk.Entry(btns2, width=4, justify='center')
        self.wavemaxbox.insert(0,str(self.wavemax))
        self.wavemaxbox.config(background="black", fg='white')
        self.waveminbox.config(background="black", fg='white')
        self.laserbox.config(background="black", fg='white')
        self.minwlabel.pack(side=tk.LEFT, pady = 20)
        self.waveminbox.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.maxwlabel.pack(side=tk.LEFT, pady = 20)
        self.wavemaxbox.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.laserlabel.pack(side=tk.LEFT, pady = 20)
        self.laserbox.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.savebutton =  tk.Button(btns2, text='Save', command = self.saveit)
        self.savebutton.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.update_graph(self.filter0.get())
    def saveit(self):
        print("saving ...")
        a = asksaveasfilename(filetypes=(("PNG Image", "*.png"),("All Files", "*.*")), defaultextension='.png', title="Save As")
        self.fig.savefig(a)
        self.savebutton['text'] = 'Saved!'
        self.savebutton.update()
        print("waiting")
        sleep(10)
        self.savebutton['text'] = 'Save'
        print("finished waiting")
        # self.fig.savefig()
    def set_lims(self):
        self.ax1.set_xlim(int(self.waveminbox.get()), int(self.wavemaxbox.get()))
        laser_line = float(self.laserbox.get())
        self.laserline.set_xdata([laser_line]*2)
        self.laserline.set_ydata([1E-6,1])
        self.canvas.draw()

    def annotate_point(self,event):
        if event.inaxes is not None:
            stringo = '(%.2f,\n%.3f)' % (event.xdata, event.ydata)
            print(event.xdata, event.ydata)
            self.ax1.plot([event.xdata], [event.ydata],'wx')
            if event.ydata > 0.5:
                ytext = event.ydata - 0.4
            else:
                ytext = event.ydata + 0.4
            self.ax1.annotate(stringo, xy = (event.xdata+1,event.ydata),
                              xytext=(event.xdata,ytext),
            arrowprops=dict(facecolor='white', width=0.5, headwidth = 5,
                            headlength = 5, shrink=0.05), ha='center',
                            backgroundcolor='black')
            self.canvas.draw()
        else:
            print('Clicked ouside axes bounds but inside plot window')

    def update_graph(self, filter_name):
        self.fig.legends = []
        self.ax1.clear()
        filtcounter = 0
        for filtervar in self.filtervars:
            filtername = filtervar.get()
            if filtername == '---':
                continue
            filtcounter = filtcounter+1
            waves = self.filters[filtername]['data'][:,0]
            transmi = self.filters[filtername]['data'][:,1]
            plabel = "%s (%d$^o$)" % (filtername, self.filters[filtername]['AOI'])
            self.ax1.plot(waves, transmi, lw=2,
                        label = plabel)
        if self.filter3.get() != '---':
            filtername = self.filter3.get()
            waves = self.filters[filtername]['data'][:,0]
            transmi = self.filters[filtername]['data'][:,1]
            plabel = "%s (%d$^o$)" % (filtername, self.filters[filtername]['AOI'])
            self.ax1.plot(waves, transmi, 'g-.', lw=2,
                            label = plabel)
        if filtcounter >= 2:
            waves = self.filters[self.filter0.get()]['data'][:,0]
            transmi = self.filters[self.filter0.get()]['data'][:,1]
            for filtervar in self.filtervars[1:]:
                filtername = filtervar.get()
                if filtername == '---':
                    continue
                transmi = transmi*self.filters[filtername]['data'][:,1]
            if self.filter3.get() != '---':
                self.ax1.plot(waves, transmi, 'r:', lw=2,
                                label = 'All but last')
            else:
                self.ax1.plot(waves, transmi, 'r:', lw=2,
                                label = 'All')
        if filtcounter == 1:
            num_cols = 1
        else:
            num_cols = filtcounter + 1
        if self.filter3.get() != '---':
            num_cols = num_cols + 1
        scale_type = self.scale_type.get()
        self.ax1.set_xlim(int(self.waveminbox.get()), int(self.wavemaxbox.get()))
        if scale_type == 'linear':
            self.ax1.set_ylim(0, 1)
        else:
            self.ax1.set_ylim(1e-6, 2)
            self.ax1.set_yscale(scale_type)
        laser_line = float(self.laserbox.get())
        self.laserline, = self.ax1.plot([laser_line]*2,[1E-6,1],'w--')
        self.ax1.set_xlabel('$\lambda$/nm')
        self.ax1.set_ylabel('T')
        self.fig.legend(loc='upper center', ncol = num_cols)
        self.canvas.draw()

root = tk.Tk()
root.resizable(height = None, width = None)
root.configure(bg='black')
root.title('Filters')
root.winfo_toplevel().title = "Simple Prog"
app = App(root)
app.pack()
root.eval('tk::PlaceWindow . center')
root.mainloop()
