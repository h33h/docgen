"""Typed chart renderer registry."""

from pathlib import Path
from typing import Callable

from docgen.config.document import FigureResource

DiagramRenderer = Callable[[FigureResource, Path], Path]


class DiagramRegistry:
    _renderers: dict[str, DiagramRenderer] = {}

    @classmethod
    def register(cls, type_name: str):
        def decorator(renderer: DiagramRenderer):
            cls._renderers[type_name] = renderer
            return renderer

        return decorator

    @classmethod
    def render(cls, resource: FigureResource, output_dir: Path) -> Path:
        renderer = cls._renderers.get(resource.type)
        if renderer is None:
            raise ValueError(f"unsupported diagram type: {resource.type}")
        output_dir.mkdir(parents=True, exist_ok=True)
        return renderer(resource, output_dir)
