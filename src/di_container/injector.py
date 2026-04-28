import inspect
from typing import Type, Any
from .exceptions import DependencyNotFoundError
from .types import Key
from .container import Inject  # reuse

class Injector:
    def __init__(self, container):
        self.container = container

    def construct(self, cls: Type) -> Any:
        sig = inspect.signature(cls.__init__)
        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            if param.annotation is inspect.Parameter.empty:
                raise TypeError(f"Missing type annotation for '{name}' in {cls}")

            ann = param.annotation

            if isinstance(ann, Inject):
                dep = self.container.resolve(ann.cls, ann.name)
            else:
                dep = self.container.resolve(ann)

            kwargs[name] = dep

        return cls(**kwargs)