"""Atomic output persistence shared by DOCX and PPTX generators."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable


def atomic_save(save_callable: Callable[[str], None], target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(
            prefix=".docgen-",
            suffix=target.suffix,
            dir=target.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        save_callable(str(temporary_path))
        os.replace(temporary_path, target)
        temporary_path = None
        return target
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
