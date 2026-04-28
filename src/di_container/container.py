from typing import Type, TypeVar, Callable, Optional
from .types import Key
from .provider import Provider
from .scope import Scope
from .injector import Injector
from .exceptions import DependencyNotFoundError

T = TypeVar("T")


class Container:
    def __init__(self):
        """_summary_
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
        """_summary_

        Args:
            cls (Type[T]): _description_
            provider (Callable[..., T] | Type[T]): _description_
            singleton (bool, optional): _description_. Defaults to False.
            name (Optional[str], optional): _description_. Defaults to None.
        """
        key: Key = (cls, name)
        self._scope.providers[key] = Provider(provider, singleton)

    def register_instance(self, cls: Type[T], instance: T, name=None) -> None:
        """_summary_

        Args:
            cls (Type[T]): _description_
            instance (T): _description_
            name (_type_, optional): _description_. Defaults to None.
        """
        key: Key = (cls, name)
        p = Provider(lambda: instance, True)
        p._instance = instance
        self._scope.providers[key] = p

    # -------------------------
    # Resolution
    # -------------------------
    def resolve(self, cls: Type[T], name: str | None = None) -> T:
        """_summary_

        Args:
            cls (Type[T]): _description_
            name (str | None, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_
            DependencyNotFoundError: _description_

        Returns:
            T: _description_
        """
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
        """_summary_

        Returns:
            Container: _description_
        """
        child:Container = Container()
        child._scope = Scope(parent=self._scope)
        return child
    
    def validate(self, fail_fast: bool = True):
        """_summary_

        Args:
            fail_fast (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
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