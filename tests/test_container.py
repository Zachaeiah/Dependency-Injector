import pytest
from src.di_container import Container, Inject

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
# Singleton behavior
# -------------------------
def test_singleton():
    c = Container()
    c.register(A, A, singleton=True)

    a1 = c.resolve(A)
    a2 = c.resolve(A)

    assert a1 is a2
