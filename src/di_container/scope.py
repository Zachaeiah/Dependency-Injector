class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.providers = {}
        self.singletons = {}

    def get_provider(self, key):
        if key in self.providers:
            return self.providers[key]
        if self.parent:
            return self.parent.get_provider(key)
        return None