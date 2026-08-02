"""Registered generic DOCX block renderers."""

from .base import BlockRendererRegistry, RenderContext
from . import figure as _figure
from . import lists as _lists
from . import page_break as _page_break
from . import table as _table
from . import text as _text

__all__ = ["BlockRendererRegistry", "RenderContext"]
