import json
from pathlib import Path

import pytest

from docgen.config.loader import (
    ConfigLoadError,
    load_project,
    resolve_project_output,
    resolve_project_path,
)


def write_json(path: Path, data) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_loader_resolves_external_content(tmp_path: Path):
    (tmp_path / "content").mkdir()
    write_json(
        tmp_path / "content/body.json",
        [{"type": "paragraph", "text": "External"}],
    )
    source = write_json(
        tmp_path / "document.json",
        {
            "kind": "document",
            "sections": [{"type": "content", "content_file": "content/body.json"}],
        },
    )
    loaded = load_project(source)
    section = loaded.config.sections[0]
    assert section.content[0].text == "External"
    assert section.content_file is None
    assert loaded.root == tmp_path.resolve()


def test_project_path_rejects_parent_traversal(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    (tmp_path / "secret.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ConfigLoadError, match="outside project root"):
        resolve_project_path(root, Path("../secret.json"))


def test_project_path_rejects_symlink_escape(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "data.json").write_text("{}", encoding="utf-8")
    (root / "link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ConfigLoadError, match="outside project root"):
        resolve_project_path(root, Path("link/data.json"))


def test_project_output_rejects_escape_without_requiring_file(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    assert resolve_project_output(root, Path("output/result.docx")) == root / "output/result.docx"
    with pytest.raises(ConfigLoadError, match="outside project root"):
        resolve_project_output(root, Path("../result.docx"))


def test_loader_resolves_image_to_absolute_path(tmp_path: Path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/image.png").write_bytes(b"image")
    source = write_json(
        tmp_path / "document.json",
        {
            "kind": "document",
            "resources": {
                "figures": [{"id": "image", "type": "image", "path": "assets/image.png"}]
            },
            "sections": [
                {"type": "content", "content": [{"type": "figure", "ref": "image"}]}
            ],
        },
    )
    loaded = load_project(source)
    assert loaded.config.resources.figures[0].path == (tmp_path / "assets/image.png").resolve()


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("{bad json", "invalid JSON"),
        (json.dumps({"kind": "unknown"}), "unsupported project kind"),
    ],
)
def test_loader_reports_malformed_root(tmp_path: Path, text: str, message: str):
    source = tmp_path / "config.json"
    source.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigLoadError, match=message):
        load_project(source)


def test_loader_reports_precise_validation_path(tmp_path: Path):
    source = write_json(
        tmp_path / "document.json",
        {"kind": "document", "sections": [{"type": "content"}]},
    )
    with pytest.raises(ConfigLoadError) as error:
        load_project(source)
    assert str(source) in str(error.value)
    assert "sections.0.content" in str(error.value)


def test_loader_rejects_unknown_citation(tmp_path: Path):
    source = write_json(
        tmp_path / "document.json",
        {
            "kind": "document",
            "sections": [
                {
                    "type": "content",
                    "content": [{"type": "paragraph", "text": "Claim {{cite:missing}}"}],
                }
            ],
        },
    )
    with pytest.raises(ConfigLoadError, match="unknown citation: missing"):
        load_project(source)


def test_external_content_graph_error_names_root_config(tmp_path: Path):
    (tmp_path / "body.json").write_text(
        json.dumps([{"type": "table", "ref": "missing"}]), encoding="utf-8"
    )
    source = write_json(
        tmp_path / "document.json",
        {
            "kind": "document",
            "sections": [{"type": "content", "content_file": "body.json"}],
        },
    )
    with pytest.raises(ConfigLoadError) as error:
        load_project(source)
    assert str(source) in str(error.value)
    assert "unknown table resource" in str(error.value)
