"""Pydantic contract for generic DOCX projects."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, PositiveFloat, PositiveInt, model_validator

from .common import Alignment, StrictModel


class MarginsConfig(StrictModel):
    left_cm: PositiveFloat = 2
    right_cm: PositiveFloat = 2
    top_cm: PositiveFloat = 2
    bottom_cm: PositiveFloat = 2


class FontConfig(StrictModel):
    name: str = "Arial"
    size_pt: PositiveFloat = 11


class PageNumberConfig(StrictModel):
    position: Literal["off", "header", "footer"] = "off"
    alignment: Alignment = Alignment.CENTER


class DocumentFormatting(StrictModel):
    page_size: Literal["A4", "LETTER"] = "A4"
    orientation: Literal["portrait", "landscape"] = "portrait"
    margins: MarginsConfig = Field(default_factory=MarginsConfig)
    font: FontConfig = Field(default_factory=FontConfig)
    heading_sizes_pt: dict[int, PositiveFloat] = Field(
        default_factory=lambda: {1: 18, 2: 16, 3: 14, 4: 12, 5: 11, 6: 11}
    )
    line_spacing: PositiveFloat = 1.15
    first_line_indent_cm: float = 0
    space_before_pt: float = 0
    space_after_pt: float = 0
    page_number: PageNumberConfig = Field(default_factory=PageNumberConfig)

    @model_validator(mode="after")
    def heading_levels_are_complete(self):
        if set(self.heading_sizes_pt) != set(range(1, 7)):
            raise ValueError("heading_sizes_pt must define levels 1 through 6")
        return self


class DocumentMetadata(StrictModel):
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    comments: str | None = None
    category: str | None = None


class ParagraphBlock(StrictModel):
    type: Literal["paragraph"]
    text: str
    alignment: Alignment = Alignment.LEFT
    bold: bool = False
    italic: bool = False
    space_before_pt: float | None = None
    space_after_pt: float | None = None


class HeadingBlock(StrictModel):
    type: Literal["heading"]
    text: str
    level: int = Field(ge=1, le=6)
    alignment: Alignment = Alignment.LEFT
    include_in_toc: bool = True


class BulletListBlock(StrictModel):
    type: Literal["bullet_list"]
    items: list[str] = Field(min_length=1)
    level: int = Field(default=0, ge=0, le=8)


class NumberedListBlock(StrictModel):
    type: Literal["numbered_list"]
    items: list[str] = Field(min_length=1)
    level: int = Field(default=0, ge=0, le=8)
    start: PositiveInt = 1


class TableBlock(StrictModel):
    type: Literal["table"]
    ref: str


class FigureBlock(StrictModel):
    type: Literal["figure"]
    ref: str
    width_inches: PositiveFloat | None = None


class PageBreakBlock(StrictModel):
    type: Literal["page_break"]


ContentBlock = Annotated[
    ParagraphBlock
    | HeadingBlock
    | BulletListBlock
    | NumberedListBlock
    | TableBlock
    | FigureBlock
    | PageBreakBlock,
    Field(discriminator="type"),
]


class TableResource(StrictModel):
    id: str
    headers: list[str] | None = None
    rows: list[list[str]] = Field(min_length=1)
    column_widths_cm: list[PositiveFloat] | None = None
    caption: str | None = None

    @model_validator(mode="after")
    def rows_have_consistent_width(self):
        widths = {len(row) for row in self.rows}
        if self.headers is not None:
            widths.add(len(self.headers))
        if len(widths) != 1 or 0 in widths:
            raise ValueError("table rows and headers must have the same width")
        column_count = next(iter(widths))
        if self.column_widths_cm is not None and len(self.column_widths_cm) != column_count:
            raise ValueError("column_widths_cm must match table width")
        return self


class ChartOptions(StrictModel):
    figsize: tuple[PositiveFloat, PositiveFloat] = (10, 7)
    dpi: PositiveInt = 300
    show_values: bool = True
    grid: bool = False
    xlabel: str | None = None
    ylabel: str | None = None


class PieOptions(StrictModel):
    figsize: tuple[PositiveFloat, PositiveFloat] = (10, 7)
    dpi: PositiveInt = 300
    show_percentages: bool = True
    start_angle: float = 90
    minimum_label_percent: float = Field(default=3, ge=0, le=100)


class ImageFigure(StrictModel):
    id: str
    type: Literal["image"]
    path: Path
    caption: str | None = None
    width_inches: PositiveFloat = 6


class CategoryFigure(StrictModel):
    id: str
    labels: list[str] = Field(min_length=1)
    values: list[float] = Field(min_length=1)
    caption: str | None = None
    title: str | None = None
    colors: list[str] | None = None
    width_inches: PositiveFloat = 6

    @model_validator(mode="after")
    def category_lengths_match(self):
        if len(self.labels) != len(self.values):
            raise ValueError("figure labels and values must have equal length")
        if self.colors is not None and len(self.colors) != len(self.labels):
            raise ValueError("figure colors must match labels")
        return self


class BarFigure(CategoryFigure):
    type: Literal["bar"]
    options: ChartOptions = Field(default_factory=ChartOptions)


class HorizontalBarFigure(CategoryFigure):
    type: Literal["horizontal_bar"]
    options: ChartOptions = Field(default_factory=ChartOptions)


class PieFigure(CategoryFigure):
    type: Literal["pie"]
    options: PieOptions = Field(default_factory=PieOptions)


class StructureNode(StrictModel):
    id: str
    label: str
    x: float | None = None
    y: float | None = None
    shape: Literal["rect", "circle"] = "rect"
    size: PositiveFloat | None = None
    width: PositiveFloat | None = None
    height: PositiveFloat | None = None
    color: str = "#95a5a6"
    font_size: PositiveFloat = 10


class StructureConnection(StrictModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    label: str | None = None


class StructureOptions(StrictModel):
    figsize: tuple[PositiveFloat, PositiveFloat] = (10, 7)
    dpi: PositiveInt = 300
    layout: Literal["manual", "tree", "grid", "force"] = "manual"
    layout_direction: Literal["TB", "LR"] = "TB"
    node_spacing: PositiveFloat = 0.15
    level_spacing: PositiveFloat = 0.2
    grid_columns: PositiveInt | None = None
    force_iterations: PositiveInt = 50
    force_k: PositiveFloat = 0.3
    force_repulsion: PositiveFloat = 0.1
    adjust_overlaps: bool = True
    overlap_iterations: PositiveInt = 10
    minimum_padding: float = Field(default=0.02, ge=0)
    bounds_margin: float = Field(default=0.05, ge=0)


class StructureFigure(StrictModel):
    id: str
    type: Literal["structure"]
    nodes: list[StructureNode] = Field(min_length=1)
    connections: list[StructureConnection] = Field(default_factory=list)
    caption: str | None = None
    title: str | None = None
    width_inches: PositiveFloat = 6
    options: StructureOptions = Field(default_factory=StructureOptions)

    @model_validator(mode="after")
    def graph_is_consistent(self):
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("duplicate structure node id")
        known = set(node_ids)
        for connection in self.connections:
            if connection.from_id not in known or connection.to_id not in known:
                raise ValueError("connection references unknown structure node")
        if self.options.layout == "manual" and any(
            node.x is None or node.y is None for node in self.nodes
        ):
            raise ValueError("manual structure layout requires x and y for every node")
        return self


FigureResource = Annotated[
    ImageFigure | BarFigure | HorizontalBarFigure | PieFigure | StructureFigure,
    Field(discriminator="type"),
]


class ResourcesConfig(StrictModel):
    tables: list[TableResource] = Field(default_factory=list)
    figures: list[FigureResource] = Field(default_factory=list)

    @model_validator(mode="after")
    def ids_are_unique(self):
        table_ids = [table.id for table in self.tables]
        figure_ids = [figure.id for figure in self.figures]
        if len(table_ids) != len(set(table_ids)):
            raise ValueError("duplicate table resource id")
        if len(figure_ids) != len(set(figure_ids)):
            raise ValueError("duplicate figure resource id")
        return self


class ReferenceConfig(StrictModel):
    id: str
    text: str


class ContentSection(StrictModel):
    type: Literal["content"]
    title: str | None = None
    level: int = Field(default=1, ge=1, le=6)
    include_in_toc: bool = True
    page_break_before: bool = False
    content: list[ContentBlock] | None = None
    content_file: Path | None = None

    @model_validator(mode="after")
    def exactly_one_content_source(self):
        if (self.content is None) == (self.content_file is None):
            raise ValueError("content section requires exactly one of content or content_file")
        return self


class TocSection(StrictModel):
    type: Literal["toc"]
    title: str | None = "Contents"
    min_level: int = Field(default=1, ge=1, le=6)
    max_level: int = Field(default=3, ge=1, le=6)
    page_break_before: bool = False

    @model_validator(mode="after")
    def level_range_is_ordered(self):
        if self.min_level > self.max_level:
            raise ValueError("toc min_level must not exceed max_level")
        return self


class BibliographySection(StrictModel):
    type: Literal["bibliography"]
    title: str | None = "Sources"
    page_break_before: bool = False
    prefix: str = "{number} "

    @model_validator(mode="after")
    def prefix_contains_number(self):
        if "{number}" not in self.prefix:
            raise ValueError("bibliography prefix must contain {number}")
        return self


DocumentSection = Annotated[
    ContentSection | TocSection | BibliographySection,
    Field(discriminator="type"),
]


class DocumentConfig(StrictModel):
    kind: Literal["document"]
    output: Path = Path("document.docx")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    formatting: DocumentFormatting = Field(default_factory=DocumentFormatting)
    resources: ResourcesConfig = Field(default_factory=ResourcesConfig)
    references: list[ReferenceConfig] = Field(default_factory=list)
    sections: list[DocumentSection] = Field(min_length=1)

    @model_validator(mode="after")
    def document_graph_is_consistent(self):
        if self.output.suffix.lower() != ".docx":
            raise ValueError("document output must use .docx extension")
        reference_ids = [reference.id for reference in self.references]
        if len(reference_ids) != len(set(reference_ids)):
            raise ValueError("duplicate reference id")
        table_ids = {table.id for table in self.resources.tables}
        figure_ids = {figure.id for figure in self.resources.figures}
        for section in self.sections:
            if not isinstance(section, ContentSection) or section.content is None:
                continue
            for block in section.content:
                if isinstance(block, TableBlock) and block.ref not in table_ids:
                    raise ValueError(f"unknown table resource: {block.ref}")
                if isinstance(block, FigureBlock) and block.ref not in figure_ids:
                    raise ValueError(f"unknown figure resource: {block.ref}")
        return self
