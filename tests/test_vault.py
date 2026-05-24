from __future__ import annotations

from pathlib import Path

import pytest

from vault_mcp.vault import Vault, canonical_path


def test_iter_notes_recursive_skips_archive(vault: Vault) -> None:
    paths = {n.path for n in vault.iter_notes()}
    assert "010-projects/alpha.md" in paths
    assert "010-projects/beta.md" in paths
    assert "070-concepts/tech/react.md" in paths
    assert not any(p.startswith("010-projects/_archive") for p in paths)


def test_iter_notes_non_recursive(vault: Vault) -> None:
    paths = {n.path for n in vault.iter_notes("010-projects", recursive=False)}
    assert paths == {
        "010-projects/alpha.md",
        "010-projects/beta.md",
        "010-projects/gamma.md",
        "010-projects/zeta.md",
    }


def test_get_note_parses_frontmatter_and_title(vault: Vault) -> None:
    note = vault.get_note("010-projects/alpha.md")
    assert note.title == "Alpha Service"
    assert note.status == "active"
    assert note.tech == ["python", "postgresql", "fastapi"]
    assert "Alpha Service" not in note.frontmatter
    assert "Backend API" in note.body


def test_cache_returns_same_object_until_mtime_changes(vault: Vault, fixture_root: Path) -> None:
    note1 = vault.get_note("010-projects/alpha.md")
    note2 = vault.get_note("010-projects/alpha.md")
    assert note1 is note2

    target = fixture_root / "010-projects" / "alpha.md"
    new_mtime = note1.mtime + 5
    import os
    os.utime(target, (new_mtime, new_mtime))
    note3 = vault.get_note("010-projects/alpha.md")
    assert note3 is not note1
    assert note3.title == note1.title
    assert note3.mtime == new_mtime


def test_get_note_missing_raises(vault: Vault) -> None:
    with pytest.raises(FileNotFoundError):
        vault.get_note("does/not/exist.md")


def test_path_escape_rejected(vault: Vault) -> None:
    with pytest.raises(ValueError):
        vault.get_note("../outside.md")


def test_canonical_path() -> None:
    assert canonical_path("070-concepts/tech/React.md") == "070-concepts/tech/react"
    assert canonical_path("070-concepts/tech/react") == "070-concepts/tech/react"
    assert canonical_path("070-Concepts\\Tech\\React") == "070-concepts/tech/react"


def test_count_notes_skips_underscored_dirs(vault: Vault, fixture_root: Path) -> None:
    count = vault.count_notes(fixture_root / "010-projects")
    assert count == 4


def test_wikilink_extraction_skips_code_spans(vault: Vault) -> None:
    note = vault.get_note("010-projects/zeta.md")
    targets = note.wikilink_targets()
    assert "070-concepts/tech/python" in targets
    assert "070-concepts/tech/postgresql" in targets
    assert "fake-inline" not in targets
    assert "fake-fenced" not in targets
    assert "also-fake" not in targets
