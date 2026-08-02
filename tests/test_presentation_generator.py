import json
from pathlib import Path

from pptx import Presentation
import pytest

from docgen.config.loader import load_project
from docgen.presentation.generator import PresentationGenerator
from docgen.presentation.slides import SlideFactory


def write_presentation(tmp_path: Path) -> Path:
    config = {
        "kind": "presentation",
        "title": "Demo",
        "author": "Author",
        "output": "result.pptx",
        "resources": {
            "tables": [{"id": "table", "headers": ["A"], "rows": [["1"]]}],
            "figures": [
                {"id": "chart", "type": "bar", "labels": ["A"], "values": [1]}
            ],
        },
        "slides": [
            {"type": "title"},
            {"type": "text", "title": "Text", "text": "Body"},
            {"type": "bullets", "title": "List", "items": ["One"]},
            {"type": "table", "title": "Table", "ref": "table"},
            {"type": "figure", "title": "Chart", "ref": "chart"},
        ],
    }
    source = tmp_path / "presentation.json"
    source.write_text(json.dumps(config), encoding="utf-8")
    return source


def test_presentation_generator_builds_readable_pptx(tmp_path: Path):
    source = write_presentation(tmp_path)
    output = PresentationGenerator(load_project(source)).generate()
    presentation = Presentation(output)
    assert output == tmp_path / "result.pptx"
    assert output.stat().st_size > 0
    assert len(presentation.slides) == 5
    all_text = "\n".join(
        shape.text
        for slide in presentation.slides
        for shape in slide.shapes
        if hasattr(shape, "text")
    )
    assert "Demo" in all_text
    assert "Body" in all_text


def test_presentation_failure_preserves_existing_target(tmp_path: Path, monkeypatch):
    source = write_presentation(tmp_path)
    target = tmp_path / "result.pptx"
    target.write_bytes(b"original")

    def fail(*args, **kwargs):
        raise RuntimeError("slide failed")

    monkeypatch.setattr(SlideFactory, "add_text_slide", fail)
    with pytest.raises(RuntimeError, match="slide failed"):
        PresentationGenerator(load_project(source)).generate()
    assert target.read_bytes() == b"original"
    assert list(tmp_path.glob(".docgen-*")) == []
