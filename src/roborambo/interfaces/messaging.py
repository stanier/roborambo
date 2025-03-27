class MessagingInterface:
    emoji = {}

    def __init__(self, chain, **kwargs):
        self.tunables = kwargs.get('tunables', {})
    
    def start_callback(self, message, **kwargs):
        pass

    def tool_callback(self, message, **kwargs):
        pass

    def finish_callback(self, message, **kwargs):
        pass

    def write_callback(self, message, **kwargs):
        pass

    def cutoff_callback(self, message, **kwargs):
        pass

    def success_callback(self, message, **kwargs):
        pass

    def failure_callback(self, message, **kwargs):
        pass

    def warning_callback(self, message, **kwargs):
        pass

    def info_callback(self, message, **kwargs):
        pass

    def intervention_callback(self, message, **kwargs):
        pass

    def reply_message(self, message, data, **kwargs):
        pass

    def send_message(self, destination, data, **kwargs):
        pass

    def add_reaction(self, mid, emoji, **kwargs):
        pass

    def remove_reaction(self, mid, emoji, **kwargs):
        pass

    def get_room_info(self, message, **kwargs):
        pass

    def handle_message(self, message, **kwargs):
        if message['content'][:8] == "TUNABLES":
            if message['sender_email'] not in self.privileged_users:
                self.client.add_reaction({"message_id": message['id'], "emoji_name": options['EMOJI_NOACCESS']})
                return False
            
            self.client.send_message({"type": message['type'], "to": kwargs['to'], "content": f"The following tunables are set on client \"{self.consolename}\":\n```\n{self.tunables}\n```"})
            return True

        if message['content'][:4] == "TUNE":
            if message['sender_email'] not in self.privileged_users:
                self.add_reaction(message['id'], 'noaccess')
                return False
            
            tune_args = {}
            for arg in re.findall(r"(?i)(\w+)\s?\=\s?(?:((?:true)|(?:false))|('[^'\|\n)]+')|(\"[^\"\|\n)]+\")|(\[.*\])|(\{.*\})|(\d+.\d+)|(\w+))?", message['content'][5:]):
                if arg[1]: # Boolean
                    value = (arg[1].lower() == 'true')
                if arg[2] or arg[3]: # String
                    value = (arg[2] + arg[3])[1:-1]
                if arg[4]: # Array/list
                    value = arg[4][1:-1]
                if arg[5]: # Object
                    value = arg[5][1:-1]
                if arg[6]: # Float
                    value = float(arg[6])
                if arg[7] and arg[7].isnumeric(): # Int
                    value = int(arg[7])

                tune_args[arg[0]] = value
            
            self.tunables.update(tune_args)
            self.add_reaction(message['id'], 'success')
            return True

    def serve(self, **kwargs):
        pass
