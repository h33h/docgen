"""Configuration primitives shared by document and presentation models."""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Base model that treats unknown keys as configuration errors."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class ProjectKind(str, Enum):
    DOCUMENT = "document"
    PRESENTATION = "presentation"
