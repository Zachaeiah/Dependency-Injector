"""
Dependency Injection Container Module

Provides a lightweight container for dependency management.
"""

from .container import Container
from .injector import Injector, Inject
from .exceptions import DependencyNotFoundError

__all__ = [
    "Container",
    "Injector",
    "Inject",
    "DependencyNotFoundError"
]

__version__ = "0.1.1"
__author__ = "Zachariah"