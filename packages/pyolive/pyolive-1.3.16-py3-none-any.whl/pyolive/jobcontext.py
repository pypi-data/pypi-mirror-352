import base64
from dataclasses import dataclass

@dataclass
class JobContext:
    regkey:str
    topic:str
    action_id:int
    action_ns:str
    action_app:str
    action_params:str
    job_id:str
    job_seq:int
    timestamp:int
    filenames:list
    msgbox:dict

    def __init__(self, message=None, devel=False):
        if not devel:
            self.first = True
            self.regkey = message['regkey']
            self.topic = message['topic']
            self.action_id = int(message['action-id'])
            self.action_ns = message['action-ns']
            self.action_app = message['action-app']
            self.action_params = message['action-params']
            self.job_id = message['job-id']
            self.job_seq = int(message['job-seq'])
            self.timestamp = int(message['timestamp'])
            self.filenames = message['filenames'][:]
            self.msgbox = message['msgbox']
        else:
            self.first = True
            self.regkey = ''
            self.topic = ''
            self.action_id = 0
            self.action_ns = ''
            self.action_app = 'ovw_test'
            self.action_params = ''
            self.job_id = ''
            self.job_seq = 0
            self.timestamp = 0
            self.filenames = ''
            self.msgbox = ''

    def get_param(self, key):
        params = dict(map(str.strip, sub.split('=', 1)) for sub in self.action_params.split('&') if '=' in sub)
        try:
            value = params[key]
        except KeyError:
            value = ''
        return value

    def get_fileset(self):
        return self.filenames

    def get_msgbox(self):
        if self.msgbox['type'] == 'binary':
            bstr = base64.b64decode(self.msgbox['data'])
            return bstr.decode('UTF-8')
        else:
            return self.msgbox['data']

    def set_fileset(self, filename):
        if self.first:
            self.filenames = []
            self.filenames.append(filename)
            self.first = False
        else:
            self.filenames.append(filename)

    def set_msgbox(self, data):
        self.msgbox['type'] = 'ascii'
        self.msgbox['size'] = len(data)
        self.msgbox['data'] = data
