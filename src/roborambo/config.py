import os
import tomllib

from . import DEFAULTS

class Reader:
    def __init__(self, **kwargs):
        self.bot_library = os.path.expandvars(kwargs.get("bot_library", DEFAULTS['BOT_LIBRARY']))
        self.model_library = os.path.expandvars(kwargs.get("model_library", DEFAULTS['MODEL_LIBRARY']))

    def read(self, **kwargs):
        bot_library = kwargs.get("bot_library", self.bot_library)
        model_library = kwargs.get("model_library", self.model_library)

        available_bots = {}
        enabled_bots = {}
        daemon_config_filepath = ""
        
        # Ensure bot library directory exists
        if not os.path.exists(bot_library):
            os.makedirs(bot_library, exist_ok=True)
            
        # Search two levels deep-- daemon top-level, bot bottom-level
        for a in os.listdir(bot_library):
            x = os.path.join(bot_library, a)
            if os.path.isfile(x) == True and a == "config.toml":
                daemon_config_filepath = x
            elif os.path.isdir(x):
                for b in os.listdir(x):
                    y = os.path.join(x, b)
                    if os.path.isfile(y) == True and b == "config.toml":
                        with open(y, "rb") as f:
                            bot_config = tomllib.load(f)
                            if bot_config.get('enabled', False) == True:
                                available_bots[bot_config['name']] = bot_config
        
        # Create default daemon config if it doesn't exist
        if not daemon_config_filepath:
            daemon_config_filepath = os.path.join(bot_library, "config.toml")
            default_daemon_config = {
                'bots': {'enabled': []},
                'daemon': {'foo': 'bar'},
                'cli': {'foo': 'bar'}
            }
            
            # Create the file with default content
            try:
                import tomli_w
                with open(daemon_config_filepath, 'wb') as f:
                    tomli_w.dump(default_daemon_config, f)
            except ImportError:
                # Fallback to manual creation
                with open(daemon_config_filepath, 'w') as f:
                    f.write("[bots]\nenabled = []\n\n[daemon]\nfoo = \"bar\"\n\n[cli]\nfoo = \"bar\"\n")
        
        # Read daemon config
        with open(daemon_config_filepath, "rb") as f:
            daemon_config = tomllib.load(f)
            for bot in daemon_config.get('bots', {}).get('enabled', []):
                if bot in available_bots:
                    enabled_bots[bot] = available_bots[bot]

        return {
            'enabled_bots': enabled_bots,
            **daemon_config,
        }