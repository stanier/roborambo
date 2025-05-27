from .messaging import MessagingInterface
from .zulip import ZulipInterface

available_clients = {
    'zulip': ZulipInterface,
}