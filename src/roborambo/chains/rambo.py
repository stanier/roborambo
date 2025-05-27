from datetime import datetime

import roborambo.tools as tools
from nothingburger.memory import ConversationalMemory
from nothingburger.chains import ChatChain
import nothingburger.templates as templates

class RamboChain(ChatChain):
    memory_db = {}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cutoff_phrase = kwargs['cutoff']['phrase'].replace(" ", "").upper()
        self.cutoff_hint = kwargs['cutoff']['hint']
        self.cutoff_message = kwargs['cutoff']['message']
        self.api_format = kwargs.get('api_format', 'completions')

    def responsiveness_simple(self, message, assistant_prefix, **kwargs):
        assessment = self.generate(
            message,
            instruction=f"Given the message in Input sent by a user, determine whether the assistant \"{assistant_prefix}\" should read it and indicate this with either a Yes or No. The Assistant should read the message if it is addressed to. If they mention they don't want their message read by the assistant, it shouldn't read it",
            template=templates.getTemplate("alpaca_instruct_input"),
            max_tokens=100,
            memory=None,
            top_k=-1,
            top_p=1.0,
            **kwargs,
        )
        return assessment[0] == "Y"

    def cutoff(self, msg, **kwargs): 
        return self.cutoff_phrase in msg.upper().replace(" ", "")
    
    def step(self, sender, content, **kwargs):
        convmem = kwargs.get('memory', ConversationalMemory())
        response = self.generate(content, user_prefix=sender, **kwargs)
        convmem.add_message(role=sender, content=content, timestamp=kwargs.get('timestamp', datetime.now()))
        convmem.add_message(role=kwargs['assistant_prefix'], content=response, timestamp=datetime.now())
        return response

    def run(self, message, callbacks, **kwargs):
        if self.cutoff(message['content']):
            callbacks["cutoff"](message)
            return

        sender = message['sender']
        content = message['content']
        privacy = message['privacy']

        if privacy in ['private_group', 'semipublic']:
            if not self.responsiveness_simple(content, self.assistant_prefix):
                return

        convhash = hash("")
        if convhash not in self.memory_db: 
            self.memory_db[convhash] = ConversationalMemory()
        convmem = self.memory_db[convhash]

        callbacks["start"](message)

        response = self.step(sender['name'], content, memory=convmem, **kwargs)
        
        invocation = tools.parse_invocation(response)
        while invocation:
            callbacks["tool"](message, invocation)
            result = self.active_tools[invocation['tool']].methods[invocation['func']]['method'](**invocation['args'])
            response = self.step(f"{invocation['tool']}.{invocation['func']}", result, memory=convmem, **kwargs)
            invocation = tools.parse_invocation(response)

        callbacks["finish"](message)
        return response