import json
from pathlib import Path
import subprocess
import sys

from docgen.cli import main


def test_init_document_creates_valid_config(tmp_path: Path):
    target = tmp_path / "project"
    assert main(["init", str(target)]) == 0
    data = json.loads((target / "document.json").read_text(encoding="utf-8"))
    assert data["kind"] == "document"
    assert data["sections"][0]["type"] == "content"
    assert (target / "content").is_dir()
    assert (target / "assets").is_dir()


def test_init_presentation_creates_valid_config(tmp_path: Path):
    target = tmp_path / "slides"
    assert main(["init", str(target), "--kind", "presentation"]) == 0
    data = json.loads((target / "presentation.json").read_text(encoding="utf-8"))
    assert data["kind"] == "presentation"
    assert [slide["type"] for slide in data["slides"]] == ["title", "text"]
    assert (target / "assets").is_dir()


def test_init_refuses_non_empty_directory(tmp_path: Path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    marker = target / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    assert main(["init", str(target)]) == 1
    assert marker.read_text(encoding="utf-8") == "keep"
    assert "not empty" in capsys.readouterr().err


def test_module_help_and_version_are_available():
    help_result = subprocess.run(
        [sys.executable, "-m", "docgen", "--help"], capture_output=True, text=True
    )
    version_result = subprocess.run(
        [sys.executable, "-m", "docgen", "--version"], capture_output=True, text=True
    )
    assert help_result.returncode == 0
    assert "init" in help_result.stdout
    assert version_result.returncode == 0
    assert "0.1.0" in version_result.stdout
