class Scope:
    def __init__(self, parent=None):
        """Represents a hierarchical scope for dependency registrations.

        Scopes allow layering of providers, where a child scope can override
        or extend registrations from its parent while still falling back to it.

        Args:
            parent (Scope, optional): Parent scope to inherit providers from.
        """
        self.parent = parent
        self.providers = {}
        self.singletons = {}

    def get_provider(self, key):
        """Retrieves a provider for a given key, searching up the scope chain.

        Looks for the provider in the current scope first, then recursively
        checks parent scopes if not found.

        Args:
            key (tuple): The lookup key (typically (Type, name)).

        Returns:
            Provider | None: The matching provider if found, otherwise None.
        """
        if key in self.providers:
            return self.providers[key]
        if self.parent:
            return self.parent.get_provider(key)
        return None