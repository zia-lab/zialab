import numpy as np
import http.client, urllib
import sys
import os
platform = sys.platform
import re
import ssl
import requests, io, json
import time, os

if platform == 'win32':
    import winsound
else:
    import pygame

pushover = False
slackit = False

try:
    from .dave import secrets
    pushover_user = secrets['pushover_user']
    pushover_token = secrets['pushover_token']
    slack_token = secrets['slack_token']
    slackit = True
    pushover = True
except:
    print("Ask David about secrets.")
    pass

ssl.match_hostname = lambda cert, hostname: True
if platform == 'win32':
    codebase_dir = 'D:/Google Drive/Zia Lab/Codebase/'
    log_dir = 'D:/Google Drive/Zia Lab/Log'
    data_dir = os.path.join(log_dir,'Data')
    graphs_dir = os.path.join(log_dir,'Graphs')
else:
    codebase_dir = '/Users/juan/Google Drive/Zia Lab/Codebase/'
    log_dir = '/Users/juan/Google Drive/Zia Lab/Log'
    data_dir = os.path.join(log_dir,'Data')
    graphs_dir = os.path.join(log_dir,'Graphs')

def wait(wait_duration=0.1):
    time.sleep(wait_duration)

def bell():
    if platform == 'win32':
        winsound.PlaySound(os.path.join(codebase_dir,'sounds','bell.wav'),
                   winsound.SND_ASYNC)
    else:
        pygame.init()
        pygame.mixer.init()
        sounda = pygame.mixer.Sound(os.path.join(codebase_dir,'sounds','bell.wav'))
        sounda.play()

def ding():
    if platform == 'win32':
        winsound.PlaySound(os.path.join(codebase_dir,'sounds','ding.wav'),
                       winsound.SND_ASYNC)
    else:
        pygame.init()
        pygame.mixer.init()
        sounda = pygame.mixer.Sound(os.path.join(codebase_dir,'sounds','ding.wav'))
        sounda.play()

pixel_sizes = {'proem': 16, 'pixis': 20, 'pionir': 20} # in um

resolutions = { # for IsoPlane
    'proem': {
        '150':[[10,20,25,50,100,150,200,300],
               [0.553,0.553,0.553,0.9875,1.975,2.9625,3.95,5.925]],
        '300':[[10,20,25,50,100,150,200,300],
               [0.2734,0.2734,0.2734,0.4883,0.9765,1.4648,1.953,2.9295]],
        '50':[[10,20,25,50,100,150,200,300],
               [1.6691,1.6691,1.6691,2.9805,5.961,8.9415,11.922,17.8831]],
    },
    'pixis': {
        '50':[[10,20,25,50,100,150,200,300],
               [1.74,1.74,1.74,2.98,5.96,8.94,11.92,17.88]],
        '150':[[10,20,25,50,100,150,200,300],
               [0.58,0.58,0.58,0.98,1.98,2.96,3.95,5.93]],
        '300':[[10,20,25,50,100,150,200,300],
               [0.28,0.28,0.28,0.49,0.98,1.46,1.95,2.93]]
    },
    'pionir': {
        '50':[[10,20,25,50,100,150,200,300],
               [1.67,1.67,1.67,2.98,5.96,8.94,11.92,17.88]],
        '150':[[10,20,25,50,100,150,200,300],
               [0.55,0.55,0.55,0.98,1.98,2.96,3.95,5.93]],
        '300':[[10,20,25,50,100,150,200,300],
               [0.27,0.27,0.27,0.49,0.98,1.46,1.95,2.93]]
    },
}

resolutions_SP2300 = {
    'pixis': {
        '150': [[10,20,25,50,100,150,200,300],
                [1.32,1.32,1.32,1.32,2.11,3.17,4.23,6.34]],
        '300': [[10,20,25,50,100,150,200,300],
                [0.648,0.648,0.648,0.648,1.04,1.56,2.08,3.12]],
    },
    'proem': {
        '150': [[10,20,25,50,100,150,200,300],
                [1.27,1.27,1.27,1.27,2.11,3.17,4.23,6.34]],
        '300': [[10,20,25,50,100,150,200,300],
                [0.623,0.623,0.623,0.623,1.039,1.56,2.08,3.12]],
    },
    'pionir': {
        '150': [[10,20,25,50,100,150,200,300],
                [1.27,1.27,1.27,1.27,2.11,3.17,4.23,6.34]],
        '300': [[10,20,25,50,100,150,200,300],
                [0.623,0.623,0.623,0.623,1.039,1.56,2.08,3.12]],
    },
}

def slit_to_resolution(grating, slit_width, camera):
    grating_string = re.sub("[^0-9]", "", str(grating))
    if grating_string not in ['50','150','300']:
        print("Unavailable grating")
        return None
    camera = camera.lower()
    if 'pixis' in camera:
        camera = 'pixis'
    elif 'proem' in camera:
        camera = 'proem'
    elif 'pionir' in camera:
        camera = 'pionir'
    else:
        print("invalid camera choice")
        return None
    return np.interp(slit_width,resolutions[camera][grating_string][0],resolutions[camera][grating_string][1])

if pushover:
    def send_message(message):
        conn = http.client.HTTPSConnection("api.pushover.net",443)
        conn.request("POST", "/1/messages.json",
          urllib.parse.urlencode({
            "token": pushover_token,
            "user": pushover_user,
            "message": message,
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        return None

    def send_count(count):
        conn = http.client.HTTPSConnection("api.pushover.net",443)
        conn.request("POST", "/1/glances.json",
          urllib.parse.urlencode({
            "token": pushover_token,
            "user": pushover_user,
            "count": count,
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        return None

    def send_image(image_fname,message=''):
        if '.jpg' in image_fname.lower():
            mime = 'image/jpeg'
        elif '.png' in image_fname.lower():
            mime = 'image/png'
        elif '.jpeg' in image_fname.lower():
            mime = 'image/jpeg'
        else:
            return "send jpg of jpeg only"
        r = requests.post("https://api.pushover.net/1/messages.json", data = {
          "token": pushover_token,
          "user": pushover_user,
          "message": message
        },
        files = {
          "attachment": ("image.jpg",
                         open(image_fname, "rb"), "image/jpeg")
        })
        return None

if slackit:
    default_slack_channel = '#datahose'
    slack_icon_emoji = ':see_no_evil:'
    slack_user_name = 'labbot'
    def post_message_to_slack(text, blocks = None, slack_channel = default_slack_channel):
        return requests.post('https://slack.com/api/chat.postMessage', {
            'token': slack_token,
            'channel': slack_channel,
            'text': text,
            'icon_emoji': slack_icon_emoji,
            'username': slack_user_name,
            'blocks': json.dumps(blocks) if blocks else None
        }).json()
    def post_file_to_slack(text, file_name, file_bytes, file_type=None, title=None, slack_channel=default_slack_channel):
        return requests.post(
        'https://slack.com/api/files.upload',
        {
            'token': slack_token,
            'filename': file_name,
            'channels': slack_channel,
            'filetype': file_type,
            'initial_comment': text,
            'title': title
        },
        files = { 'file': file_bytes }).json()

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
