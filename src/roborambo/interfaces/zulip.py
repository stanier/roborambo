import sys
import re

from zulip import Client as ZulipClient
from .messaging import MessagingInterface

class ZulipInterface(MessagingInterface):
    consolecolor = (40, 177, 249)
    consolename = "Zulip"
    sourcename = "zulip"

    def __init__(self, chain, **kwargs):
        super().__init__(chain, **kwargs)
        self.emoji["look"]      = "eyes"
        self.emoji["read"]      = "book"
        self.emoji["write"]     = "pencil"
        self.emoji["work"]      = "working on it"
        self.emoji["ask"]       = "umm"
        self.emoji["point"]     = "point up"
        self.emoji["plan"]      = "thought"
        self.emoji["yes"]       = "+1"
        self.emoji["no"]        = "-1"
        self.emoji["maybe"]     = "palm hand down"
        self.emoji["octo"]      = "octopus"
        self.emoji["success"]   = "check"
        self.emoji["failure"]   = "cross mark"
        self.emoji["tool"]      = "toolbox"
        self.emoji["web"]       = "globe"
        self.emoji["search"]    = "search"
        self.emoji["noaccess"]  = "prohibited"

        self.client = ZulipClient(
            api_key = kwargs['key'],
            email = kwargs['email'],
            site = kwargs['site'],
        )

        self.privileged_users = kwargs.get("privileged_users", [])

        self.chain = chain
        self.profile = self.client.get_profile()

        self.tunables = kwargs['tunables']
    
    def serve(self, **kwargs):
        _ = super().serve(**kwargs);
        if (_ is not None): return _
        self.client.call_on_each_message(self.handle_message)

    def start_callback(self, message, **kwargs):
        _ = super().start_callback(message, **kwargs);
        if (_ is not None): return _
        self.add_reaction(message['id'], 'look')

    def tool_callback(self, message, invocation, **kwargs):
        _ = super().tool_callback(message, **kwargs);
        if (_ is not None): return _
        if active_tools[invocation['tool']].emoji:
            self.add_reaction(message['id'], active_tools[invocation['tool']].emoji)
        if active_tools[invocation['tool']].methods[invocation['func']].get('emoji', False):
            self.add_reaction(message['id'], active_tools[invocation['tool']].methods[invocation['func']]['emoji'])

    def finish_callback(self, message, **kwargs):
        _ = super().finish_callback(message, **kwargs);
        if (_ is not None): return _
        self.remove_reaction(message['id'], 'look')
        self.remove_reaction(message['id'], 'write')

    def write_callback(self, message, **kwargs):
        _ = super().write_callback(message, **kwargs);
        if (_ is not None): return _
        self.add_reaction(message['id'], 'write')

    def cutoff_callback(self, message, **kwargs):
        _ = super().cutoff_callback(message, **kwargs);
        if (_ is not None): return _
        if message['type'] == 'private':
            recips = []
            for r in message['display_recipient']: recips.append(r['id'])
            msg_type = "private"
            msg_to = recips
        else:
            msg_type = "stream",
            msg_to = message['stream_id']
        
        self.client.send_message({"type": msg_type, "to": msg_to, "content": CUTOFF_MESSAGE})
        sys.exit()

    def success_callback(self, message, **kwargs):
        if super().success_callback(message, **kwargs): return

    def failure_callback(self, message, **kwargs):
        _ = super().failure_callback(message, **kwargs);
        if (_ is not None): return _

    def warning_callback(self, message, **kwargs):
        _ = super().warning_callback(message, **kwargs);
        if (_ is not None): return _

    def info_callback(self, message, **kwargs):
        _ = super().info_callback(message, **kwargs);
        if (_ is not None): return _

    def intervention_callback(self, message, **kwargs):
        _ = super().intervention_callback(message, **kwargs);
        if (_ is not None): return _

    def reply_message(self, message, data, **kwargs):
        _ = super().reply_message(message, **kwargs);
        if (_ is not None): return _

    def send_message(self, destination, data, **kwargs):
        _ = super().send_message(message, **kwargs);
        if (_ is not None): return _

    def add_reaction(self, mid, emoji, **kwargs):
        _ = super().add_reaction(mid, emoji, **kwargs);
        if (_ is not None): return _
        self.client.add_reaction({"message_id": mid, "emoji_name": self.emoji[emoji]})
    def remove_reaction(self, mid, emoji, **kwargs):
        _ = super().remove_reaction(mid, emoji, **kwargs);
        if (_ is not None): return _
        self.client.remove_reaction({"message_id": mid, "emoji_name": self.emoji[emoji]})

    def get_room_info(self, message, **kwargs):
        _ = super().get_room_info(message, **kwargs);
        if (_ is not None): return _
        
        info = {
            'ri': [],
            'rs': [],
            'recips': [],
        }
        for recip in message['display_recipient']:
            info['ri'].append(int(recip['id']))
            info['rs'].append(str(recip['id']))
            info['recips'].append({
                'id': recip['id'],
                'full_name': recip['full_name'],
                'email': recip['email'],
            })
        info['ri'].sort()

        if message['type'] == 'private':
            info['visibility'] = 'private'
            if len(info['recips']) > 2:
                info['privacy'] = 'private_group'
            else:
                info['privacy'] = 'private_direct'

            info['channel'] = ','.join(info['rs'])
            info['to'] = info['ri'] # Don't think we can use channel because Zulip API expects array?  I think?  I should double check
        else:
            info['visibility'] = 'semipublic'
            info['privacy'] = 'semipublic'
            info['channel'] = message['stream_id']
            info['to'] = info['channel']

        return info

    def handle_message(self, message, **kwargs):
        if message['sender_id'] == self.profile['user_id']: return # Don't talk to yourself

        kwargs.update(self.get_room_info(message, **kwargs))

        _ = super().handle_message(message, **kwargs);
        if (_ is not None): return _

        msg = {
            'id': message['id'],
            'sender': {
                'name': message['sender_full_name'],
                'email': message['sender_email'],
                'id': message['sender_id'],
            },
            'recips': kwargs['recips'],
            'source': self.sourcename,
            'content': message['content'],
            'channel': kwargs['channel'],
            'server': 'default',
            'visibility': kwargs['visibility'],
            'privacy': kwargs['privacy'],
            'secure': False,
        }

        response = self.chain.run(
            msg,
            callbacks = {
                'start'         : self.start_callback,
                'finish'        : self.finish_callback,
                'write'         : self.write_callback,
                'cutoff'        : self.cutoff_callback,
                'success'       : self.success_callback,
                'failure'       : self.failure_callback,
                'warning'       : self.warning_callback,
                'info'          : self.info_callback,
                'intervention'  : self.intervention_callback,
                'tool'          : self.tool_callback,
            },
            assistant_prefix = self.profile['full_name'],
            stop = ["\n[", "</s>"],
            **self.tunables,
        )
        
        self.client.send_message({"type": message['type'], "to": kwargs['to'], "content": response})
