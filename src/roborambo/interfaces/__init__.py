import sys
import re

from .messaging import MessagingInterface
from .zulip import ZulipInterface
#from .discord import DiscordInterface
#from .googlechat import GoogleChatInterface
#from .matrix import MatrixInterface
#from .mattermost import MattermostInterface
#from .rocketchat import RocketchatInterface
#from .teams import TeamsIntefface
#import .web import Interface
#import .cli import Interface

available_clients = {
    'zulip': ZulipInterface,
    #'teams': TeamsInferface,
    #'mattermost': MattermostInterface,
    #'matrix': MatrixInterface,
    #'discord': DiscordInterface,
    #'rocketchat': RocketchatInterface,
    #'gsuite': GoogleChatInferface,
    #'web': WebInterface,
    #'cli': CliInterface,
}
