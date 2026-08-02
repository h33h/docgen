"""Registered generic DOCX section renderers."""

from .base import SectionRendererRegistry
from . import bibliography as _bibliography
from . import content as _content
from . import toc as _toc

__all__ = ["SectionRendererRegistry"]
