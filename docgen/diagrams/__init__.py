"""Registered chart renderers."""

from .registry import DiagramRegistry
from . import bar as _bar
from . import pie as _pie
from . import structure as _structure

__all__ = ["DiagramRegistry"]
