#!/usr/bin/env python3

# Module for turning on and off the top light on the cryostat

import requests

class Peye():
    def __init__(self):
        self.url = 'http://10.9.93.240:7777/'
    def on(self):
        requests.get('http://10.9.93.240:7777/'+'uon')
    def off(self):
        requests.get('http://10.9.93.240:7777/'+'uoff')
