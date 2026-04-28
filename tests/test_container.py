import pytest
from di_container import Container, Inject, DependencyNotFoundError

# -------------------------
# Test classes
# -------------------------
class A:
    pass

class B:
    def __init__(self, a: A):
        self.a = a

# -------------------------
# Basic resolution
# -------------------------
def test_simple_resolution():
    c = Container()
    c.register(A, A)

    b = c.resolve(B)

    assert isinstance(b, B)
    assert isinstance(b.a, A)

# -------------------------
# Deep dependency graph
# -------------------------
class C:
    def __init__(self, b: B):
        self.b = b

def test_deep_graph():
    c = Container()
    c.register(A, A)

    c_obj = c.resolve(C)

    assert isinstance(c_obj.b.a, A)


# -------------------------
# Singleton behavior
# -------------------------
def test_singleton():
    c = Container()
    c.register(A, A, singleton=True)

    assert c.resolve(A) is c.resolve(A)


def test_transient_default():
    c = Container()
    c.register(A, A)

    assert c.resolve(A) is not c.resolve(A)

# -------------------------
# Named dependency
# -------------------------
class Logger: pass
class FileLogger(Logger): pass

class Service:
    def __init__(self, logger: Logger = Inject(Logger, "file")):
        self.logger = logger

def test_named_injection():
    c = Container()
    c.register(Logger, Logger)
    c.register(Logger, FileLogger, name="file")

    s = c.resolve(Service)

    assert isinstance(s.logger, FileLogger)


def test_named_missing():
    c = Container()
    c.register(Logger, Logger)

    with pytest.raises(DependencyNotFoundError):
        c.resolve(Service)

# -------------------------
# Factory provider
# -------------------------
def factory():
    return A()

def test_factory_provider():
    c = Container()
    c.register(A, factory)

    assert isinstance(c.resolve(A), A)


def test_factory_singleton():
    calls = []

    def factory():
        calls.append(1)
        return A()

    c = Container()
    c.register(A, factory, singleton=True)

    c.resolve(A)
    c.resolve(A)

    assert len(calls) == 1

# -------------------------
# Scoped override
# -------------------------
def test_scope_override():
    c = Container()
    c.register(A, A)

    child = c.create_scope()

    class A2(A): pass
    child.register(A, A2)

    assert type(c.resolve(A)) is A
    assert type(child.resolve(A)) is A2


def test_scope_singleton_isolation():
    c = Container()
    c.register(A, A, singleton=True)

    child = c.create_scope()

    assert c.resolve(A) is child.resolve(A)  # inherited singleton


# -------------------------
# Auto-construction (no registration)
# -------------------------
def test_auto_construct():
    c = Container()

    class C:
        pass

    obj = c.resolve(C)

    assert isinstance(obj, C)

# -------------------------
# Missing dependency
# -------------------------
class NeedsMissing:
    def __init__(self, x):
        pass

def test_missing_dependency():
    c = Container()

    with pytest.raises(TypeError):
        c.resolve(NeedsMissing)

# -------------------------
# Circular dependency
# -------------------------
class X:
    def __init__(self, y: "Y"):
        pass

class Y:
    def __init__(self, x: X):
        pass

def test_circular_dependency():
    c = Container()

    with pytest.raises(RuntimeError):
        c.resolve(X)

# -------------------------
# Forward reference resolution
# -------------------------
def test_forward_reference():
    c = Container()

    class A: pass

    class B:
        def __init__(self, a: "A"):
            self.a = a

    assert isinstance(c.resolve(B).a, A)

# -------------------------
# Ignore *args, **kwargs
# -------------------------
class Flexible:
    def __init__(self, *args, **kwargs):
        pass

def test_ignore_varargs():
    c = Container()

    obj = c.resolve(Flexible)

    assert isinstance(obj, Flexible)

# -------------------------
# Default parameters should not break DI
# -------------------------
class WithDefaults:
    def __init__(self, a: A = None):
        self.a = a

def test_default_param():
    c = Container()
    c.register(A, A)

    obj = c.resolve(WithDefaults)

    assert isinstance(obj.a, A)

# -------------------------
# Explicit instance registration
# -------------------------
def test_register_instance():
    c = Container()
    instance = A()

    c.register_instance(A, instance)

    assert c.resolve(A) is instance

# -------------------------
# Multiple named providers
# -------------------------
def test_multiple_named_providers():
    c = Container()

    class A1(A): pass
    class A2(A): pass

    c.register(A, A1, name="one")
    c.register(A, A2, name="two")

    assert isinstance(c.resolve(A, "one"), A1)
    assert isinstance(c.resolve(A, "two"), A2)