"""Block rendering registry and shared context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from docx.document import Document as DocxDocument

from docgen.config.document import ContentBlock, DocumentConfig
from docgen.document.citations import CitationRegistry


@dataclass
class RenderContext:
    doc: DocxDocument
    config: DocumentConfig
    citations: CitationRegistry
    project_root: Path
    temp_dir: Path | None


BlockRenderer = Callable[[ContentBlock, RenderContext], None]


class BlockRendererRegistry:
    _renderers: dict[str, BlockRenderer] = {}

    @classmethod
    def register(cls, type_name: str):
        def decorator(renderer: BlockRenderer):
            cls._renderers[type_name] = renderer
            return renderer

        return decorator

    @classmethod
    def render(cls, block: ContentBlock, context: RenderContext) -> None:
        renderer = cls._renderers.get(block.type)
        if renderer is None:
            raise ValueError(f"unsupported block type: {block.type}")
        renderer(block, context)
