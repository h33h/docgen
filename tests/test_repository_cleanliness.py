from pathlib import Path
import tomllib


PUBLIC_DESCRIPTION = (
    "Generate structured DOCX documents and PPTX presentations "
    "from validated JSON configurations."
)


def test_internal_planning_artifacts_are_absent():
    assert not Path("docs").exists()


def test_product_description_is_specific():
    metadata = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert metadata["project"]["description"] == PUBLIC_DESCRIPTION
    assert PUBLIC_DESCRIPTION in Path("README.md").read_text(encoding="utf-8")
