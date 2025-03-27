import os
import tomllib

from . import DEFAULTS

class Reader:
    def __init__(self, **kwargs):
        self.assistant_library = os.path.expandvars(kwargs.get("assistant_library", DEFAULTS['ASSISTANT_LIBRARY']))
        self.model_library = os.path.expandvars(kwargs.get("model_library", DEFAULTS['MODEL_LIBRARY']))

    def read(self, **kwargs):
        assistant_library = kwargs.get("assistant_library", self.assistant_library)
        model_libray = kwargs.get("model_library", self.model_library)

        available_bots = {}
        enabled_bots = {}
        daemon_config_filepath = ""
        # Search two levels deep-- daemon top-level, bot bottom-level
        for a in os.listdir(assistant_library):
            x = os.path.join(assistant_library, a)
            if os.path.isfile(x) == True and a == "config.toml":
                daemon_config_filepath = x
            else:
                for b in os.listdir(x):
                    y = os.path.join(x, b)
                    if os.path.isfile(y) == True and b == "config.toml":
                        with open(y, "rb") as f:
                            bot_config = tomllib.load(f)
                            if bot_config['enabled'] == True:
                                available_bots[bot_config['name']] = bot_config
        #print(daemon_config_filepath)
        with open(daemon_config_filepath, "rb") as f:
            daemon_config = tomllib.load(f)
            for bot in daemon_config['bots']['enabled']:
                if bot in available_bots:
                    enabled_bots[bot] = available_bots[bot]

        return {
            'enabled_bots': enabled_bots,
            **daemon_config,
        }
