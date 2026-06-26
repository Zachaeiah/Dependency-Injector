import inspect
from typing import Type, Any, get_type_hints
from .exceptions import DependencyNotFoundError
from .types import Key
import sys


def _build_namespaces(cls):
    """Builds the global and local namespaces required for resolving type hints.

    This is necessary to correctly evaluate forward references and locally defined
    classes when using get_type_hints.

    Args:
        cls (Type): The class whose constructor annotations need resolution.

    Returns:
        tuple: (globalns, localns) used for type hint evaluation.
    """
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
        """Marker used to explicitly define how a dependency should be resolved.

        Allows overriding default type-based resolution by specifying both
        the dependency type and an optional named binding.

        Args:
            cls (Type): The dependency type to resolve.
            name (str | None, optional): Optional qualifier for named bindings.
        """
        self.cls = cls
        self.name = name

class Injector:
    def __init__(self, container):
        """Handles automatic construction of objects using dependency injection.

        Uses constructor introspection and type hints to resolve dependencies
        from the container.

        Args:
            container: The container responsible for resolving dependencies.
        """
        self.container = container

    def construct(self, cls: Type) -> Any:
        """Constructs an instance of a class by resolving its dependencies.

        Inspects the constructor signature and resolves required constructor
        parameters from the container.

        Rules:
            - Required annotated parameters are auto-injected.
            - Parameters with normal default values are skipped.
            - Parameters using Inject(...) are explicitly injected.
            - *args and **kwargs are ignored.

        Args:
            cls (Type): The class to instantiate.

        Raises:
            TypeError: If a required parameter is missing a type annotation.

        Returns:
            Any: A fully constructed instance of the class.
        """
        sig = inspect.signature(cls.__init__)

        globalns, localns = _build_namespaces(cls)
        type_hints = get_type_hints(
            cls.__init__,
            globalns=globalns,
            localns=localns,
        )

        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            # def __init__(self, reader = Inject(IPDFReader)):
            if isinstance(param.default, Inject):
                inject = param.default
                dependency = self.container.resolve(inject.cls, inject.name)
                kwargs[name] = dependency
                continue
            
            # def __init__(self, y_tolerance: float = 3.0):
            if param.default is not inspect.Parameter.empty:
                continue

            # def __init__(self, reader: IPDFReader):
            ann = type_hints.get(name, param.annotation)

            if ann is inspect.Parameter.empty:
                raise TypeError(f"Missing type annotation for '{name}' in {cls}")

            dependency = self.container.resolve(ann)
            kwargs[name] = dependency

        return cls(**kwargs)