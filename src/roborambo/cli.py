import os

from nothingburger.cli import bcolors
#from nothingburger.model_loader import initializeModel

from .daemon import Daemon
from .config import Reader as ConfigReader
#from .chains import RamboChain
from .assistant import Assistant
#from . import DEFAULTS

#import nothingburger.templates as templates

#import roborambo.tools as tools

class Repl:
    def __init__(self, conf, **kwargs):
        active_tools = {}

        bot = kwargs.get('assistant_name', 'Son of Rambo')

        a = Assistant(conf['enabled_bots'][bot])

        while True:
            raw_input = input(f"{bcolors.BOLD}{kwargs.get('user_identifier', 'User')} >{bcolors.ENDC} ")
            if (raw_input == "quit" or raw_input == "exit"): break

            result = a.chain.generate(raw_input)

            print(f"{bcolors.BOLD}{kwargs.get('assistant_identifier', 'Assistant')} >{bcolors.ENDC} ", end = "")
            if a.chain.stream:
                for p in result: print(p['response'], end='', flush=True)
                print('\n')
            else: print(result)

def run(**kwargs):
    import argparse
    from multiprocessing import Process

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action = 'store_true', help = 'Enable debugging mode', default = False, dest='debug')
    parser.add_argument('--serve', action = 'store_true', help = 'Start up daemon', default = False, dest='serve')
    parser.add_argument('--assistant', help = 'Name of assistant to load', default = 'RoboRambo', dest='assistant')
    #parser.add_argument('--nomem', action = 'store_true', help = 'Turn off persistent memory', default = options['PERSIST_MEMORY'])
    #parser.add_argument('--supervised', action = 'store_true', help = 'Disable all self-guided capabilites', default = options['SUPERVISED'])

    args = parser.parse_args()

    bot = kwargs.get('assistant_name', 'Son of Rambo')

    conf = ConfigReader().read()

    if args.serve == True:
        d = Daemon(conf, **kwargs)

        for bot in d.bots:
            for process in d.bots[bot]['processes']:
                d.bots[bot]['processes'][process].start()
                print(f"{bcolors.BOLD}{bot}:{bcolors.ENDC} Messaging client {process} has been started")

    Repl(conf, **kwargs)

if __name__ == "__main__": run()