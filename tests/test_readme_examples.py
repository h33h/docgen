import json
from pathlib import Path

from docgen.cli import main


def test_document_readme_example_builds(tmp_path: Path):
    project = tmp_path / "document"
    project.mkdir()
    config = {
        "kind": "document",
        "output": "result.docx",
        "sections": [
            {
                "type": "content",
                "title": "Overview",
                "content": [{"type": "paragraph", "text": "Hello."}],
            }
        ],
    }
    source = project / "document.json"
    source.write_text(json.dumps(config), encoding="utf-8")
    assert main(["build", str(source)]) == 0
    assert (project / "result.docx").stat().st_size > 0


def test_presentation_readme_example_builds(tmp_path: Path):
    project = tmp_path / "slides"
    project.mkdir()
    config = {
        "kind": "presentation",
        "title": "Demo",
        "slides": [
            {"type": "title"},
            {"type": "text", "title": "One", "text": "Hello."},
        ],
    }
    source = project / "presentation.json"
    source.write_text(json.dumps(config), encoding="utf-8")
    assert main(["build", str(source)]) == 0
    assert (project / "presentation.pptx").stat().st_size > 0
