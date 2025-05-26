from datetime import datetime

import roborambo.tools as tools
from nothingburger.memory import ConversationalMemory
from nothingburger.chains import ChatChain
import nothingburger.templates as templates

class RamboChain(ChatChain):
    # TODO:  So yeah, this should be an actual DB of some sort.... but we're going by prototype principles atm so it's fiiiiine
    memory_db = {}
    
    def __init__(self, **kwargs):
        print(f"🔗 Initializing RamboChain...")
        print(f"  Kwargs keys: {list(kwargs.keys())}")
        print(f"  Model: {type(kwargs.get('model', 'None'))}")
        print(f"  Template: {type(kwargs.get('template', 'None'))}")
        print(f"  API format: {kwargs.get('api_format', 'not specified')}")
        
        super().__init__(**kwargs)
        
        self.cutoff_phrase = kwargs['cutoff']['phrase'].replace(" ", "").upper()
        self.cutoff_hint = kwargs['cutoff']['hint']
        self.cutoff_message = kwargs['cutoff']['message']
        self.api_format = kwargs.get('api_format', 'completions')
        
        print(f"  Cutoff phrase: '{self.cutoff_phrase}'")
        print(f"  API format: {self.api_format}")
        print(f"  Model in chain: {type(self.model) if hasattr(self, 'model') else 'No model'}")
        print(f"✅ RamboChain initialization complete!")

    def responsiveness_simple(self, message, assistant_prefix, **kwargs):
        # For responsiveness check, always use a simple completion-style prompt
        assessment = self.generate(
            message,
            instruction = f"Given the message in Input sent by a user, determine whether the assistant \"{assistant_prefix}\" should read it and indicate this with either a Yes or No.  The Assistant should read the message if it is addressed to.  If they mention they don't want their message read by the assistant, it shouldn't read it",
            template    = templates.getTemplate("alpaca_instruct_input"),
            max_tokens  = 100, # Should be 1, but Ollama currently bugs with low num_predict
            memory      = None,
            top_k       = -1,
            top_p       = 1.0,
            **kwargs,
        )
        return assessment[0] == "Y"

    def cutoff(self, msg, **kwargs): 
        return self.cutoff_phrase in msg.upper().replace(" ", "")
    
    def step(self, sender, content, **kwargs):
        convmem = kwargs.get('memory', ConversationalMemory())
        
        # Original simple approach - memory is already in kwargs
        response = self.generate(content, user_prefix=sender, **kwargs)
            
        # Update memory after generation
        convmem.add_message(role=sender, content=content, timestamp=kwargs.get('timestamp', datetime.now()))
        convmem.add_message(role=kwargs['assistant_prefix'], content=response, timestamp=datetime.now())
        
        return response

    def run(self, message, callbacks, **kwargs):
        convkey = ""

        if self.cutoff(message['content']) is True:
            callbacks["cutoff"](message)
            return

        sender = message['sender'] # Message sent by
        recips = message['recips'] # Message addressed to
        source = message['source'] # Messaging client received from
        content = message['content'] # The main content of the message
        channel = message['channel'] # Channel the message was sent to
        server = message['server'] # Server the message was sent to
        visibility = message['visibility'] # The general visibility of the message
        privacy = message['privacy'] # How private the message is
        secure = message['secure'] # Whether the message received over a secure, end-to-end encrypted channel

        if privacy == 'private_direct':
            pass
        elif privacy == 'private_group':
            if not self.responsiveness_simple(content, self.assistant_prefix):
                if kwargs.get("DEBUG"): 
                    import sys
                    sys.stdout.write(f"IGNORED MESSAGE\n")
                return
        else:
            if not self.responsiveness_simple(content, self.assistant_prefix):
                if kwargs.get("DEBUG"): 
                    import sys
                    sys.stdout.write(f"IGNORED MESSAGE\n")
                return

        convhash = hash(convkey)
        if convhash not in self.memory_db: 
            self.memory_db[convhash] = ConversationalMemory()
        convmem = self.memory_db[convhash]

        callbacks["start"](message)

        response = self.step(
            sender['name'],
            content,
            memory=convmem,
            **kwargs,
        )
        
        invocation = tools.parse_invocation(response)
        while invocation:
            callbacks["tool"](message, invocation)
            result = self.active_tools[invocation['tool']].methods[invocation['func']]['method'](**invocation['args'])

            response = self.step(
                f"{invocation['tool']}.{invocation['func']}",
                result,
                memory=convmem,
                **kwargs,
            )

            invocation = tools.parse_invocation(response)

        callbacks["finish"](message)
        return response