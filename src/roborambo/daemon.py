import argparse
from multiprocessing import Process
from nothingburger.cli import bcolors
from .interfaces import available_clients
from .config import Reader as ConfigReader
from .assistant import Assistant

class Daemon:
    def __init__(self, conf, **kwargs):
        self.bots = {}
        for bot in conf['enabled_bots']:
            self.bots[bot] = {
                'assistant': Assistant(conf['enabled_bots'][bot]),
            }

            self.tunables = {
                'temperature': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('temperature', 0.0),
                'frequency_penalty': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('frequency_penalty', 1.07),
                'presence_penalty': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('presence_penalty', 0.0),
                'top_k': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('top_k', -1),
                'top_p': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('top_p', 1.0),
                'seed': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('seed', 42),
                'mirostat': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('mirostat', {}).get('mode', 0),
                'mirostat_eta': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('mirostat', {}).get('eta', 0.1),
                'mirostat_tau': conf['enabled_bots'][bot].get('tunables', {}).get('generation', {}).get('mirostat', {}).get('tau', 5.0),
            }

            clients = {}
            self.bots[bot]['processes'] = {}
            for client in conf['enabled_bots'][bot]['interfaces']['enabled']:
                clients[client] = available_clients[client](
                    chain=self.bots[bot]['assistant'].chain, 
                    **conf['enabled_bots'][bot]['interfaces'][client], 
                    tunables=self.tunables
                )
                clients[client].pname = f"{bcolors.BOLD}\x1b[38;2;{clients[client].consolecolor[0]};{clients[client].consolecolor[1]};{clients[client].consolecolor[2]}m{clients[client].consolename}{bcolors.ENDC}"
                
                self.bots[bot]['processes'][clients[client].pname] = Process(
                    target=clients[client].serve, 
                    args=[], 
                    kwargs={}
                )

def serve(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
    args = parser.parse_args()

    conf = ConfigReader().read()
    d = Daemon(conf, **kwargs)

    for bot in d.bots:
        for process in d.bots[bot]['processes']:
            d.bots[bot]['processes'][process].start()
            print(f"{bcolors.BOLD}{bot}:{bcolors.ENDC} Started {process}")

    # Join the last process to keep daemon running
    if d.bots:
        last_bot = list(d.bots.keys())[-1]
        last_process = list(d.bots[last_bot]['processes'].keys())[-1]
        d.bots[last_bot]['processes'][last_process].join()

if __name__ == "__main__": 
    serve()