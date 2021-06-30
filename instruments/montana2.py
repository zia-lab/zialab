
import requests

class Montana():
    def __init__(self, tcp_port = 7778):
        self.url = 'http://127.0.0.1:%d/getmontana' % tcp_port
    def get_full_state(self):
        try:
            req = requests.get(self.url).text
            state = tuple(map(float,req.split(',')))
        except:
            state = ''
        return state
