#!/usr/bin/env python3

# Put together by David on Aug of 2020
# based on Jonathan Van Schenck's code https://github.com/jonathanvanschenck/LS335-Python

import serial, sys, os, atexit
from time import sleep
import numpy as np

class LS335:
    """
    Class controls the LakeShore 335 Temperature Controller via a usb connection
    Inputs:
    comport:            Name of the port used by the USB. See task manager for details.

    Variables:
    .ser:               pySerial connection to the LS335
    ._t:                String holding the termination characters for LS335 serial connection ("\r\n")
    ._rdic:             Dictionary converting heater range names to their terminal index
    ._rlist:            Numpy array holding heater range names in terminal index order
    ._pid:              Numpy array holding most recently checked PID values for heater 1 and 2
    ._sp:               Numpy array holding most recently checked setpoint values for heater 1 and 2
    ._range:            Numpy array holding most recently checked Heater range names for heater 1 and 2

    Methods:
    .close()            Closes the pySerial connection to the LS335
    .off()              Turns off all heaters
    .query(message)     Writes "message" to serial port, after adding appropriate termination characters,
                          then it returns the serial port's response
    .getTemp(which=1,   Returns the current read on thermometer "A" (which=1) or "B" (which=2) in units of
             unit="K")    kelvin (unit="K") or celcius (unit="C")
    .getHeat(which=1)   Returns the proportion of the heater range that heater 1/2 (which=1/2) is using
    .getPID()           Updates ._pid and then returns the value of ._pid
    .setPID(...)        Allows modification of pid parameters, and then updates ._pid
    .getSP()            Updates ._sp and then returns the value of ._sp
    .setSP(Temp,        Changes the setpoint of heater 1/2 (which=1/2) to Temp (units of K), then updates
           which=1)       the value of ._sp
    .getRange()         Updates ._range and then returns the value of ._range
    .setRange(...)      Allows modification of heater ranges, and then updates ._range
    """

    def __init__(self,comport="COM3"):
        self.ser = serial.Serial(comport,baudrate=57600,parity=serial.PARITY_ODD,stopbits=1,bytesize=7,timeout=0.1)
        self._t = "\r\n"
        self._rdic = {"Off":"0","Low":"1","Medium":"2","High":"3"}
        self._rlist = np.array(["Off","Low","Medium","High"])
        self.getPID()
        self.getSP()
        self.getRange()
        self.setPID(pid=(40,20,100))

    def getPID(self):
        """
        Checks the current PID parameters for heater 1&2, updates ._pid and then returns the value.

        Ouput:
        ._pid:      The current PID parameters. Format: np.array([[p1,i1,d1],[p2,i2,d2]])
        """
        self._pid = np.array([[float(i[1:]) for i in (self.query("PID? "+j).split(self._t)[-2]).split(",")[-3:]] for j in ["1","2"]])
        return self._pid

    def setPID(self,pid=None,p=None,i=None,d=None,which=1):
        """
        Allows updating of PID parameters. User can change either heater 1 (which=1) or heater 2 (which=2).
        The specification of PID parameters can either be via a 1d tuple: (p,i,d) by specifying "pid". Else
        any of p, i or d can be seperately specified to update only that parameter.

        Inputs:
        pid:        1-tuple containing desired new PID parameters: (p,i,d). Specifying "None" for any
                      element will result in that parameter NOT being modified from it's current value
        p:          New p value for PID controller (See manual). Specifying "None" leaves value unchanged
        i:          New i value for PID controller (See manual). Specifying "None" leaves value unchanged
        d:          New d value for PID controller (See manual). Specifying "None" leaves value unchanged
        which:      Integer specifying which heater to update. Must take value 1 or 2.

        Outputs:
        ._pid:      The current PID parameters. Format: np.array([[p1,i1,d1],[p2,i2,d2]])
        """
        if pid:
            pt,it,dt=pid
        else:
            pt,it,dt=p,i,d
        pt2,it2,dt2 = self.getPID()[which-1]
        if pt:
            assert pt>=0.1 and pt<=1000
            pt2=1*pt
        if it:
            assert it>=0.1 and it<=1000
            it2=1*it
        if dt:
            assert dt>=0 and dt<=200
            dt2=1*dt
        self.query("PID "+str(which)+","+str(pt2)+","+str(it2)+","+str(dt2))
        return self.getPID()

    def getSP(self):
        """
        Checks the current setpoints, updates ._sp and then returns the value of ._sp

        Output:
        ._sp:       The current setpoints for heaters 1/2 in units of K. Format: np.array([sp1,sp2])
        """
        self._sp = np.array([float(self.query("SETP? "+j).split(self._t)[-2]) for j in ["1","2"]])
        return self._sp

    def setSP(self,Temp,which=1):
        """
        Allows updating of setpoint value. User can change either heater 1 (which=1) or heater 2 (which=2).
        SP values must be cited in unites of Kelvin

        Input:
        Temp:       New temperature setpoint value (units of Kelvin)
        which:      Integer specifying which heater to update. Must take value 1 or 2.

        Output:
        ._sp:       The current setpoints for heaters 1/2 in units of K. Format: np.array([sp1,sp2])
        """
        self.query("SETP "+str(which)+","+str(Temp))
        return self.getSP()

    def getRange(self):
        """
        Checks the current heater range names, updates ._range and then returns the value of ._range

        Output:
        ._range:     The current heater range names for heaters 1/2. Format: np.array([range1,range2])
        """
        self._range = [self._rlist[int(self.query("RANGE? "+j)[-3:-2])] for j in ["1","2"]]
        return self._range

    def setRange(self,rangeStr=None,rangeInd=None,which=1):
        """
        Allows updating of heater range value. User can change either heater 1 (which=1) or heater 2 (which=2).
        User can update either using the range name: ["Off","Low","Medium","High"], or by specifying the
        corresponding range name index: [0,1,2,3]. Specifying both will result in the index overriding
        the name.

        Input:
        rangeStr:       A string containing the desired heater range. Value must be a string from the list:
                          ["Off","Low","Medium","High"]
        rangeInd:       An integer specifying the desired heater range. Value must be from the list: [0,1,2,3]
        which:      Integer specifying which heater to update. Must take value 1 or 2.

        Output:
        ._range:        The current heater range names for heaters 1/2. Format: np.array([range1,range2])
        """
        if rangeStr:
            self.query("RANGE "+str(which)+","+self._rdic[rangeStr])
            return self.getRange()
        if rangeInd:
            assert rangeInd in [0,1,2,3]
            self.query("RANGE "+str(which)+","+str(rangeInd))
            return self.getRange()
        return self.getRange()

    def setSmartTemp(self, temp):
        if temp <= 20:
            self.setSP(temp, 1)
            # self.setPID(pid=(30,50,50))
            self.setRange("Medium")
        if temp <= 300:
            self.setSP(temp, 1)
            # self.setPID(pid=(40,20,100))
            self.setRange("High")

    def getTemp(self,which=1,unit="K"):
        """
        Returns the current temperature value

        Input:
        which:      Integer specifying which heater to check. Must take value 1 or 2.
        unit:       A string specifying either units of kelvin ("K") or celcius ("C")

        Output:
        res:        A float holding the current temperature
        """
        return float(self.query(unit+"RDG? "+str(which)).split(self._t)[-2])

    def getHeat(self,which=1):
        """
        Returns the current proportion of the total heater range that the heater is using.

        Input:
        which:      Integer specifying which heater to check. Must take value 1 or 2.

        Output:
        res:        A float from 0.0 to 1.0 specifying the heaters power
        """
        return float(self.query("HTR? "+str(which)).split(self._t)[-2])/100

    def off(self):
        """
        Shuts down all heaters
        """
        self.setRange("Off",which=1)
        self.setRange("Off",which=2)

    def query(self,message):
        """
        Allows user to send messages directly to the serial port connection (after attaching
        appropriate termination characters) and returns the result

        Input:
        message:    UTF-8 string to send to via the serial port (Do not include termination characters)

        Output:
        res:        A UTF-8 string containing the serial port response
        """
        self.ser.write((str(message)+self._t).encode())
        return self.ser.read(1000).decode()

    def close(self):
        """
        Closes pySerial connection
        """
        self.ser.close()
