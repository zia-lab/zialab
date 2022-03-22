#!/usr/bin/env python3

# Put together by David on Jun of 2021

import requests
from time import sleep
from tenacity import retry, stop_after_attempt

max_retries = 100

class LS335:
    """
    Class controls the LakeShore 335 Temperature Controller via a TCP
    relay to a serial connection to the controller.
    """

    def __init__(self,tcp_port="7777"):
        self.terminator = "\r\n"
        self.url = 'http://127.0.0.1:%s/commander' % tcp_port
        self.range_dict = {"Off":"0","Low":"1","Medium":"2","High":"3"}
        self.range_options = ["Off","Low","Medium","High"]

    def query(self, cmd):
        req = requests.get(self.url, params={'cmd': cmd})
        return req.text

    @retry(stop=stop_after_attempt(max_retries))
    def getSP(self): #checked
        """
        Get the current temperature setpoint for heater 1.
        """
        set_point = float(self.query("SETP? 1").split(self.terminator)[-2])
        return set_point

    @retry(stop=stop_after_attempt(max_retries))
    def setSP(self, set_temp): #checked
        """
        Set the temperature setpoint as given in Kelvin.
        """
        self.query("SETP 1,%s" % str(set_temp))

    @retry(stop=stop_after_attempt(max_retries))
    def getRange(self): #checked
        '''
        Get the current range for heater 1.
        '''
        range1 = self.range_options[int(self.query("RANGE? 1")[-3:-2])]
        return range1

    @retry(stop=stop_after_attempt(max_retries))
    def getRamp(self): #checked
        '''
        Get the current ramp rate in K/min.
        '''
        ramp_rate = float(self.query("RAMP? 1").split(self.terminator)[0].split(',')[1])
        return ramp_rate

    @retry(stop=stop_after_attempt(max_retries))
    def setRamp(self, ramp_rate): #checked
        '''
        Set the ramp rate for heater 1, and echo its set value.
        '''
        self.query("RAMP 1,1,%.1f" % ramp_rate)
        return self.getRamp()

    @retry(stop=stop_after_attempt(max_retries))
    def setRange(self,rangeStr): #checked
        """
        Update the heater range. Valid values are ["Off","Low","Medium","High"]
        """
        self.query("RANGE 1," + self.range_dict[rangeStr])
        the_range = self.getRange()
        return the_range

    @retry(stop=stop_after_attempt(max_retries))
    def getTemp(self): # checked
        """
        Returns the current thermometer reading in K.
        """
        temp = float(self.query("KRDG? 1").split(self.terminator)[-2])
        return temp

    @retry(stop=stop_after_attempt(max_retries))
    def getHeat(self): #checked
        """
        Return the fraction of the total heater range that heater 1 is using.
        """
        return float(self.query("HTR? 1").split(self.terminator)[-2])/100

    @retry(stop=stop_after_attempt(max_retries))
    def off(self): #checkd
        """
        Turns off heater 1
        """
        self.setRange("Off")
