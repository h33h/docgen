"""Section rendering registry."""

from typing import Callable

from docgen.config.document import DocumentSection
from docgen.document.blocks import RenderContext

SectionRenderer = Callable[[DocumentSection, RenderContext], None]


class SectionRendererRegistry:
    _renderers: dict[str, SectionRenderer] = {}

    @classmethod
    def register(cls, type_name: str):
        def decorator(renderer: SectionRenderer):
            cls._renderers[type_name] = renderer
            return renderer

        return decorator

    @classmethod
    def render(cls, section: DocumentSection, context: RenderContext) -> None:
        renderer = cls._renderers.get(section.type)
        if renderer is None:
            raise ValueError(f"unsupported section type: {section.type}")
        renderer(section, context)
