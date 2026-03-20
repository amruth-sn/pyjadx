from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def hello_dex() -> Path:
    return FIXTURES_DIR / "hello.dex"


@pytest.fixture
def multi_dex() -> Path:
    return FIXTURES_DIR / "multi.dex"
