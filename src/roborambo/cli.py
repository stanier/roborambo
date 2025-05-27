import argparse
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
            if raw_input in ("quit", "exit"):
                break

            result = a.chain.generate(raw_input)
            print(f"{bcolors.BOLD}{kwargs.get('assistant_identifier', 'Assistant')} >{bcolors.ENDC} ", end="")
            
            if a.chain.stream:
                for p in result:
                    print(p['response'], end='', flush=True)
                print('\n')
            else:
                print(result)

def config_bot():
    """Launch the bot configuration TUI."""
    try:
        from .config_tui import BotConfigTUI
        tui = BotConfigTUI()
        tui.run()
    except ImportError as e:
        print(f"Config TUI unavailable: {e}")

def run(**kwargs):
    parser = argparse.ArgumentParser(
        prog='roborambo',
        description='Dead simple LLM-augmented Assistant/Bot system'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    config_parser = subparsers.add_parser('config-bot', help='Launch interactive bot configuration generator')
    
    chat_parser = subparsers.add_parser('chat', help='Start an interactive chat session with a bot')
    chat_parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
    chat_parser.add_argument('--assistant', help='Name of assistant to load', default='Son of Rambo')
    
    serve_parser = subparsers.add_parser('serve', help='Start up daemon with messaging interfaces')
    serve_parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
    
    # Legacy support
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
    parser.add_argument('--serve', action='store_true', help='Start up daemon')
    parser.add_argument('--assistant', help='Name of assistant to load', default='Son of Rambo')

    args = parser.parse_args()
    
    if args.command == 'config-bot':
        config_bot()
        return
    elif args.command == 'chat':
        conf = ConfigReader().read()
        if args.assistant not in conf['enabled_bots']:
            print(f"{bcolors.BOLD}Error:{bcolors.ENDC} Assistant '{args.assistant}' not found.")
            print(f"Available bots: {', '.join(conf['enabled_bots'].keys())}")
            return
        
        print(f"{bcolors.BOLD}Starting chat with {args.assistant}{bcolors.ENDC}")
        Repl(conf, assistant_name=args.assistant, debug=args.debug)
        return
    elif args.command == 'serve':
        conf = ConfigReader().read()
        d = Daemon(conf, debug=args.debug)
        for bot in d.bots:
            for process in d.bots[bot]['processes']:
                d.bots[bot]['processes'][process].start()
                print(f"{bcolors.BOLD}{bot}:{bcolors.ENDC} Started {process}")
        return
    
    # Legacy mode
    if hasattr(args, 'serve') and args.serve:
        conf = ConfigReader().read()
        d = Daemon(conf, debug=args.debug)
        for bot in d.bots:
            for process in d.bots[bot]['processes']:
                d.bots[bot]['processes'][process].start()
    else:
        conf = ConfigReader().read()
        if args.assistant not in conf['enabled_bots']:
            print(f"{bcolors.BOLD}Error:{bcolors.ENDC} Assistant '{args.assistant}' not found.")
            return
        
        print(f"{bcolors.BOLD}Roborambo Interactive Chat{bcolors.ENDC}")
        print("Type 'quit' or 'exit' to end the session.")
        Repl(conf, assistant_name=args.assistant, debug=args.debug)

if __name__ == "__main__": 
    run()