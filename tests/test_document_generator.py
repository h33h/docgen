import json
from pathlib import Path

from docx import Document
import matplotlib.pyplot as plt
import pytest

from docgen.config.loader import load_project
from docgen.document.generator import DocumentGenerator
from docgen.document.sections import SectionRendererRegistry


def write_project(tmp_path: Path) -> Path:
    image = tmp_path / "image.png"
    figure, axes = plt.subplots(figsize=(1, 1))
    axes.plot([0, 1], [0, 1])
    figure.savefig(image)
    plt.close(figure)
    config = {
        "kind": "document",
        "output": "result.docx",
        "metadata": {"title": "Generated title", "author": "Author"},
        "resources": {
            "tables": [{"id": "table", "headers": ["A"], "rows": [["1"]]}],
            "figures": [{"id": "image", "type": "image", "path": "image.png"}],
        },
        "sections": [
            {
                "type": "content",
                "title": "Overview",
                "content": [
                    {"type": "paragraph", "text": "Body"},
                    {"type": "table", "ref": "table"},
                    {"type": "figure", "ref": "image"},
                ],
            }
        ],
    }
    source = tmp_path / "document.json"
    source.write_text(json.dumps(config), encoding="utf-8")
    return source


def test_document_generator_builds_readable_docx(tmp_path: Path):
    source = write_project(tmp_path)
    output = DocumentGenerator(load_project(source)).generate()
    generated = Document(output)
    assert output == tmp_path / "result.docx"
    assert generated.core_properties.title == "Generated title"
    assert generated.core_properties.author == "Author"
    assert "Overview" in [paragraph.text for paragraph in generated.paragraphs]
    assert len(generated.tables) == 1
    assert len(generated.inline_shapes) == 1


def test_generation_failure_preserves_existing_target(tmp_path: Path, monkeypatch):
    source = write_project(tmp_path)
    target = tmp_path / "result.docx"
    target.write_bytes(b"original")

    def fail(section, context):
        raise RuntimeError("render failed")

    monkeypatch.setattr(SectionRendererRegistry, "render", fail)
    with pytest.raises(RuntimeError, match="render failed"):
        DocumentGenerator(load_project(source)).generate()
    assert target.read_bytes() == b"original"
    assert list(tmp_path.glob(".docgen-*.tmp")) == []


def test_explicit_output_is_resolved_from_working_directory(tmp_path: Path, monkeypatch):
    project = tmp_path / "project"
    project.mkdir()
    source = write_project(project)
    monkeypatch.chdir(tmp_path)
    output = DocumentGenerator(load_project(source)).generate(Path("custom.docx"))
    assert output == tmp_path / "custom.docx"
