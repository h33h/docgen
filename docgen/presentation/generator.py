"""Typed orchestration for generic PPTX presentations."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from pptx import Presentation

from docgen.config.document import ImageFigure
from docgen.config.loader import LoadedProject, resolve_project_output
from docgen.config.presentation import (
    BulletsSlide,
    ContentsSlide,
    FigureSlide,
    PresentationConfig,
    SourcesSlide,
    TableSlide,
    TextSlide,
    ThanksSlide,
    TitleSlide,
    TwoColumnSlide,
)
from docgen.diagrams import DiagramRegistry
from docgen.document.resources import ResourceRegistry
from docgen.io import atomic_save

from .slides import SlideFactory
from .themes import get_theme


def resolve_output_path(loaded: LoadedProject, output: Path | None) -> Path:
    if output is None:
        target = resolve_project_output(loaded.root, loaded.config.output)
    else:
        target = output.resolve(strict=False)
    if target.suffix.lower() != ".pptx":
        raise ValueError("presentation output must use .pptx extension")
    return target


class PresentationGenerator:
    def __init__(self, loaded: LoadedProject):
        if not isinstance(loaded.config, PresentationConfig):
            raise TypeError("PresentationGenerator requires PresentationConfig")
        self.loaded = loaded

    def generate(self, output: Path | None = None) -> Path:
        config = self.loaded.config
        target = resolve_output_path(self.loaded, output)
        target.parent.mkdir(parents=True, exist_ok=True)
        presentation = Presentation()
        factory = SlideFactory(presentation, get_theme(config.theme))
        resources = ResourceRegistry(config.resources)

        with TemporaryDirectory(prefix="docgen-") as temporary:
            temporary_dir = Path(temporary)
            for slide in config.slides:
                if isinstance(slide, TitleSlide):
                    factory.add_title_slide(
                        slide.title or config.title,
                        slide.subtitle if slide.subtitle is not None else config.subtitle,
                        config.author,
                        slide.lines,
                    )
                elif isinstance(slide, ContentsSlide):
                    factory.add_contents_slide(slide.title, slide.items)
                elif isinstance(slide, TextSlide):
                    factory.add_text_slide(slide.title, slide.text, slide.subtitle)
                elif isinstance(slide, BulletsSlide):
                    factory.add_bullets_slide(slide.title, slide.items, slide.subtitle)
                elif isinstance(slide, TwoColumnSlide):
                    factory.add_two_column_slide(
                        slide.title,
                        slide.left,
                        slide.right,
                        slide.left_title,
                        slide.right_title,
                    )
                elif isinstance(slide, TableSlide):
                    table = resources.table(slide.ref)
                    factory.add_table_slide(slide.title or table.caption or "", table)
                elif isinstance(slide, FigureSlide):
                    figure = resources.figure(slide.ref)
                    if isinstance(figure, ImageFigure):
                        image_path = figure.path
                    else:
                        image_path = DiagramRegistry.render(figure, temporary_dir)
                    factory.add_figure_slide(
                        slide.title or getattr(figure, "title", None) or "",
                        image_path,
                        slide.caption if slide.caption is not None else figure.caption,
                    )
                elif isinstance(slide, SourcesSlide):
                    factory.add_sources_slide(slide.title, slide.items)
                elif isinstance(slide, ThanksSlide):
                    factory.add_thanks_slide(slide.title, slide.subtitle)
                else:
                    raise ValueError(f"unsupported slide type: {slide.type}")
            return atomic_save(presentation.save, target)
