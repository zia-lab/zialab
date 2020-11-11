#!/usr/bin/python3
# read voltage on the adc and save it to the log file

import ADS1x15
from time import time, sleep

adc = ADS1x15.ADS1115()
adc_channel = 0
adc_gain = 1
log_file = '/home/pi/Log/volt.log'
dt = 2 # resolution of log in seconds : about 325 Mb per year of log

now = time()

while True:
    while (time() - now) <= dt: # wait until timer is
        sleep(0.1)
    now = time()
    voltage  = '{:.3e}'.format(adc.read_voltage(adc_channel, adc_gain))
    now_str = str(int(now))
    with open (log_file,"a") as logfile:
        logfile.write('%s,%s\n' % (now_str, voltage))
