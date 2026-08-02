from pathlib import Path

import pytest
from pydantic import TypeAdapter

from docgen.config.document import FigureResource
from docgen.diagrams import DiagramRegistry
from docgen.diagrams.layout import apply_layout


@pytest.mark.parametrize("kind", ["bar", "horizontal_bar", "pie"])
def test_simple_diagram_creates_png(tmp_path: Path, kind: str):
    resource = TypeAdapter(FigureResource).validate_python(
        {
            "id": f"{kind}-1",
            "type": kind,
            "labels": ["A", "B"],
            "values": [1, 2],
            "title": "Chart",
        }
    )
    output = DiagramRegistry.render(resource, tmp_path)
    assert output == tmp_path / f"{kind}-1.png"
    assert output.stat().st_size > 0


def test_diagram_registry_rejects_image_resources(tmp_path: Path):
    image = tmp_path / "source.png"
    image.write_bytes(b"not rendered")
    resource = TypeAdapter(FigureResource).validate_python(
        {"id": "image", "type": "image", "path": str(image)}
    )
    with pytest.raises(ValueError, match="unsupported diagram type"):
        DiagramRegistry.render(resource, tmp_path)


def test_structure_tree_layout_is_deterministic_and_renderable(tmp_path: Path):
    raw = {
        "id": "structure-1",
        "type": "structure",
        "nodes": [
            {"id": "root", "label": "Root"},
            {"id": "left", "label": "Left"},
            {"id": "right", "label": "Right"},
        ],
        "connections": [
            {"from": "root", "to": "left"},
            {"from": "root", "to": "right"},
        ],
        "options": {"layout": "tree"},
    }
    resource = TypeAdapter(FigureResource).validate_python(raw)
    nodes = [node.model_dump() for node in resource.nodes]
    connections = [connection.model_dump(by_alias=True) for connection in resource.connections]
    first = apply_layout(nodes, connections, resource.options)
    second = apply_layout(nodes, connections, resource.options)
    assert first == second
    assert all(node["x"] is not None and node["y"] is not None for node in first)
    output = DiagramRegistry.render(resource, tmp_path)
    assert output.stat().st_size > 0


def test_manual_structure_layout_requires_coordinates():
    with pytest.raises(Exception, match="manual structure layout requires x and y"):
        TypeAdapter(FigureResource).validate_python(
            {
                "id": "structure-1",
                "type": "structure",
                "nodes": [{"id": "root", "label": "Root"}],
                "options": {"layout": "manual"},
            }
        )
