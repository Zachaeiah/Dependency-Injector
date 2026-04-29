from typing import Callable, Any, Type

class Provider:
    def __init__(self, factory: Callable[..., Any] | Type, singleton: bool):
        """Encapsulates the creation logic for a dependency.

        A provider can either wrap a factory function or a class type and
        controls whether the created instance should be reused (singleton)
        or recreated on each request.

        Args:
            factory (Callable[..., Any] | Type): Function or class used to create the instance.
            singleton (bool): If True, caches and returns a single instance.
        """
        self.factory: Callable[..., Any] | Type = factory
        self.singleton:bool = singleton
        self._instance = None

    def get(self, container, dry_run=False):
        """Retrieves an instance of the dependency.

        If configured as a singleton, returns the cached instance or creates
        and stores it on first access. Supports a dry run mode for validation
        without mutating internal state.

        Args:
            container: The container used for resolving nested dependencies.
            dry_run (bool, optional): If True, does not cache singleton instances. Defaults to False.

        Returns:
            Any: The resolved or newly created instance.
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
        """Creates a new instance using the configured factory.

        If the factory is a class type, it is constructed using the container's
        injector to resolve its dependencies. Otherwise, the factory is called
        directly.

        Args:
            container: The container used for dependency resolution.

        Returns:
            Any: A newly created instance.
        """
        if isinstance(self.factory, type):
            return container._injector.construct(self.factory)
        return self.factory()