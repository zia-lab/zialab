#!/usr/bin/env python3

import requests
from time import sleep
num_retries = 10
wait_between_retries = 1

class Flipper():
    '''
    Control a flip mirror through the Rapsberry Pi that is attached to it.
    '''
    def __init__(self,IP='10.9.93.186'):
        self.IP = IP
    def flip(self,state):
        '''
        Lower or raise the flip mirror.
        '''
        state = state.lower()
        if state == "up":
            url = 'http://%s:7777/flipmirror/state?state=%s' % (self.IP, state)
        elif state == "down":
            url = 'http://%s:7777/flipmirror/state?state=%s' % (self.IP, state)
        else:
            return "Invalid state."
        for _ in range(num_retries):
            try:
                rep = str(requests.get(url, timeout=1).content.decode())
                return rep
            except:
                print("Error in reply...")
                print("Retrying...")
                sleep(wait_between_retries)
        return ""
