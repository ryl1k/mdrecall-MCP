from __future__ import annotations

from pathlib import Path

import pytest

from vault_mcp.vault import Vault


@pytest.fixture
def fixture_root() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def vault(fixture_root: Path) -> Vault:
    return Vault(fixture_root)
