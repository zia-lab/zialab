# Coded by David on Jul 18 2019
# To be used with the Thorlabs Si photodiode PDA36A,
# and a ADS1115 ADC connected to a Raspberry Pi.
# The one in lab is reading the voltage across a 50 Ohm

#    _____ _                _       _
#   |_   _| |__   ___  _ __| | __ _| |__  ___
#     | | | '_ \ / _ \| '__| |/ _` | '_ \/ __|
#     | | | | | | (_) | |  | | (_| | |_) \__ \
#     |_| |_| |_|\___/|_|  |_|\__,_|_.__/|___/
#
#     ____  ____    _    _____  __     _
#    |  _ \|  _ \  / \  |___ / / /_   / \
#    | |_) | | | |/ _ \   |_ \| '_ \ / _ \
#    |  __/| |_| / ___ \ ___) | (_) / ___ \
#    |_|   |____/_/   \_\____/ \___/_/   \_\
#
#
#            NOxxOKXNNKOxx0XXKOO0XNNK0OO0XWNX0O0XNX00OO0XW
#          WO;.....'''......'....',,.....',,'...','.....':xN
#        NOc..,cl:..';:clc:;;:clc:;;:cllc:::ccc:::;..;cc,..;kN
#     NOl;..':ooo:..cdooooddoooooooooooooodoooooodl..;oooc,..,cxX
#    Xc..';coooooc..cdl:;::cclooooooooollccc:;;coo:..cooooolc;'.,O
#    x..;ooooooooo,.,ol:;;;;::clloooolcc:::::::col'.;oooooooooo,.cN
#    d..ldoooooooo:..co:;;:::clclooolcccc:;;,,,coc..cdooooooooo;.:X
#    O..:ooooooooo;..coolllccc:;coool:;;::cccloodc..cdooooooodl..oW
#    No..:oooooooo,.'loooodddol;,:ol;':loddddooool'.;ooooooooc'.cX
#     Nx,.':oooooo,.,oooolccccoo:,cc'coolcc::loooc..:oooooo:'..oX
#       Xx;..:oooo;.'lool;:c:;;ooloololc;:::;;ooo:..cdoooc'.,dKW
#         Nx'.;ooo:..cooo:;::;:odooooool:;;:;:ooo;..looo;.'xN
#          Wk..:ol,.'looooc:clol:;,,;:loolcclooooc..;lc'.:K
#           Wx..'....,looooool,''.  .''.,cooooooo;......oX
#            WOl:cx0o.,odoooo,.;;.  .;;..'ldoooo;.:xlco0W
#                   Nl.;ooooo:..,.  .'...;oooooc.,0
#                    Kc.,cooooc;'....';;cooooo:.'kW
#                     X:..,cooooooooooddoodoc,..oW
#                     Nl.';,,;;::;;;;,,;;;;,''. :X
#                     0,..,llc:::ccllll:cc::;''..lX
#                    Nl.,c,';clc::;;;::;:c;',:ol'.cX
#                   Nd.'looc;;;;:cccc::::::looooc..cX
#                  Nd..coooooddoooooooooooooooooo;..:K
#              NOll;. ,odlclooooooooooooooooolclo;...,ld0W
#             Wo.':;..,oo,.:do;':ooooooo:,cod:.;l'.;:;;'.dW
#             Nl.,cl:..:c..ldl..:ooooool,.;odl'';..coll;.:N
#              Xd:;,.. ...;od:..cdoooolc'.;ooo;......,,,:OW
#                WK:.....'ldo;..ldooodl:..;ooo:. .cox0XXW
#                Nl.;llc,:ool'..,;::cc,...;oodl'..':kW
#                X;.:lllloodl::,..,'..';;;:ooooccl;.'0
#                WO:....,;:;;::,.:XO..looooooollc:;.'O
#                  N0OOd:,,;:;',lK Nl...,,,,,,..'',:kW
#                       WNNWWNXNW   NOollodolldkKXNW
#
#
#

import numpy as np
import sys
from zialab.instruments import ADS1x15

class PhotoDiode:
    def __init__(self, settings={}):
        self.min_wavelength = 352
        self.max_wavelength = 1099
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
        self.responsivity = np.array([[352,0.0479292],[383.538,0.0483439],
            [414.84,0.0790784],[455.3,0.122153],[500.043,0.165116],
            [555.453,0.224512],[600.572,0.275834],[658.676,0.344122],
            [698.6,0.387234],[750.875,0.44838],[800.551,0.498523],
            [843.752,0.539818],[887.262,0.578865],[927.237,0.609987],
            [960.269,0.630814],[986.415,0.63086],[1009.17,0.61136],
            [1021.59,0.566442],[1033.3,0.509277],[1045.2,0.436869],
            [1055.49,0.351615],[1066.72,0.271641],[1082.39,0.204956],
            [1099,0.14756]]) # wavelength in nm, responsivity in A/W
        self.defaults = {
            'scale_factor': 0.5, # depends on the load resistance: 50 Ohm / (50 Ohm + R_load)
            'wavelength': 532,
            'adc_channel': 0,
            'adc_gain': 1,
            'dc_samples': 100,
            'gain': '0 dB',
            'gain_load': '50 Ohm'
            }
        if settings: # if settings are given, then set it up like so
            self.settings = settings
        else: # else use defaults
            print("Using default settings.")
            print(self.defaults)
            self.settings = self.defaults
        # checkpoints
        assert self.settings['gain'] in self.gains, "Invalid gain setting."
        assert self.settings['gain_load'] in ['50 Ohm','Hi-Z'], "Invaling gain_load setting."
        assert self.settings['scale_factor'] > 0, "Invalid scale factor."
        assert self.settings['adc_channel'] in [0,1,2,3], "Invalid ADC channel."
        assert self.adc_gain in [1,2,4,8,16], "Invalid ADC gain level."
        self.gain = self.gains[self.settings['gain']][self.settings['gain_load']]
        self.shorname = 'PDA36A'
        self.fullname = 'Thorlabs - Si Switchable Gain Detector PDA36A'
        self.platform = sys.platform
        self.manual_fname = './zialab/Manuals/'+self.fullname + '.pdf'
        self.scale_factor = self.settings['scale_factor']
        self.adc_gain = self.settings['adc_gain']
        self.ADC = ADS1115(gain = self.adc_gain) # create an instance of the ADC
        self.wavelength = self.settings['wavelength']
        assert self.min_wavelength <= self.wavelength <= self.max_wavelength, "Wavelength outside of range."
        self.responsivity = np.interp(self.wavelength, responsivity[:,0], responsivity[:,1])
        self.adc_channel = self.settings['adc_channel']
        self.dc_samples = self.settings['dc_samples']
    def manual(self):
        '''open the pdf manual'''
        platform_open_cmds = {'linux':'xdg-open','darwin':'open'}
        try:
            print("Opening the manual.")
            os.system('%s "%s"' % (platform_open_cmds[self.platform],self.manual_fname))
        except:
            print("wups, could not open")
    def read_cw_optical_power(self, wavelength):
        '''returns optical power in Watts along with the statistical uncertainty'''
        # Update wavelength and responsivity if necessary
        if wavelength != self.wavelength:
            self.wavelength = wavelength
            assert self.min_wavelength <= self.wavelength <= self.max_wavelength, "Wavelength outside of range."
            self.responsivity = np.interp(self.wavelength, responsivity[:,0], responsivity[:,1])
        adc_voltages = [self.ADC.read_voltage(self.adc_channel, self.adc_gain) for i in range(self.dc_samples)]
        mean_voltage = np.mean(adc_voltages)
        std_voltage = np.std(adc_voltages)
        rel_uncert_in_voltage = std_voltage/mean_voltage
        optical_power = mean_voltage / (self.gain * self.responsivity * self.scale_factor)
        optical_power_uncertainty = optical_power * rel_uncert_in_voltage
        return optical_power, optical_power_uncertainty
