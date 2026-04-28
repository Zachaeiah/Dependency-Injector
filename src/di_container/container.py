from typing import Type, TypeVar, Callable, Optional
from .types import Key
from .provider import Provider
from .scope import Scope
from .injector import Injector
from .exceptions import DependencyNotFoundError

T = TypeVar("T")


class Inject:
    def __init__(self, cls: Type, name: str | None = None):
        self.cls = cls
        self.name = name


class Container:
    def __init__(self):
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
    ):
        key: Key = (cls, name)
        self._scope.providers[key] = Provider(provider, singleton)

    def register_instance(self, cls: Type[T], instance: T, name=None):
        key: Key = (cls, name)
        p = Provider(lambda: instance, True)
        p._instance = instance
        self._scope.providers[key] = p

    # -------------------------
    # Resolution
    # -------------------------
    def resolve(self, cls: Type[T], name: str | None = None) -> T:
        key: Key = (cls, name)

        if key in self._resolving:
            raise RuntimeError(f"Circular dependency: {self._resolving} -> {key}")

        provider = self._scope.get_provider(key)

        self._resolving.append(key)
        try:
            if provider:
                return provider.get(self)

            # fallback auto construct
            return self._injector.construct(cls)

        except Exception as e:
            raise DependencyNotFoundError(cls, name) from e

        finally:
            self._resolving.pop()

    # -------------------------
    # Scope
    # -------------------------
    def create_scope(self):
        child = Container()
        child._scope = Scope(parent=self._scope)
        return child