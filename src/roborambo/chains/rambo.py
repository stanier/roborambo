from datetime import datetime
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
        self.active_tools = kwargs.get('active_tools', {})

    def responsiveness_simple(self, message, assistant_prefix, **kwargs):
        """Determine if the assistant should respond to a message."""
        assessment = self.generate(
            message,
            instruction=f"Given the message in Input sent by a user, determine whether the assistant \"{assistant_prefix}\" should read it and indicate this with either a Yes or No. The Assistant should read the message if it is addressed to them. If they mention they don't want their message read by the assistant, it shouldn't read it",
            template=templates.getTemplate("chat_simple"),
            max_tokens=100,
            memory=None,
            top_k=-1,
            top_p=1.0,
            **kwargs,
        )
        return assessment.strip().upper().startswith("Y")

    def cutoff(self, msg, **kwargs): 
        """Check if message contains emergency cutoff phrase."""
        return self.cutoff_phrase in msg.upper().replace(" ", "")
    
    def step(self, sender, content, **kwargs):
        """Generate a single response step with function calling."""
        convmem = kwargs.get('memory', ConversationalMemory())
        
        # Always pass active_tools for function calling
        kwargs['active_tools'] = self.active_tools
        
        response = self.generate(content, user_prefix=sender, **kwargs)
        
        # Add messages to memory
        convmem.add_message(role=sender, content=content, timestamp=kwargs.get('timestamp', datetime.now()))
        convmem.add_message(role=kwargs.get('assistant_prefix', self.assistant_prefix), content=response, timestamp=datetime.now())
        
        return response

    def run(self, message, callbacks, **kwargs):
        """Main conversation loop - simplified without text-based tool parsing."""
        if self.cutoff(message['content']):
            callbacks.get("cutoff", lambda x: None)(message)
            return

        sender = message['sender']
        content = message['content']
        privacy = message['privacy']

        # Check if we should respond in group/public contexts
        if privacy in ['private_group', 'semipublic']:
            if not self.responsiveness_simple(content, self.assistant_prefix, **kwargs):
                return

        # Get or create conversation memory
        convhash = hash("")  # Simple hash for now, could be improved with actual conversation context
        if convhash not in self.memory_db: 
            self.memory_db[convhash] = ConversationalMemory()
        convmem = self.memory_db[convhash]

        # Signal start of processing
        callbacks.get("start", lambda x: None)(message)

        # Generate response with function calling
        # All tool execution is handled automatically by the model adapter
        response = self.step(sender['name'], content, memory=convmem, **kwargs)

        # Signal completion
        callbacks.get("finish", lambda x: None)(message)
        
        return response