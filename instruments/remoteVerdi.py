#!/usr/bin/env python3

import requests
from time import sleep
num_retries = 10
wait_between_retries = 1

class RemoteVerdi():
    '''
    Use Verdi through the Rapsberry Pi that is attached to it.
    '''
    def __init__(self,IP='172.18.129.48'):
        self.IP = IP
    def set_shutter(self,shut):
        '''
        Open (1) or close (0) the shutter. Function returns the queried state of
        the shutter right after being set.
        '''
        url = 'http://%s:7777/setverdi/shutter?shutter=%d' % (self.IP, shut)
        for _ in range(num_retries):
            try:
                rep = int(requests.get(url, timeout=1).content)
                return rep
            except:
                print("Error in reply...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""

    def get_shutter(self):
        '''
        Open (1) or close (0) the shutter. Function returns the queried state of
        the shutter right after being set.
        '''
        for _ in range(num_retries):
            try:
                rep = int(requests.get('http://%s:7777/qverdi/shutter' % (self.IP)).content)
                return rep
            except:
                print("Error found...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""

    def set_power(self, power):
        '''
        Set the power of Verdi in W. Function returns the power queried on the
        Verdi after being set.
        '''
        for _ in range(num_retries):
            try:
                rep = float(requests.get('http://%s:7777/setverdi/power?power=%f' % (self.IP, power)).content)
                return rep
            except:
                print("Error found...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""

    def get_calpower(self):
        '''
        Get the calibrated power in W.
        '''
        for _ in range(num_retries):
            try:
                rep = float(requests.get('http://%s:7777/qverdi/calpower' % self.IP).content)
                return rep
            except:
                print("Error found...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""

    def get_regpower(self):
        '''
        Get the regulated power in W.
        '''
        for _ in range(num_retries):
            try:
                rep = float(requests.get('http://%s:7777/qverdi/regpower' % self.IP).content)
                return rep
            except:
                print("Error found...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""
