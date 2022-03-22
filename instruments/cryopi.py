#!/usr/bin/env python3

import requests
from time import sleep
num_retries = 10
wait_between_retries = 1

class CryoPi():
    '''
    Flip or change LED power.
    '''
    def __init__(self,IP='10.9.93.247'):
        self.IP = IP

    def set_flipper(self,flipstate):
        '''
        Raise (up) or lower (down) the flip mirror.
        '''
        flipstate = flipstate.lower()
        assert flipstate in ["up","down"], "invalid mirror state"
        url = 'http://%s:7777/flipmirror/state?state=%s' % (self.IP, flipstate)
        for _ in range(num_retries):
            try:
                rep = str(requests.get(url, timeout=1).content.decode())
                return rep
            except:
                print("Error in reply...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""

    def set_led(self, led_power):
        '''
        Sets the power of the white light illumination using the MOD mode
        on the LED power supply.
        led_power must be between 0 and 100.
        '''
        led_power = int(led_power)
        url = 'http://%s:7777/led/power?power=%d' % (self.IP, led_power)
        for _ in range(num_retries):
            try:
                rep = str(requests.get(url, timeout=1).content.decode())
                return rep
            except:
                print("Error in reply...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""
