"""Pydantic contract for generic PPTX projects."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .common import StrictModel
from .document import ResourcesConfig


class TitleSlide(StrictModel):
    type: Literal["title"]
    title: str | None = None
    subtitle: str | None = None
    lines: list[str] = Field(default_factory=list)


class TextSlide(StrictModel):
    type: Literal["text"]
    title: str
    text: str
    subtitle: str | None = None


class BulletsSlide(StrictModel):
    type: Literal["bullets"]
    title: str
    items: list[str] = Field(min_length=1)
    subtitle: str | None = None


class ContentsSlide(StrictModel):
    type: Literal["contents"]
    title: str = "Contents"
    items: list[str] = Field(min_length=1)


class TwoColumnSlide(StrictModel):
    type: Literal["two_column"]
    title: str
    left: list[str] = Field(min_length=1)
    right: list[str] = Field(min_length=1)
    left_title: str | None = None
    right_title: str | None = None


class TableSlide(StrictModel):
    type: Literal["table"]
    title: str | None = None
    ref: str


class FigureSlide(StrictModel):
    type: Literal["figure"]
    title: str | None = None
    ref: str
    caption: str | None = None


class SourcesSlide(StrictModel):
    type: Literal["sources"]
    title: str = "Sources"
    items: list[str] = Field(min_length=1)


class ThanksSlide(StrictModel):
    type: Literal["thanks"]
    title: str = "Thank you"
    subtitle: str | None = None


PresentationSlide = Annotated[
    TitleSlide
    | TextSlide
    | BulletsSlide
    | ContentsSlide
    | TwoColumnSlide
    | TableSlide
    | FigureSlide
    | SourcesSlide
    | ThanksSlide,
    Field(discriminator="type"),
]


class PresentationConfig(StrictModel):
    kind: Literal["presentation"]
    title: str
    subtitle: str | None = None
    author: str | None = None
    theme: Literal["classic", "modern"] = "classic"
    output: Path = Path("presentation.pptx")
    resources: ResourcesConfig = Field(default_factory=ResourcesConfig)
    slides: list[PresentationSlide] = Field(min_length=1)

    @model_validator(mode="after")
    def presentation_graph_is_consistent(self):
        if self.output.suffix.lower() != ".pptx":
            raise ValueError("presentation output must use .pptx extension")
        table_ids = {table.id for table in self.resources.tables}
        figure_ids = {figure.id for figure in self.resources.figures}
        for slide in self.slides:
            if isinstance(slide, TableSlide) and slide.ref not in table_ids:
                raise ValueError(f"unknown table resource: {slide.ref}")
            if isinstance(slide, FigureSlide) and slide.ref not in figure_ids:
                raise ValueError(f"unknown figure resource: {slide.ref}")
        return self
