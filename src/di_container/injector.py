import inspect
from typing import Type, Any
from .exceptions import DependencyNotFoundError
from .types import Key

class Inject:
    def __init__(self, cls: Type, name: str | None = None):
        """_summary_

        Args:
            cls (Type): _description_
            name (str | None, optional): _description_. Defaults to None.
        """
        self.cls = cls
        self.name = name

class Injector:
    def __init__(self, container):
        """_summary_

        Args:
            container (_type_): _description_
        """
        self.container = container

    def construct(self, cls: Type) -> Any:
        """_summary_

        Args:
            cls (Type): _description_

        Raises:
            TypeError: _description_

        Returns:
            Any: _description_
        """
        sig = inspect.signature(cls.__init__)
        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,   # *args
                inspect.Parameter.VAR_KEYWORD       # **kwargs
            ):
                continue

            if param.annotation is inspect.Parameter.empty:
                if param.default is not inspect.Parameter.empty:
                    continue  # allow default-only params
                raise TypeError(f"Missing type annotation for '{name}' in {cls}")


            if isinstance(param.default, Inject):
                inject = param.default
                dependency = self.container.resolve(inject.cls, inject.name)
            else:
                dependency = self.container.resolve(param.annotation)

            kwargs[name] = dependency

        return cls(**kwargs)