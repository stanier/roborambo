from datetime import datetime

import os
import sys
import json
import requests
import re
import time
import tomllib
import argparse

from multiprocessing import Process

from nothingburger.chains import ChatChain
from nothingburger.memory import ConversationalMemory
from nothingburger.cli import bcolors
#from nothingburger.model_loader import initializeModel

#import nothingburger.templates as templates

#import roborambo.tools as tools

#from .chains import RamboChain
from .interfaces import available_clients
from .options import options
from .config import Reader as ConfigReader
from .assistant import Assistant
#from . import DEFAULTS

from pandoc.types import *

class Daemon:
    def __init__(self, conf, **kwargs):
        self.bots = {}
        for bot in conf['enabled_bots']:
            self.bots[bot] = {
                'assistant': Assistant(conf['enabled_bots'][bot]),
            }

            self.tunables = {
                'temperature'         : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('temperature', 0.0),
                'frequency_penalty'   : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('frequency_penalty', 1.07),
                'presence_penalty'    : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('presense_penalty', 0.0),
                'top_k'               : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('top_k', -1),
                'top_p'               : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('top_p', 1.0),
                'seed'                : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('seed', 42),
                'mirostat'            : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('mirostat', {}).get('mode', 0),
                'mirostat_eta'        : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('mirostat', {}).get('eta', 0.1),
                'mirostat_tau'        : conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('mirostat', {}).get('tau', 5.0),
            }

            clients = {}
            self.bots[bot]['processes'] = {}
            for client in conf['enabled_bots'][bot]['interfaces']['enabled']:
                clients[client] = available_clients[client](chain=self.bots[bot]['assistant'].chain, **conf['enabled_bots'][bot]['interfaces'][client], tunables = self.tunables)
                clients[client].pname = f"{bcolors.BOLD}\x1b[38;2;{clients[client].consolecolor[0]};{clients[client].consolecolor[1]};{clients[client].consolecolor[2]}m{clients[client].consolename}{bcolors.ENDC}"
                
                self.bots[bot]['processes'][clients[client].pname] = Process(target = clients[client].serve, args = [], kwargs = {})

def serve(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action = 'store_true', help = 'Enable debugging mode', default = False)
    #parser.add_argument('--nomem', action = 'store_true', help = 'Turn off persistent memory', default = options['PERSIST_MEMORY'])
    #parser.add_argument('--supervised', action = 'store_true', help = 'Disable all self-guided capabilites', default = options['SUPERVISED'])

    args = parser.parse_args()

    conf = ConfigReader().read()

    d = Daemon(conf, **kwargs)

    for bot in d.bots:
        for process in d.bots[bot]['processes']:
            d.bots[bot]['processes'][process].start()
            print(f"{bcolors.BOLD}{bot}:{bcolors.ENDC} Messaging client {process} has been started")

    # Just join the last one, I'm lazy atm
    d.bots[bot]['processes'][process].join()

if __name__ == "__main__": serve()