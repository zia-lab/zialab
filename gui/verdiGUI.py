#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import random
import sys
from remoteVerdi import RemoteVerdi


class VerdiGUI():
    bg_color = 'white'
    text_color = '#00ff00'
    text_color = 'black'

    def __init__(self, verbose=True):
        self.IP = '10.9.93.186'
        self.verbose = verbose
        self.platform = sys.platform
        self.verdi = RemoteVerdi(IP=self.IP)
        self.root = tk.Tk()
        self.root.title("Verdi")
#        self.root.geometry("%dx%d" % (self.width, self.height))
        self.verdi_on = tk.PhotoImage(file='verdi_on.gif')
        self.verdi_off = tk.PhotoImage(file='verdi_off.gif')
        self.root.resizable(False, False)
        self.root.configure(background=self.bg_color)
        self.frame = tk.Frame()

        # Background image
        if (sys.platform == 'win32'):
            self.top_image = tk.PhotoImage(file='verdi_background_win.gif')
        elif (self.platform == 'darwin'):
            self.top_image = tk.PhotoImage(file='verdi_background_darwin.gif')
        elif (self.platform == 'linux'):
            self.top_image = tk.PhotoImage(file='verdi_background_linux.gif')
        self.top_label = tk.Label(self.frame,
                                  image=self.top_image,
                                  borderwidth=0,
                                  highlightthickness=0)
        self.top_label.place(x=0, y=0)

        # Power display
        power_str = '{0:.0f} mW'.format(1000 * self.get_regpower())
        self.power_display = tk.Label(self.frame,
                                      text=power_str)
        self.power_display.config(font=("TkDefaultFont", 40))
        self.power_display.grid(row=1, column=0,
                                columnspan=3, pady=(80, 10))

        # Entry field for changing power
        self.entry_field_left = tk.Label(self.frame, text='Set')
        self.entry_field_left.grid(row=2, column=0, padx=5)
        self.entry_field = tk.Entry(self.frame, justify='center')
        self.entry_field.bind('<Return>', self.change_power)
        self.entry_field.grid(row=2, column=1, columnspan=1)
        self.entry_field_right = tk.Label(self.frame, text='mW')
        self.entry_field_right.grid(row=2, column=2, padx=5)

        # Increment section
        self.left_increment_btn = tk.Button(self.frame,
                                            text="↓",
                                            command=self.decreasepower)
        self.left_increment_btn.grid(row=3, column=0)
        self.increment_field = tk.Entry(self.frame, justify='center')
        self.increment_field.insert(0, '10')
        self.increment_field.grid(row=3, column=1)
        self.left_increment_btn = tk.Button(self.frame, text="↑",
                                            command=self.increasepower)
        self.left_increment_btn.grid(row=3, column=2)

        # IP field
        self.ip_field = tk.Label(self.frame, text='IP: ' + self.IP,
                                 justify='center')
        self.ip_field.config(font=("TkDefaultFont", 12, "underline"))
        self.ip_field.grid(row=4, column=1, pady=(5, 0))

        # Shutter button
        self.toggle_btn = tk.Button(self.frame, image=self.verdi_on,
                                    command=self.toggle, bd=0, relief='flat')
        self.shutter_state = self.get_shutter()
        # Query the current state of the shutter
        if self.shutter_state == 1:
            self.toggle_btn.configure(image=self.verdi_on)
        else:
            self.toggle_btn.configure(image=self.verdi_off)
        self.toggle_btn.grid(row=5,
                             column=1,
                             pady=(5, 20))

        # Pack it all up
        self.frame.grid(padx=5, pady=(4, 4))

    def change_power(self, x):
        self.verdi.set_power(0.001 * float(self.entry_field.get()))
        power_str = '{0:.0f} mW'.format(1000*self.get_regpower())
        self.power_display.config(text=power_str)
        return None

    def get_regpower(self):
        return self.verdi.get_regpower()

    def decreasepower(self):
        current_power = float(self.get_regpower())
        new_power = current_power - 0.001 * float(self.increment_field.get())
        self.verdi.set_power(new_power)
        power_str = '{0:.0f} mW'.format(1000*self.get_regpower())
        self.power_display.config(text=power_str)
        return None

    def increasepower(self):
        current_power = float(self.get_regpower())
        new_power = current_power + 0.001 * float(self.increment_field.get())
        self.verdi.set_power(new_power)
        power_str = '{0:.0f} mW'.format(1000*self.get_regpower())
        self.power_display.config(text=power_str)
        return None

    def get_shutter(self):
        return self.verdi.get_shutter()

    def toggle(self):
        if self.shutter_state == 1:
            self.verdi.set_shutter(0)
            self.shutter_state = 0
        else:
            self.verdi.set_shutter(1)
            self.shutter_state = 1
        if self.shutter_state == 1:
            self.toggle_btn.configure(image=self.verdi_on)
        else:
            self.toggle_btn.configure(image=self.verdi_off)

    def run(self):
        if (self.verbose is True):
            self.root.update()
            print(self.root.winfo_width())
            print(self.root.winfo_height())
        self.root.mainloop()


if __name__ == '__main__':
    verdiGUI = VerdiGUI()
    verdiGUI.run()
