"""Typed configuration contracts for docgen projects."""

from .common import Alignment, ProjectKind, StrictModel
from .loader import ConfigLoadError, LoadedProject, load_project

__all__ = [
    "Alignment",
    "ConfigLoadError",
    "LoadedProject",
    "ProjectKind",
    "StrictModel",
    "load_project",
]
