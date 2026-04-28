import pytest
from di_container import Container, Inject

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
class Logger:
    pass

class FileLogger(Logger):
    pass

class Service:
    def __init__(self, logger: Logger = Inject(Logger, "file")):
        self.logger = logger

def test_named_injection():
    c = Container()
    c.register(Logger, Logger)
    c.register(Logger, FileLogger, name="file")

    s = c.resolve(Service)

    assert isinstance(s.logger, FileLogger)

# -------------------------
# Factory provider
# -------------------------
def factory():
    return A()

def test_factory_provider():
    c = Container()
    c.register(A, factory)

    a = c.resolve(A)

    assert isinstance(a, A)

# -------------------------
# Scoped override
# -------------------------
def test_scope_override():
    c = Container()
    c.register(A, A)

    child = c.create_scope()

    class A2(A):
        pass

    child.register(A, A2)

    parent_a = c.resolve(A)
    child_a = child.resolve(A)

    assert type(parent_a) is A
    assert type(child_a) is A2

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
# Ignore *args, **kwargs
# -------------------------
class Flexible:
    def __init__(self, *args, **kwargs):
        pass

def test_ignore_varargs():
    c = Container()

    obj = c.resolve(Flexible)

    assert isinstance(obj, Flexible)