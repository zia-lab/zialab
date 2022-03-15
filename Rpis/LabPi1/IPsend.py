#!/usr/bin/python3.7
import subprocess
import re
import requests
ifconfigText=str(subprocess.check_output(["ifconfig"]))
hwAddr_wifi=['']
hwAddr_ethernet=['']

try:
        hwAddr_wifi=re.findall('ether ([0-9a-f:]{17})',ifconfigText)[1]
except:
        pass

try:
        hwAddr_ethernet=re.findall('ether ([0-9a-f:]{17})',ifconfigText)[0]
except:
        pass

ipAddr_wifi=re.findall('wlan0.+inet (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})',ifconfigText,re.DOTALL)
ipAddr_ethernet=re.findall('eth0.+?inet (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})',ifconfigText,re.DOTALL)

deviceType="Raspberry Pi 3 Model B"
deviceName="LabPi1"
webAppURL="see in hardware locations"
dataToSend={"Device Name":deviceName,"Device Type":deviceType,
"MAC_wifi":hwAddr_wifi,"MAC_ethernet":hwAddr_ethernet,"IP_wifi":ipAddr_wifi,"IP_ethernet":ipAddr_ethernet}
response = requests.get(webAppURL,params=dataToSend)
