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
        self.emoji = {
            "look": "eyes", "write": "pencil", "success": "check", 
            "failure": "cross mark", "noaccess": "prohibited"
        }

        self.client = ZulipClient(
            api_key=kwargs['key'],
            email=kwargs['email'],
            site=kwargs['site'],
        )

        self.privileged_users = kwargs.get("privileged_users", [])
        self.chain = chain
        self.profile = self.client.get_profile()
        self.tunables = kwargs['tunables']
    
    def convert_think_blocks_to_spoilers(self, text):
        """Convert <think></think> blocks to Zulip spoilers."""
        def replace_think_block(match):
            content = match.group(1).strip()
            return f"```spoiler Thinking\n{content}\n```"
        
        # Use re.DOTALL to match across newlines, re.IGNORECASE for case insensitivity
        pattern = r'<think>(.*?)</think>'
        return re.sub(pattern, replace_think_block, text, flags=re.DOTALL | re.IGNORECASE)
    
    def serve(self, **kwargs):
        self.client.call_on_each_message(self.handle_message)

    def start_callback(self, message, **kwargs):
        self.add_reaction(message['id'], 'look')

    def finish_callback(self, message, **kwargs):
        self.remove_reaction(message['id'], 'look')
        self.remove_reaction(message['id'], 'write')

    def write_callback(self, message, **kwargs):
        self.add_reaction(message['id'], 'write')

    def cutoff_callback(self, message, **kwargs):
        if message['type'] == 'private':
            recips = [r['id'] for r in message['display_recipient']]
            msg_type = "private"
            msg_to = recips
        else:
            msg_type = "stream"
            msg_to = message['stream_id']
        
        self.client.send_message({"type": msg_type, "to": msg_to, "content": "Emergency cutoff activated."})
        sys.exit()

    def add_reaction(self, mid, emoji, **kwargs):
        self.client.add_reaction({"message_id": mid, "emoji_name": self.emoji[emoji]})
    
    def remove_reaction(self, mid, emoji, **kwargs):
        self.client.remove_reaction({"message_id": mid, "emoji_name": self.emoji[emoji]})

    def get_room_info(self, message, **kwargs):
        info = {'ri': [], 'rs': [], 'recips': []}
        
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
            info['privacy'] = 'private_group' if len(info['recips']) > 2 else 'private_direct'
            info['channel'] = ','.join(info['rs'])
            info['to'] = info['ri']
        else:
            info['visibility'] = 'semipublic'
            info['privacy'] = 'semipublic'
            info['channel'] = message['stream_id']
            info['to'] = info['channel']

        return info

    def handle_message(self, message, **kwargs):
        if message['sender_id'] == self.profile['user_id']:
            return

        kwargs.update(self.get_room_info(message, **kwargs))

        # Handle special commands
        if super().handle_message(message, **kwargs):
            return

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
            callbacks={
                'start': self.start_callback,
                'finish': self.finish_callback,
                'write': self.write_callback,
                'cutoff': self.cutoff_callback,
                'tool': lambda m, i: None,
                'success': lambda m: None,
                'failure': lambda m: None,
                'warning': lambda m: None,
                'info': lambda m: None,
                'intervention': lambda m: None,
            },
            assistant_prefix=self.profile['full_name'],
            stop=["\n[", "</s>"],
            **self.tunables,
        )
        
        # Convert think blocks to spoilers for Zulip
        response = self.convert_think_blocks_to_spoilers(response)
        
        self.client.send_message({"type": message['type'], "to": kwargs['to'], "content": response})