from typing import Type, TypeVar, Callable, Optional
from .types import Key
from .provider import Provider
from .scope import Scope
from .injector import Injector
from .exceptions import DependencyNotFoundError

T = TypeVar("T")


class Container:
    def __init__(self):
        """Dependency injection container responsible for managing registrations,
        object lifetimes, and resolution of dependencies.

        Initializes the root scope, injector, and circular dependency tracking.
        """
        self._scope = Scope()
        self._injector = Injector(self)
        self._resolving = []

    # -------------------------
    # Registration
    # -------------------------
    def register(
        self,
        cls: Type[T],
        provider: Callable[..., T] | Type[T],
        singleton: bool = False,
        name: Optional[str] = None,
    ) -> None:
        """Registers a dependency provider for a given type.

        Args:
            cls (Type[T]): The abstraction or type being registered.
            provider (Callable[..., T] | Type[T]): Factory function or class used to create the instance.
            singleton (bool, optional): If True, the instance is created once and reused. Defaults to False.
            name (Optional[str], optional): Optional qualifier to distinguish multiple bindings of the same type.
        """
        key: Key = (cls, name)
        self._scope.providers[key] = Provider(provider, singleton)

    def register_instance(self, cls: Type[T], instance: T, name=None) -> None:
        """Registers a pre-created instance as a singleton.

        Args:
            cls (Type[T]): The abstraction or type being registered.
            instance (T): The concrete instance to bind.
            name (Optional[str], optional): Optional qualifier for named bindings.
        """
        key: Key = (cls, name)
        p = Provider(lambda: instance, True)
        p._instance = instance
        self._scope.providers[key] = p

    # -------------------------
    # Resolution
    # -------------------------
    def resolve(self, cls: Type[T], name: str | None = None) -> T:
        """Resolves an instance of the requested type.

        Attempts to retrieve a registered provider. If none exists,
        falls back to automatic construction using dependency injection.

        Args:
            cls (Type[T]): The type to resolve.
            name (str | None, optional): Optional qualifier for named bindings.

        Raises:
            RuntimeError: If a circular dependency is detected.
            DependencyNotFoundError: If a named dependency is not registered.

        Returns:
            T: The resolved instance.
        """
        key: Key = (cls, name)

        if key in self._resolving:
            raise RuntimeError(f"Circular dependency: {self._resolving} -> {key}")

        provider = self._scope.get_provider(key)

        if provider is None and name is not None:
            raise DependencyNotFoundError(cls, name)

        self._resolving.append(key)
        try:
            if provider:
                return provider.get(self)

            # fallback auto construct
            return self._injector.construct(cls)

        except DependencyNotFoundError:
            raise
        except Exception:
            raise  # let real bugs surface

        finally:
            self._resolving.pop()

    # -------------------------
    # Scope
    # -------------------------
    def create_scope(self) -> 'Container':
        """Creates a child container scope.

        The child scope inherits providers from the parent but can override
        or extend registrations independently.

        Returns:
            Container: A new scoped container instance.
        """
        child:Container = Container()
        child._scope = Scope(parent=self._scope)
        return child
    
    def validate(self, fail_fast: bool = True):
        """Validates all registered dependencies by attempting resolution.

        Useful for detecting missing dependencies or configuration issues
        at startup rather than runtime.

        Args:
            fail_fast (bool, optional): If True, raises immediately on first error.
                                       If False, collects all errors. Defaults to True.

        Returns:
            list: A list of (key, exception) tuples if fail_fast is False.
        """
        errors = []

        for key in self._scope.providers.keys():
            cls, name = key
            try:
                # force resolution
                self.resolve(cls, name)
            except Exception as e:
                if fail_fast:
                    raise
                errors.append((key, e))

        return errors