"""
StarLive examples package.

This package provides example applications demonstrating StarLive functionality
with both Starlette and FastAPI frameworks.
"""

from .app_factory import create_app, create_fastapi_app, create_starlette_app
from .shared import items_store

__all__ = [
    "create_app",
    "create_fastapi_app",
    "create_starlette_app",
    "items_store",
]
