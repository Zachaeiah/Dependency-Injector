from typing import Callable, Any, Type

class Provider:
    def __init__(self, factory: Callable[..., Any] | Type, singleton: bool):
        """_summary_

        Args:
            factory (Callable[..., Any] | Type): _description_
            singleton (bool): _description_
        """
        self.factory: Callable[..., Any] | Type = factory
        self.singleton:bool = singleton
        self._instance = None

    def get(self, container, dry_run=False):
        """_summary_

        Args:
            container (_type_): _description_
            dry_run (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if self.singleton:
            if self._instance is None:
                instance = self._create(container)
                if not dry_run:
                    self._instance = instance
                return instance
            return self._instance

        return self._create(container)

    def _create(self, container):
        """_summary_

        Args:
            container (_type_): _description_

        Returns:
            _type_: _description_
        """
        if isinstance(self.factory, type):
            return container._injector.construct(self.factory)
        return self.factory()