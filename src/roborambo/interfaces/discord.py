import sys

from discord import Client as DiscordClient
from .messaging import MessagingInterface

class DiscordInterface(MessagingInterface):
    consolecolor = (114, 137, 218)

    def __init__(self, chain, **kwargs):
        super().__init__(chain, **kwargs)
    
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
