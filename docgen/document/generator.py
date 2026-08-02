"""Orchestration and atomic persistence for generic DOCX documents."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

from docgen.config.document import DocumentConfig
from docgen.config.loader import LoadedProject, resolve_project_output
from docgen.io import atomic_save

from .blocks import RenderContext
from .citations import CitationRegistry
from .formatter import DocumentFormatter
from .sections import SectionRendererRegistry


def resolve_output_path(loaded: LoadedProject, output: Path | None) -> Path:
    if output is None:
        target = resolve_project_output(loaded.root, loaded.config.output)
    else:
        target = output.resolve(strict=False)
    if target.suffix.lower() != ".docx":
        raise ValueError("document output must use .docx extension")
    return target


class DocumentGenerator:
    def __init__(self, loaded: LoadedProject):
        if not isinstance(loaded.config, DocumentConfig):
            raise TypeError("DocumentGenerator requires DocumentConfig")
        self.loaded = loaded

    def generate(self, output: Path | None = None) -> Path:
        config = self.loaded.config
        target = resolve_output_path(self.loaded, output)
        target.parent.mkdir(parents=True, exist_ok=True)
        doc = Document()
        DocumentFormatter(config.formatting).apply(doc)
        for name, value in config.metadata.model_dump().items():
            if value is not None:
                setattr(doc.core_properties, name, value)

        with TemporaryDirectory(prefix="docgen-") as temporary:
            context = RenderContext(
                doc=doc,
                config=config,
                citations=CitationRegistry(config.references),
                project_root=self.loaded.root,
                temp_dir=Path(temporary),
            )
            for section in config.sections:
                SectionRendererRegistry.render(section, context)
            return atomic_save(doc.save, target)
