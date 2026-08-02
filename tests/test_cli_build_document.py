import json
from pathlib import Path

from docx import Document

from docgen.cli import main


def test_cli_builds_document(tmp_path: Path, capsys):
    source = tmp_path / "document.json"
    source.write_text(
        json.dumps(
            {
                "kind": "document",
                "sections": [
                    {
                        "type": "content",
                        "content": [{"type": "paragraph", "text": "CLI output"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "custom.docx"
    assert main(["build", str(source), "-o", str(output)]) == 0
    assert "CLI output" in [paragraph.text for paragraph in Document(output).paragraphs]
    assert str(output) in capsys.readouterr().out


def test_cli_reports_invalid_document(tmp_path: Path, capsys):
    source = tmp_path / "document.json"
    source.write_text('{"kind":"document","sections":[]}', encoding="utf-8")
    assert main(["build", str(source)]) == 1
    assert "sections" in capsys.readouterr().err


def test_cli_reports_generation_failure(tmp_path: Path, capsys, monkeypatch):
    source = tmp_path / "document.json"
    source.write_text(
        '{"kind":"document","sections":[{"type":"content",'
        '"content":[{"type":"paragraph","text":"Hello"}]}]}',
        encoding="utf-8",
    )

    def fail_generation(*_args, **_kwargs):
        raise RuntimeError("renderer failed")

    monkeypatch.setattr("docgen.cli.DocumentGenerator.generate", fail_generation)

    assert main(["build", str(source)]) == 1
    assert "docgen: error: renderer failed" in capsys.readouterr().err
