#!/usr/bin/env python3

import requests

class RemoteVerdi():
    '''
    Use Verdi through the Rapsberry Pi is attached to it.
    '''
    def __init__(self,IP='10.9.93.159'):
        self.IP = IP
    def set_shutter(self,shut):
        '''
        Open (1) or close (0) the shutter. Function returns the queried state of
        the shutter right after being set.
        '''
        url = 'http://%s:7777/setverdi/shutter?shutter=%d' % (self.IP, shut)
        return int(requests.get(url, timeout=1).content)

    def get_shutter(self):
        '''
        Open (1) or close (0) the shutter. Function returns the queried state of
        the shutter right after being set.
        '''
        return int(requests.get('http://%s:7777/qverdi/shutter' % (self.IP)).content)

    def set_power(self, power):
        '''
        Set the power of Verdi in W. Function returns the power queried on the
        Verdi after being set.
        '''
        return float(requests.get('http://%s:7777/setverdi/power?power=%f' % (self.IP, power)).content)

    def get_calpower(self):
        '''
        Get the calibrated power in W.
        '''
        return float(requests.get('http://%s:7777/qverdi/calpower' % self.IP).content)

    def get_regpower(self):
        '''
        Get the regulated power in W.
        '''
        return float(requests.get('http://%s:7777/qverdi/regpower' % self.IP).content)