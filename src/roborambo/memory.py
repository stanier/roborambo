class MemoryBackend:
    def __init__(self, **kwargs):
        pass

class SqlMemoryBackend(MemoryBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MemcacheMemoryBackend(MemoryBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)