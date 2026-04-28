import inspect
from typing import Any, Callable, Dict, Type, TypeVar
from .exceptions import DependencyNotFoundError

T = TypeVar("T")

# -------------------------
# Named injection helper
# -------------------------
class Inject:
    """ Helper class to specify named dependencies for injection in constructor parameters.
    """
    def __init__(self, cls: Type, name: str | None = None):
        """ Helper class to specify named dependencies for injection in constructor parameters.

        Args:
            cls (Type): Class to inject
            name (str | None, optional): Optional name for the provider (for multiple providers of the same class). Defaults to None.
        """
        ...


class Container:
    """A simple dependency injection container that supports constructor injection and singleton management.
    It allows you to register providers for classes and resolve instances of those classes, automatically
    """
    def __init__(self) -> None:
        """ Constructor for Container class
        """
        ...

    # -------------------------
    # Registration
    # -------------------------
    def register(
        self,
        cls: Type[T],
        provider: Callable[..., T] | Type[T],
        singleton: bool = False,
        name: str | None = None
    ) -> None:
        """ Register a provider for a given class

        Args:
            cls (Type[T]): Class to register provider for
            provider (Callable[..., T] | Type[T]): Provider function or class
            singleton (bool, optional): Whether to use singleton pattern. Defaults to False.
            name (str | None, optional): Optional name for the provider (for multiple providers of the same class). Defaults to None.
        """
        ...

    def register_instance(self, cls: Type[T], instance: T, name) -> None:
        """ Register a specific instance for a given class (singleton)

        Args:
            cls (Type[T]): Class to register instance for
            instance (T): Instance to register
            name (str | None, optional): Optional name for the provider (for multiple providers of the same class). Defaults to None.
        """
        ...

    def resolve(self, cls: Type[T], name: str | None = None) -> T:
        """ Resolve an instance of the given class, using registered providers or constructor injection.

        Args:
            cls (Type[T]): Class to resolve
            name (str | None, optional): Optional name for the provider (for multiple providers of the same class). Defaults to None.

        Raises:
            RuntimeError: If a circular dependency is detected during resolution
            DependencyNotFoundError: If no provider is registered for the class and it cannot be constructed

        Returns:
            T: Instance of the class returned by the provider or constructed directly
        """
        
        ...

    def _construct(self, cls: Type[T]) -> T:
        """ Construct an instance of the given class by resolving its constructor dependencies.

        Args:
            cls (Type[T]): Class to construct

        Raises:
            TypeError: If any constructor parameter is missing a type annotation

        Returns:
            T: Instance of the class constructed with resolved dependencies
        """
        ...
    
    def validate(self, fail_fast: bool = True) -> list[Exception]:
        """
        Validate the container by attempting to resolve all registered providers.

        Args:
            fail_fast (bool): If True, raise on first error.
                            If False, collect all errors.

        Returns:
            list[Exception]: List of validation errors (empty if valid)
        """
        ...
    
    def _validate_resolve(self, cls: Type[T], name: str | None):
        """Internal resolve used only for validation.
        Does not mutate singleton cache.

        Args:
            cls (Type[T]): _description_
            name (str | None): _description_

        Raises:
            RuntimeError: _description_
            DependencyNotFoundError: _description_
        """
        ...

    def _validate_construct(self, cls: Type[T]):
        """_summary_

        Args:
            cls (Type[T]): _description_

        Raises:
            TypeError: _description_
        """
        ...
    
    def create_scope(self) -> "Container":
        """ Create a new scope (child container) that inherits providers and singletons from the parent container. 
        This allows for scoped dependencies in sub-operations or tasks.

        Returns:
            Container: A new child container with the same providers and singletons as the parent container
        """
        ...

    def has(self, cls: Type, name: str = None) -> bool:
        """ Check if a provider is registered for a given class

        Args:
            cls (Type): Class to check for registered provider
            name (str, optional): Optional name for the provider (for multiple providers of the same class). Defaults to None.

        Returns:
            bool: True if a provider is registered for the class, False otherwise
        """
        ...

    def clear(self) -> None:
        """ Clear all registered providers and singletons from the container
        """
        ...