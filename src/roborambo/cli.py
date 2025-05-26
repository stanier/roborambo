import os

from nothingburger.cli import bcolors

from .daemon import Daemon
from .config import Reader as ConfigReader
from .assistant import Assistant

class Repl:
    def __init__(self, conf, **kwargs):
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

def config_bot():
    """Launch the bot configuration TUI."""
    try:
        from .config_tui import BotConfigTUI
        tui = BotConfigTUI()
        tui.run()
    except ImportError as e:
        print(f"Error importing config TUI: {e}")
        print("Make sure tomli-w is installed: pip install tomli-w")
        import sys
        sys.exit(1)

def run(**kwargs):
    import argparse
    from multiprocessing import Process

    parser = argparse.ArgumentParser(
        prog='roborambo',
        description='Dead simple LLM-augmented Assistant/Bot system'
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Bot configuration TUI
    config_parser = subparsers.add_parser(
        'config-bot',
        help='Launch interactive bot configuration generator'
    )
    
    # Chat command (existing REPL)
    chat_parser = subparsers.add_parser(
        'chat',
        help='Start an interactive chat session with a bot'
    )
    chat_parser.add_argument('--debug', action='store_true', help='Enable debugging mode', default=False)
    chat_parser.add_argument('--assistant', help='Name of assistant to load', default='Son of Rambo', dest='assistant')
    
    # Serve command (existing daemon)
    serve_parser = subparsers.add_parser(
        'serve',
        help='Start up daemon with messaging interfaces'
    )
    serve_parser.add_argument('--debug', action='store_true', help='Enable debugging mode', default=False)
    
    # Legacy support - if no subcommand, assume chat
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode', default=False, dest='debug')
    parser.add_argument('--serve', action='store_true', help='Start up daemon', default=False, dest='serve')
    parser.add_argument('--assistant', help='Name of assistant to load', default='Son of Rambo', dest='assistant')

    args = parser.parse_args()
    
    # Handle subcommands
    if args.command == 'config-bot':
        config_bot()
        return
    elif args.command == 'chat':
        # Start chat REPL
        conf = ConfigReader().read()
        if args.assistant not in conf['enabled_bots']:
            print(f"{bcolors.BOLD}Error:{bcolors.ENDC} Assistant '{args.assistant}' not found in enabled bots.")
            print(f"Available bots: {', '.join(conf['enabled_bots'].keys())}")
            return
        
        print(f"{bcolors.BOLD}Starting chat with {args.assistant}{bcolors.ENDC}")
        Repl(conf, assistant_name=args.assistant, debug=args.debug)
        return
    elif args.command == 'serve':
        # Start daemon
        conf = ConfigReader().read()
        d = Daemon(conf, debug=args.debug)

        for bot in d.bots:
            for process in d.bots[bot]['processes']:
                d.bots[bot]['processes'][process].start()
                print(f"{bcolors.BOLD}{bot}:{bcolors.ENDC} Messaging client {process} has been started")
        
        # Join the last process to keep the daemon running
        if d.bots:
            last_bot = list(d.bots.keys())[-1]
            last_process = list(d.bots[last_bot]['processes'].keys())[-1]
            d.bots[last_bot]['processes'][last_process].join()
        return
    
    # Legacy mode - handle old-style arguments
    if hasattr(args, 'serve') and args.serve:
        # Legacy serve mode
        conf = ConfigReader().read()
        d = Daemon(conf, debug=args.debug)

        for bot in d.bots:
            for process in d.bots[bot]['processes']:
                d.bots[bot]['processes'][process].start()
                print(f"{bcolors.BOLD}{bot}:{bcolors.ENDC} Messaging client {process} has been started")
    else:
        # Legacy chat mode
        conf = ConfigReader().read()
        
        if args.assistant not in conf['enabled_bots']:
            print(f"{bcolors.BOLD}Error:{bcolors.ENDC} Assistant '{args.assistant}' not found in enabled bots.")
            print(f"Available bots: {', '.join(conf['enabled_bots'].keys())}")
            return
        
        print(f"{bcolors.BOLD}Roborambo Interactive Chat{bcolors.ENDC}")
        print(f"Chatting with: {args.assistant}")
        print("Type 'quit' or 'exit' to end the session.")
        print("Use 'roborambo config-bot' to create new bot configurations.")
        print("-" * 50)
        
        Repl(conf, assistant_name=args.assistant, debug=args.debug)

if __name__ == "__main__": 
    run()