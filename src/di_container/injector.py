import inspect
from typing import Type, Any, get_type_hints
from .exceptions import DependencyNotFoundError
from .types import Key
import sys


def _build_namespaces(cls):
    module = sys.modules[cls.__module__]
    globalns = vars(module)

    # Walk stack to find function locals that contain the class
    localns = {}

    for frame_info in inspect.stack():
        frame_locals = frame_info.frame.f_locals

        # If this class exists in that frame, we found the defining scope
        if cls.__name__ in frame_locals:
            localns = frame_locals
            break

    return globalns, localns

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

        globalns, localns = _build_namespaces(cls)

        type_hints = get_type_hints(cls.__init__, globalns=globalns, localns=localns)

        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD
            ):
                continue

            ann = type_hints.get(name, param.annotation)

            if ann is inspect.Parameter.empty:
                if param.default is not inspect.Parameter.empty:
                    continue
                raise TypeError(f"Missing type annotation for '{name}' in {cls}")

            if isinstance(param.default, Inject):
                inject = param.default
                dependency = self.container.resolve(inject.cls, inject.name)
            else:
                dependency = self.container.resolve(ann)

            kwargs[name] = dependency

        return cls(**kwargs)