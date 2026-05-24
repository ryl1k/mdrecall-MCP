from __future__ import annotations

from vault_mcp.backlinks import find_backlinks
from vault_mcp.frontmatter import query_frontmatter
from vault_mcp.vault import Vault


def test_query_status_active(vault: Vault) -> None:
    results = query_frontmatter(vault, {"status": "active"})
    paths = {r["path"] for r in results}
    assert paths == {
        "010-projects/alpha.md",
        "010-projects/zeta.md",
        "060-hackathons/delta.md",
    }


def test_query_tech_list_any_of(vault: Vault) -> None:
    results = query_frontmatter(vault, {"tech": ["postgresql"]})
    paths = {r["path"] for r in results}
    assert "010-projects/alpha.md" in paths
    assert "010-projects/beta.md" in paths
    assert "010-projects/gamma.md" not in paths


def test_query_combines_keys_with_and(vault: Vault) -> None:
    results = query_frontmatter(vault, {"status": "active", "tech": ["postgresql"]})
    paths = {r["path"] for r in results}
    assert paths == {"010-projects/alpha.md"}


def test_query_empty_filters_returns_all_notes(vault: Vault) -> None:
    results = query_frontmatter(vault, {})
    assert len(results) >= 6


def test_query_no_match(vault: Vault) -> None:
    results = query_frontmatter(vault, {"status": "nonexistent"})
    assert results == []


def test_query_limit(vault: Vault) -> None:
    results = query_frontmatter(vault, {}, limit=2)
    assert len(results) == 2


def test_backlinks_to_postgresql(vault: Vault) -> None:
    results = find_backlinks(vault, "070-concepts/tech/postgresql.md")
    paths = {r["path"] for r in results}
    assert paths == {
        "010-projects/alpha.md",
        "010-projects/beta.md",
        "010-projects/zeta.md",
    }


def test_backlinks_with_alias_form(vault: Vault) -> None:
    results = find_backlinks(vault, "070-concepts/tech/python.md")
    paths = {r["path"] for r in results}
    assert "010-projects/alpha.md" in paths


def test_backlinks_no_results(vault: Vault) -> None:
    assert find_backlinks(vault, "070-concepts/tech/nonexistent.md") == []


def test_backlinks_bare_basename(vault: Vault) -> None:
    results = find_backlinks(vault, "any/folder/gamma-helper.md")
    paths = {r["path"] for r in results}
    assert "010-projects/gamma.md" in paths


def test_backlinks_ignores_code_span_links(vault: Vault) -> None:
    """A wikilink inside backticks or a fenced block must not produce a backlink."""
    assert find_backlinks(vault, "any/folder/fake-inline.md") == []
    assert find_backlinks(vault, "any/folder/fake-fenced.md") == []


def test_backlinks_context_contains_link(vault: Vault) -> None:
    results = find_backlinks(vault, "070-concepts/tech/react.md")
    assert results
    assert "react" in results[0]["context"].lower()
