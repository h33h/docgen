"""Load and fully resolve a docgen project configuration."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from pydantic import TypeAdapter, ValidationError

from .document import (
    BulletListBlock,
    ContentBlock,
    ContentSection,
    DocumentConfig,
    ImageFigure,
    NumberedListBlock,
    ParagraphBlock,
)
from .presentation import PresentationConfig

ProjectConfig = DocumentConfig | PresentationConfig
_CONTENT_ADAPTER = TypeAdapter(list[ContentBlock])
_CITATION_PATTERN = re.compile(r"\{\{cite:([A-Za-z0-9_.-]+)\}\}")


class ConfigLoadError(ValueError):
    """A project cannot be read or does not satisfy the complete contract."""


@dataclass(frozen=True)
class LoadedProject:
    config: ProjectConfig
    source: Path
    root: Path


def resolve_project_path(root: Path, relative: Path) -> Path:
    root = root.resolve(strict=True)
    try:
        candidate = (root / relative).resolve(strict=True)
    except FileNotFoundError as error:
        raise ConfigLoadError(f"project file not found: {relative}") from error
    if not candidate.is_relative_to(root):
        raise ConfigLoadError(f"path is outside project root: {relative}")
    return candidate


def resolve_project_output(root: Path, relative: Path) -> Path:
    root = root.resolve(strict=True)
    candidate = (root / relative).resolve(strict=False)
    if not candidate.is_relative_to(root):
        raise ConfigLoadError(f"output path is outside project root: {relative}")
    return candidate


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ConfigLoadError(f"configuration file not found: {path}") from error
    except UnicodeDecodeError as error:
        raise ConfigLoadError(f"configuration is not UTF-8: {path}") from error
    except json.JSONDecodeError as error:
        raise ConfigLoadError(
            f"invalid JSON in {path}: line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error


def _validation_error(source: Path, error: ValidationError) -> ConfigLoadError:
    lines = []
    for issue in error.errors(include_url=False):
        location = ".".join(str(part) for part in issue["loc"])
        lines.append(f"{source}: {location}: {issue['msg']}")
    return ConfigLoadError("\n".join(lines))


def _resolve_content(config: DocumentConfig, root: Path, source: Path) -> DocumentConfig:
    sections = []
    for index, section in enumerate(config.sections):
        if not isinstance(section, ContentSection) or section.content_file is None:
            sections.append(section)
            continue
        content_path = resolve_project_path(root, section.content_file)
        try:
            blocks = _CONTENT_ADAPTER.validate_python(_read_json(content_path))
        except ValidationError as error:
            raise _validation_error(content_path, error) from error
        sections.append(section.model_copy(update={"content": blocks, "content_file": None}))
    try:
        return DocumentConfig.model_validate(
            config.model_copy(update={"sections": sections}).model_dump(by_alias=True)
        )
    except ValidationError as error:
        raise _validation_error(source, error) from error


def _resolve_images(config: ProjectConfig, root: Path) -> ProjectConfig:
    figures = []
    for figure in config.resources.figures:
        if isinstance(figure, ImageFigure):
            figure = figure.model_copy(update={"path": resolve_project_path(root, figure.path)})
        figures.append(figure)
    resources = config.resources.model_copy(update={"figures": figures})
    return config.model_copy(update={"resources": resources})


def _iter_citation_text(config: DocumentConfig):
    for section in config.sections:
        if not isinstance(section, ContentSection) or section.content is None:
            continue
        for block in section.content:
            if isinstance(block, ParagraphBlock):
                yield block.text
            elif isinstance(block, (BulletListBlock, NumberedListBlock)):
                yield from block.items


def _validate_citations(config: DocumentConfig) -> None:
    known = {reference.id for reference in config.references}
    for text in _iter_citation_text(config):
        for citation_id in _CITATION_PATTERN.findall(text):
            if citation_id not in known:
                raise ConfigLoadError(f"unknown citation: {citation_id}")


def load_project(path: Path | str) -> LoadedProject:
    source = Path(path).resolve(strict=False)
    data = _read_json(source)
    if not isinstance(data, dict):
        raise ConfigLoadError(f"configuration root must be an object: {source}")
    kind = data.get("kind")
    model = DocumentConfig if kind == "document" else PresentationConfig if kind == "presentation" else None
    if model is None:
        raise ConfigLoadError(f"unsupported project kind: {kind!r}")
    try:
        config: ProjectConfig = model.model_validate(data)
    except ValidationError as error:
        raise _validation_error(source, error) from error

    root = source.parent.resolve(strict=True)
    if isinstance(config, DocumentConfig):
        config = _resolve_content(config, root, source)
    config = _resolve_images(config, root)
    if isinstance(config, DocumentConfig):
        _validate_citations(config)
    return LoadedProject(config=config, source=source, root=root)
