"""Command-line interface for docgen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .config.common import ProjectKind
from .config.document import DocumentConfig
from .config.loader import ConfigLoadError, load_project
from .config.presentation import PresentationConfig
from .document import DocumentGenerator
from .presentation import PresentationGenerator


DOCUMENT_TEMPLATE = {
    "kind": "document",
    "metadata": {"title": "New document"},
    "sections": [
        {
            "type": "content",
            "content": [{"type": "paragraph", "text": "Start writing here."}],
        }
    ],
}

PRESENTATION_TEMPLATE = {
    "kind": "presentation",
    "title": "New presentation",
    "slides": [
        {"type": "title"},
        {"type": "text", "title": "Overview", "text": "Start writing here."},
    ],
}


def init_project(target: Path, kind: ProjectKind = ProjectKind.DOCUMENT) -> Path:
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"target directory is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)
    (target / "assets").mkdir(exist_ok=True)

    if kind == ProjectKind.PRESENTATION:
        filename = "presentation.json"
        template = PRESENTATION_TEMPLATE
    else:
        filename = "document.json"
        template = DOCUMENT_TEMPLATE
        (target / "content").mkdir(exist_ok=True)

    source = target / filename
    source.write_text(
        json.dumps(template, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    load_project(source)
    return source


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docgen",
        description="Generate DOCX documents and PPTX presentations from JSON.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="create a minimal project")
    init_parser.add_argument("path", type=Path)
    init_parser.add_argument(
        "--kind",
        choices=[kind.value for kind in ProjectKind],
        default=ProjectKind.DOCUMENT.value,
    )
    build_parser = subparsers.add_parser("build", help="build a DOCX or PPTX project")
    build_parser.add_argument("config", type=Path)
    build_parser.add_argument("-o", "--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "init":
            result = init_project(args.path, ProjectKind(args.kind))
            print(result)
            return 0
        if args.command == "build":
            loaded = load_project(args.config)
            if isinstance(loaded.config, DocumentConfig):
                result = DocumentGenerator(loaded).generate(args.output)
            elif isinstance(loaded.config, PresentationConfig):
                result = PresentationGenerator(loaded).generate(args.output)
            else:
                raise ConfigLoadError(f"unsupported project kind: {loaded.config.kind}")
            print(result)
            return 0
        raise ValueError(f"unsupported command: {args.command}")
    except (ConfigLoadError, OSError, RuntimeError, ValueError) as error:
        print(f"docgen: error: {error}", file=sys.stderr)
        return 1


def entrypoint() -> None:
    raise SystemExit(main())
