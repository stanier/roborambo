import sys

from mattermostdriver import Driver as MattermostClient
from .messaging import MessagingInterface

class MattermostInterface(MessagingInterface):
    consolecolors = (255, 255, 255)

    def __init__(self, chain, **kwargs):
        super().__init__(chain, **kwargs)

        self.client = MattermostClient({
            'url': '',
            'login_id': '',
            'password': '',
            'token': '',
            'scheme': 'https',
            'port': 8065,
            'basepath': '/api/v4',
            'mfa_token': '',
            'auth': None,
            'timeout': 30,
            'request_timeout': None,
            'keepalive': False,
            'keepalive_delay': 5,
            'websocket_kw_args': None,
            'debug': False,
        })
    
    def start_callback(self, message, **kwargs):
        pass

    def tool_callback(self, message, **kwargs):
        pass

    def finish_callback(self, message, **kwargs):
        pass

    def write_callback(self, message, **kwargs):
        pass

    def cutoff_callback(self, message, **kwargs):
        pass

    def success_callback(self, message, **kwargs):
        pass

    def failure_callback(self, message, **kwargs):
        pass

    def warning_callback(self, message, **kwargs):
        pass

    def info_callback(self, message, **kwargs):
        pass

    def intervention_callback(self, message, **kwargs):
        pass

    def reply_message(self, message, data, **kwargs):
        pass

    def send_message(self, destination, data, **kwargs):
        pass

    def add_reaction(self, message, data, **kwargs):
        pass

    def remove_reaction(self, message, data, **kwargs):
        pass

    def handle_message(self, message, **kwargs):
        pass
