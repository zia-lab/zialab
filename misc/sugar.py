import numpy as np
import http.client, urllib
import sys
import ssl
import requests
import winsound
import time, os

ssl.match_hostname = lambda cert, hostname: True
codebase_dir = 'D:/Google Drive/Zia Lab/Codebase/'
log_dir = 'D:/Google Drive/Zia Lab/Log'
data_dir = os.path.join(log_dir,'Data')
graphs_dir = os.path.join(log_dir,'Graphs')
platform = sys.platform

def wait(wait_duration=0.1):
    time.sleep(wait_duration)

def bell():
    winsound.PlaySound(os.path.join(codebase_dir,'sounds','bell.wav'),
                   winsound.SND_ASYNC)

def send_message(message):
    conn = http.client.HTTPSConnection("api.pushover.net",443)
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "aqxvnvfq42adpf78g9pwmphse9c2un",
        "user": "uqhx6qfvn87dtfz5dhk71hf2xh1iwu",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    return None

def roundsigfigs(x,sig_figs):
    '''Takes a number x and rounds it to have the
    give number of significant figures.'''
    return float(np.format_float_positional(x,
                                            precision=sig_figs,
                                            unique=False,
                                            fractional=False,
                                            trim='k'))

def wav2RGB(wavelength):
    '''
    Credits: the internet
    '''
    w = int(wavelength)
    if w < 380:
        w = 380
    if w > 780:
        w = 780
    # colour
    if w >= 380 and w < 440:
        R = -(w - 440.) / (440. - 350.)
        G = 0.0
        B = 1.0
    elif w >= 440 and w < 490:
        R = 0.0
        G = (w - 440.) / (490. - 440.)
        B = 1.0
    elif w >= 490 and w < 510:
        R = 0.0
        G = 1.0
        B = -(w - 510.) / (510. - 490.)
    elif w >= 510 and w < 580:
        R = (w - 510.) / (580. - 510.)
        G = 1.0
        B = 0.0
    elif w >= 580 and w < 645:
        R = 1.0
        G = -(w - 645.) / (645. - 580.)
        B = 0.0
    elif w >= 645 and w <= 780:
        R = 1.0
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0

    # intensity correction
    if w >= 380 and w < 420:
        SSS = 0.3 + 0.7*(w - 350) / (420 - 350)
    elif w >= 420 and w <= 700:
        SSS = 1.0
    elif w > 700 and w <= 780:
        SSS = 0.3 + 0.7*(780 - w) / (780 - 700)
    else:
        SSS = 0.0
    SSS *= 255

    return [int(SSS*R)/256., int(SSS*G)/256., int(SSS*B)/256., 1]
