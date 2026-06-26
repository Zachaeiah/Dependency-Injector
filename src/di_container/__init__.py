"""
Dependency Injection Container

Lightweight, explicit dependency injection framework focused on:
- Constructor-based injection
- Scoped resolution
- Minimal magic, maximum control

Public API is intentionally small and stable.
"""

# -------------------------
# Public API
# -------------------------
from .container import Container
from .injector import Injector, Inject
from .exceptions import DependencyNotFoundError

__all__ = (
    "Container",
    "Injector",
    "Inject",
    "DependencyNotFoundError",
    "create_container",
)

# -------------------------
# Metadata
# -------------------------
__version__ = "0.1.3"
__author__ = "Zachariah"
__license__ = "MIT"

# -------------------------
# Convenience API
# -------------------------
def create_container() -> Container:
    """Factory helper for creating a default container.

    Exists to provide a stable entrypoint if initialization logic
    evolves (config hooks, plugins, etc).

    Returns:
        Container: New container instance.
    """
    return Container()