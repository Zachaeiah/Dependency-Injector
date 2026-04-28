from typing import Callable, Any, Type

class Provider:
    def __init__(self, factory: Callable[..., Any] | Type, singleton: bool):
        self.factory = factory
        self.singleton = singleton
        self._instance = None

    def get(self, container):
        if self.singleton:
            if self._instance is None:
                self._instance = self._create(container)
            return self._instance

        return self._create(container)

    def _create(self, container):
        if isinstance(self.factory, type):
            return container._injector.construct(self.factory)
        return self.factory()