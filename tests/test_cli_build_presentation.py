from pathlib import Path

from pptx import Presentation

from docgen.cli import main


def test_cli_initializes_and_builds_presentation(tmp_path: Path):
    project = tmp_path / "slides"
    assert main(["init", str(project), "--kind", "presentation"]) == 0
    output = tmp_path / "result.pptx"
    assert main(
        ["build", str(project / "presentation.json"), "-o", str(output)]
    ) == 0
    presentation = Presentation(output)
    assert len(presentation.slides) == 2


def test_cli_rejects_wrong_presentation_output_suffix(tmp_path: Path, capsys):
    project = tmp_path / "slides"
    assert main(["init", str(project), "--kind", "presentation"]) == 0
    assert main(
        ["build", str(project / "presentation.json"), "-o", str(tmp_path / "wrong.docx")]
    ) == 1
    assert "pptx" in capsys.readouterr().err
