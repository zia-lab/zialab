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
import pickle
import os


info = '''
┌─GUI for configuring PL filter cubes.───────────────────┐
│                                                        │
│ - Allows selecting excitation filters, emission        │
│ filters, and dichroic mirror.                          │
│ - Clicking on the graphs annotates them with the       │
│ corresponding coordinates.                             │
│ - Log and linear scale are available for display.      │
│ - In all cases polarization is suspect.                │
│ - For the "Total Excitation Transmission" the          │
│ reflectivity of the dichroic mirror is taken into      │
│ account, for the Total Emission Transmission", the     │
│ transmission of the dichroic mirror is used instead.   │
│ - For adding filters to the database, open and inspect │
│ Filters.ipynb.                                         │
│                                                        │
│ X This was initially coded in Nov 2020 by David and    │
│ improved significantly in 2022.                        │
└────────────────────────────────────────────────────────┘
'''

print(info)

if os.path.exists('filter_GUI_state.pkl'):
    print("Loading state ...")
    state = pickle.load(open('filter_GUI_state.pkl','rb'))
else:
    state = {'filter0' : 'Semrock - BLP01-325R',
            'filter1' : '---',
            'filter2' : '---',
            'dic_mirror' : '---',
            'filter3' : 'Semrock - BLP01-635R',
            'filter4' : '---',
            'filter5' : '---',
            'scale' : 'linear',
            'min_wave' : 400,
            'max_wave' : 1600,
            'laser_wave' : '532',
            'scale_checkbox': 0}

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        self.state = state
        self.master = master
        self.dt = 1
        self.scale_types = ['linear','log']
        self.filters = pickle.load(open('filters.pkl','rb'))
        self.filter_names = list(sorted(self.filters.keys()))
        dic_options = ['---']
        dic_options.extend([s for s in self.filter_names if any(['di' in s.lower(), 'lpd' in s.lower()])])
        self.filter_names = [s for s in self.filter_names if not any(['di' in s.lower(), 'lpd' in s.lower()])]
        self.filter_names.insert(0,'---')
        self.wavemin = self.state['min_wave']
        self.wavemax = self.state['max_wave']

        # excitation filters
        self.filter0 = tk.StringVar()
        self.filter0.set(self.state['filter0'])
        self.filter1 = tk.StringVar()
        self.filter1.set(self.state['filter1'])
        self.filter2 = tk.StringVar()
        self.filter2.set(self.state['filter2'])
        self.ex_filtervars = [self.filter0, self.filter1, self.filter2]

        # dichroic mirror
        self.dic_mirror = tk.StringVar()
        self.dic_mirror.set(self.state['dic_mirror'])

        # emission filters filters
        self.filter3 = tk.StringVar()
        self.filter3.set(self.state['filter3'])
        self.filter4 = tk.StringVar()
        self.filter4.set(self.state['filter4'])
        self.filter5 = tk.StringVar()
        self.filter5.set(self.state['filter5'])
        self.em_filtervars = [self.filter3, self.filter4, self.filter5]
        
        tk.Frame.__init__(self, master, **kwargs, bg='black')

        btns = tk.Frame(self, bg ='black')
        btns.pack()
        btns.configure(background="black")

        self.exlabel = tk.Label(btns, text='Excitation Filters', background="black", fg='white', padx=20)
        self.diclabel = tk.Label(btns, text='Dichroic Mirror', background="black", fg='white', padx=20)
        self.filterbox0 = tk.OptionMenu(btns, self.filter0,
                        *self.filter_names[1:], command=self.update_graphs)
        self.filterbox1 = tk.OptionMenu(btns, self.filter1,
                        *self.filter_names, command=self.update_graphs)
        self.filterbox2 = tk.OptionMenu(btns, self.filter2,
                        *self.filter_names, command=self.update_graphs)
        self.dic_box = tk.OptionMenu(btns, self.dic_mirror,
                        *dic_options, command=self.update_graphs)


        if sys.platform == 'darwin':
            self.filterbox0.config(background="black")
            self.filterbox1.config(background="black")
            self.filterbox2.config(background="black")
            self.dic_box.config(background="black")
        self.exlabel.pack(side=tk.LEFT)
        self.filterbox0.pack(side=tk.LEFT)
        self.filterbox1.pack(side=tk.LEFT, pady=20)
        self.filterbox2.pack(side=tk.LEFT)
        self.diclabel.pack(side=tk.LEFT)
        self.dic_box.pack(side=tk.LEFT)

        self.master.bind('<Return>', lambda _ : self.set_lims())
        self.master.bind('<KP_Enter>', lambda _: self.set_lims())
        self.master.bind('<Escape>', lambda _: root.destroy())

        plt.style.use('dark_background')
        self.fig = plt.Figure(figsize=(10,4))
        self.ax1 = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.canvas.get_tk_widget().pack()
        self.fig.canvas.callbacks.connect('button_press_event',
                                          self.annotate_point1)
        
        btns3 = tk.Frame(self, bg ='black')
        btns3.pack()

        self.emlabel = tk.Label(btns3, text='Emission Filters', background="black", fg='white', padx=20)
        self.filterbox3 = tk.OptionMenu(btns3, self.filter3,
                        *self.filter_names, command=self.update_graph2)
        self.filterbox4 = tk.OptionMenu(btns3, self.filter4,
                        *self.filter_names, command=self.update_graph2)
        self.filterbox5 = tk.OptionMenu(btns3, self.filter5,
                        *self.filter_names, command=self.update_graph2)
        
        if sys.platform == 'darwin':
            self.filterbox3.config(background="black")
            self.filterbox4.config(background="black")
            self.filterbox5.config(background="black")
        self.emlabel.pack(side=tk.LEFT)
        self.filterbox3.pack(side=tk.LEFT)
        self.filterbox4.pack(side=tk.LEFT, pady=20)
        self.filterbox5.pack(side=tk.LEFT)

        self.fig2 = plt.Figure(figsize=(10,4))
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)

        self.canvas2.get_tk_widget().pack()
        self.fig2.canvas.callbacks.connect('button_press_event',
                                          self.annotate_point2)
        

        btns2 = tk.Frame(self, bg ='black')
        btns2.pack()

        self.scale_type = tk.StringVar()
        self.scale_type.set(self.state['scale'])
        self.log_scale = tk.IntVar()
        self.log_scale.set(self.state['scale_checkbox'])
        self.minwlabel = tk.Label(btns2, text='min wave / nm', background="black", fg='white')
        self.laserlabel = tk.Label(btns2, text='excitation / nm', background="black", fg='white')
        self.waveminbox = tk.Entry(btns2, width=4, justify='center')
        self.waveminbox.insert(0,str(self.wavemin))
        self.scaleboxlabel = tk.Label(btns2, text='Log scale', background="black", fg='white')
        self.laserbox = tk.Entry(btns2, width=4, justify='center')
        self.laserbox.insert(0,(self.state['laser_wave']))
        self.maxwlabel = tk.Label(btns2, text='max wave / nm', background="black", fg='white')
        self.wavemaxbox = tk.Entry(btns2, width=4, justify='center')
        self.wavemaxbox.insert(0,str(self.wavemax))
        self.wavemaxbox.config(background="black", fg='white')
        self.waveminbox.config(background="black", fg='white')
        self.laserbox.config(background="black", fg='white')

        # pack em

        self.minwlabel.pack(side=tk.LEFT, pady = 20)
        self.waveminbox.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.maxwlabel.pack(side=tk.LEFT, pady = 20)
        self.wavemaxbox.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.laserlabel.pack(side=tk.LEFT, pady = 20)
        self.laserbox.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.scaleboxlabel.pack(side=tk.LEFT)
        self.scale_check = tk.Checkbutton(btns2, variable = self.log_scale, command=self.update_graphs, bg='black')
        self.scale_check.pack(side=tk.LEFT)
        self.exitbutton =  tk.Button(btns2, text='Save & Exit', command = self.quit, background='black', fg='red')
        if sys.platform == 'darwin':
            self.exitbutton.config(highlightbackground="black")
        self.exitbutton.pack(side=tk.LEFT, pady = 20, padx = 5)
        self.resetbutton =  tk.Button(btns2, text='Reset', command = self.reset, background='black', fg='red')
        if sys.platform == 'darwin':
            self.resetbutton.config(highlightbackground="black")
        self.resetbutton.pack(side=tk.LEFT)
        self.update_graphs()

    def reset(self):
        default_state = {'filter0' : 'BLP01-325R',
                'filter1' : '---',
                'filter2' : '---',
                'dic_mirror' : '---',
                'filter3' : 'BLP01-635R',
                'filter4' : '---',
                'filter5' : '---',
                'scale' : 'linear',
                'min_wave' : 400,
                'max_wave' : 1600,
                'laser_wave' : '532',
                'scale_checkbox': 0}
        self.filter0.set(default_state['filter0'])
        self.filter1.set(default_state['filter1'])
        self.filter2.set(default_state['filter2'])
        self.dic_mirror.set(default_state['dic_mirror'])
        self.filter3.set(default_state['filter3'])
        self.filter4.set(default_state['filter4'])
        self.filter5.set(default_state['filter5'])
        self.update_graphs()

    def quit(self):
        self.state = {'filter0' : self.filter0.get(),
                'filter1' : self.filter1.get(),
                'filter2' : self.filter2.get(),
                'dic_mirror' : self.dic_mirror.get(),
                'filter3': self.filter3.get(),
                'filter4': self.filter4.get(),
                'filter5': self.filter5.get(),
                'scale' : self.scale_type.get(),
                'min_wave' : int(self.waveminbox.get()),
                'max_wave' : int(self.wavemaxbox.get()),
                'scale_checkbox': self.log_scale.get(),
                'laser_wave' : str(int(self.laserbox.get()))}
        try:
            pickle.dump(self.state, open('filter_GUI_state.pkl','wb'))
        except:
            print("Problem saving state of GUI.")
            pass
        root.destroy()
    
    def set_lims(self):
        self.ax1.set_xlim(int(self.waveminbox.get()), int(self.wavemaxbox.get()))
        laser_line = float(self.laserbox.get())
        self.laserline.set_xdata([laser_line]*2)
        self.laserline.set_ydata([1E-6,1])
        self.canvas.draw()
        self.ax2.set_xlim(int(self.waveminbox.get()), int(self.wavemaxbox.get()))
        laser_line = float(self.laserbox.get())
        self.laserline2.set_xdata([laser_line]*2)
        self.laserline2.set_ydata([1E-6,1])
        self.canvas2.draw()

    def annotate_point1(self,event):
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

    def annotate_point2(self,event):
        if event.inaxes is not None:
            stringo = '(%.2f,\n%.3f)' % (event.xdata, event.ydata)
            print(event.xdata, event.ydata)
            self.ax2.plot([event.xdata], [event.ydata],'wx')
            if event.ydata > 0.5:
                ytext = event.ydata - 0.4
            else:
                ytext = event.ydata + 0.4
            self.ax2.annotate(stringo, xy = (event.xdata+1,event.ydata),
                              xytext=(event.xdata,ytext),
            arrowprops=dict(facecolor='white', width=0.5, headwidth = 5,
                            headlength = 5, shrink=0.05), ha='center',
                            backgroundcolor='black')
            self.canvas2.draw()
        else:
            print('Clicked ouside axes bounds but inside plot window')

    def update_graph1(self, filtername=''):
        self.fig.legends = []
        self.ax1.clear()
        filtcounter = 0
        for filtervar in self.ex_filtervars:
            filtername = filtervar.get()
            if filtername == '---':
                continue
            filtcounter = filtcounter+1
            waves = self.filters[filtername]['data'][:,0]
            transmi = self.filters[filtername]['data'][:,1]
            plabel = "%s (%d$^o$)" % (filtername, self.filters[filtername]['AOI'])
            self.ax1.plot(waves, transmi, lw=2,
                        label = plabel)
        if self.dic_mirror.get() != '---':
            filtername = self.dic_mirror.get()
            waves = self.filters[filtername]['data'][:,0]
            transmi = 1 - self.filters[filtername]['data'][:,1]
            plabel = "%s (%d$^o$)" % (filtername, self.filters[filtername]['AOI'])
            self.ax1.plot(waves, transmi, 'g-.', lw=2,
                            label = plabel)
        if filtcounter >= 1:
            waves = self.filters[self.filter0.get()]['data'][:,0]
            transmi = self.filters[self.filter0.get()]['data'][:,1]
            for filtervar in self.ex_filtervars[1:]:
                filtername = filtervar.get()
                if filtername == '---':
                    continue
                transmi = transmi*self.filters[filtername]['data'][:,1]
            if self.dic_mirror.get() != '---':
                filtername = self.dic_mirror.get()
                waves = self.filters[filtername]['data'][:,0]
                transmi = transmi*(1 - self.filters[filtername]['data'][:,1])
                self.ax1.plot(waves, transmi, 'r:', lw=2,
                                label = 'Excitation Transmission')
            else:
                self.ax1.plot(waves, transmi, 'r:', lw=2,
                                label = 'Excitation Transmission')
        num_cols = filtcounter + 1
        if self.dic_mirror.get() != '---':
            num_cols = num_cols + 1
        if self.log_scale.get():
            scale_type = 'log'
        else:
            scale_type = 'linear'
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

    def update_graphs(self, filtername=''):
        self.update_graph1('')
        self.update_graph2('')

    def update_graph2(self, filtername=''):
        self.fig2.legends = []
        self.ax2.clear()
        filtcounter = 0
        for filtervar in self.em_filtervars:
            filtername = filtervar.get()
            if filtername == '---':
                continue
            filtcounter = filtcounter + 1
            waves = self.filters[filtername]['data'][:,0]
            transmi = self.filters[filtername]['data'][:,1]
            plabel = "%s (%d$^o$)" % (filtername, self.filters[filtername]['AOI'])
            self.ax2.plot(waves, transmi, lw=2,
                        label = plabel)
        if self.dic_mirror.get() != '---':
            filtername = self.dic_mirror.get()
            waves = self.filters[filtername]['data'][:,0]
            transmi = self.filters[filtername]['data'][:,1]
            plabel = "%s (%d$^o$)" % (filtername, self.filters[filtername]['AOI'])
            self.ax2.plot(waves, transmi, 'g-.', lw=2,
                            label = plabel)
        if filtcounter >= 1:
            waves = self.filters[self.filter3.get()]['data'][:,0]
            transmi = self.filters[self.filter3.get()]['data'][:,1]
            for filtervar in self.em_filtervars[1:]:
                filtername = filtervar.get()
                if filtername == '---':
                    continue
                transmi = transmi*self.filters[filtername]['data'][:,1]
            if self.dic_mirror.get() != '---':
                filtername = self.dic_mirror.get()
                transmi = transmi*(self.filters[filtername]['data'][:,1])
                self.ax2.plot(waves, transmi, 'r:', lw=2,
                                label = 'Emission Transmission')
            else:
                self.ax2.plot(waves, transmi, 'r:', lw=2,
                                label = 'Emission Transmission')
        num_cols = filtcounter + 1
        if self.dic_mirror.get() != '---':
            num_cols = num_cols + 1
        if self.log_scale.get():
            scale_type = 'log'
        else:
            scale_type = 'linear'
        # scale_type = self.scale_type.get()
        self.ax2.set_xlim(int(self.waveminbox.get()), int(self.wavemaxbox.get()))
        if scale_type == 'linear':
            self.ax2.set_ylim(0, 1)
        else:
            self.ax2.set_ylim(1e-6, 2)
            self.ax2.set_yscale(scale_type)
        laser_line = float(self.laserbox.get())
        self.laserline2, = self.ax2.plot([laser_line]*2,[1E-6,1],'w--')
        self.ax2.set_xlabel('$\lambda$/nm')
        self.ax2.set_ylabel('T')
        self.fig2.legend(loc='upper center', ncol = num_cols)
        self.canvas2.draw()

root = tk.Tk()
root.resizable(height = None, width = None)
root.configure(bg='black')
root.title('Filters')
root.winfo_toplevel().title = "Simple Prog"
app = App(root)
app.pack()
root.eval('tk::PlaceWindow . center')
root.mainloop()
