from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import shutil
from uuid import uuid4

import pytest


@pytest.fixture
def local_tmp_path() -> Iterator[Path]:
    root = Path("tmp") / "test-runs"
    path = root / uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        resolved = path.resolve()
        allowed_root = root.resolve()
        if allowed_root in resolved.parents:
            shutil.rmtree(resolved, ignore_errors=True)
