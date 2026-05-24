from __future__ import annotations

from vault_mcp.search import search_notes
from vault_mcp.vault import Vault


def test_search_substring_case_insensitive(vault: Vault) -> None:
    results = search_notes(vault, "agentic loop")
    paths = [r["path"] for r in results]
    assert "010-projects/alpha.md" in paths
    assert "060-hackathons/delta.md" in paths


def test_search_with_tech_filter(vault: Vault) -> None:
    results = search_notes(vault, "postgresql", tech=["postgresql"])
    paths = {r["path"] for r in results}
    assert "010-projects/alpha.md" in paths
    assert "010-projects/beta.md" in paths
    assert "010-projects/gamma.md" not in paths


def test_search_ranked_by_hit_count(vault: Vault) -> None:
    results = search_notes(vault, "postgresql")
    assert results
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_empty_query_returns_empty(vault: Vault) -> None:
    assert search_notes(vault, "") == []


def test_search_no_results(vault: Vault) -> None:
    assert search_notes(vault, "this-string-does-not-exist-anywhere") == []


def test_search_whitespace_matches_hyphen(vault: Vault) -> None:
    """Query 'agentic loop' should match 'agentic-loop' and 'agentic loops' too."""
    import frontmatter as fm
    from pathlib import Path

    target = Path(__file__).parent / "fixtures" / "010-projects" / "epsilon.md"
    target.write_text(
        "---\ntype: project\nstatus: active\ntech: [python]\ntags: [agentic-loop]\n---\n\n"
        "# Epsilon\n\nUses an agentic-loop pattern.\n",
        encoding="utf-8",
    )
    try:
        v = Vault(target.parent.parent)
        results = search_notes(v, "agentic loop")
        assert any(r["path"] == "010-projects/epsilon.md" for r in results)
    finally:
        target.unlink()


def test_search_snippet_contains_query(vault: Vault) -> None:
    results = search_notes(vault, "ETL")
    assert results
    assert "etl" in results[0]["snippet"].lower()
