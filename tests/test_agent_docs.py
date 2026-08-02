from pathlib import Path


def test_agent_guide_covers_operational_context():
    text = Path("AGENTS.md").read_text(encoding="utf-8")
    required = [
        "docgen init",
        "docgen build",
        "python -m pytest",
        "DocumentGenerator",
        "PresentationGenerator",
        "SectionRendererRegistry",
        "BlockRendererRegistry",
        "Pydantic",
        "content_file",
        "{{cite:id}}",
    ]
    assert all(term in text for term in required)


def test_no_nested_agent_guides():
    guides = [path for path in Path(".").rglob("AGENTS.md") if path != Path("AGENTS.md")]
    assert guides == []
