"""
Dependency Injection Container Module

Provides a lightweight container for dependency management.
"""

from .container import Container, Inject
from .exceptions import DependencyNotFoundError

__all__ = [
    "Container",
    "Inject",
    "DependencyNotFoundError",
]

__version__ = "0.1.1"
__author__ = "Zachariah"