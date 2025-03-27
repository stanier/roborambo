class Configable:
    def __init__(self, **kwargs):
        if getattr(self, '__config__', False) == False: setattr(self, '__config__', {
            'tool_methods': {}
        })