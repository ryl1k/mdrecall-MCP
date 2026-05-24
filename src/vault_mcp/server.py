"""MCP server entry point. Exposes six read-only tools over stdio."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .backlinks import find_backlinks as _find_backlinks
from .frontmatter import query_frontmatter as _query_frontmatter
from .search import search_notes as _search_notes
from .vault import Vault

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("vault_mcp")

DEFAULT_VAULT = Path(r"D:\Documents\Knowledge")

FOLDER_DESCRIPTIONS: dict[str, str] = {
    "000-index": "Entry points and Maps of Content.",
    "010-projects": "All code artifacts: personal, learning, forks, contributions, paused experiments.",
    "020-work": "Reserved for work / contract / client projects. Currently empty by design.",
    "030-ideas": "Thoughts not yet promoted to projects.",
    "040-learning": "Course notes, paper summaries, book takeaways.",
    "050-university": "University coursework (labs, courses, diploma).",
    "060-hackathons": "Hackathon projects, time-boxed.",
    "070-concepts": "Shared knowledge hubs and backlink targets (tech, ml, llm, patterns, hardware, web).",
    "080-decisions": "ADR-style decision records.",
    "090-daily": "Daily notes.",
    "100-inbox": "Temporary capture, awaiting routing.",
    "999-meta": "Vault metadata: spec, conventions, templates, logs.",
}


def _vault() -> Vault:
    raw = os.environ.get("VAULT_PATH")
    root = Path(raw) if raw else DEFAULT_VAULT
    return Vault(root)


_VAULT: Vault | None = None


def vault() -> Vault:
    global _VAULT
    if _VAULT is None:
        _VAULT = _vault()
        logger.info("Vault rooted at %s", _VAULT.root)
    return _VAULT


mcp = FastMCP("vault-mcp")


@mcp.tool()
def list_folders() -> list[dict[str, Any]]:
    """Return the top-level vault folders with note counts and descriptions."""

    v = vault()
    out: list[dict[str, Any]] = []
    for folder in v.top_level_folders():
        name = folder.name
        out.append(
            {
                "name": name,
                "path": name,
                "description": FOLDER_DESCRIPTIONS.get(name, ""),
                "note_count": v.count_notes(folder),
            }
        )
    return out


@mcp.tool()
def list_notes(folder: str, recursive: bool = False) -> list[dict[str, Any]]:
    """Enumerate notes in a vault folder. Returns frontmatter summaries, not bodies."""

    v = vault()
    notes = v.iter_notes(folder=folder, recursive=recursive)
    return [n.summary() for n in notes]


@mcp.tool()
def read_note(path: str) -> dict[str, Any]:
    """Read a single note. Returns frontmatter, body, and resolved wikilink targets.

    Accepts paths with or without the `.md` suffix.
    """

    v = vault()
    note = v.get_note(path)
    seen: set[str] = set()
    unique_targets: list[str] = []
    for target in note.wikilink_targets():
        if target not in seen:
            seen.add(target)
            unique_targets.append(target)
    return {
        "path": note.path,
        "frontmatter": note.frontmatter,
        "body": note.body,
        "wikilinks": unique_targets,
    }


@mcp.tool()
def search_notes(
    query: str,
    types: list[str] | None = None,
    status: list[str] | None = None,
    tech: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Case-insensitive full-text search across body + frontmatter values.

    Optional filters narrow candidates before searching. Results are ranked by
    hit count (descending) and include a ~200-char context snippet.
    """

    return _search_notes(vault(), query, types=types, status=status, tech=tech, limit=limit)


@mcp.tool()
def query_frontmatter(
    filters: dict[str, Any],
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Filter notes by frontmatter fields.

    Multiple keys combine with AND. A list value for a key is any-of (e.g.
    `{"tech": ["postgresql"]}` matches notes whose `tech` array contains
    `postgresql`). A `null` value matches notes where the field is null or
    absent (e.g. `{"github": null}` finds notes with no github remote).
    """

    return _query_frontmatter(vault(), filters, limit=limit)


@mcp.tool()
def find_backlinks(path: str) -> list[dict[str, Any]]:
    """Find notes that link to `path` via wikilink. Returns context around each link."""

    return _find_backlinks(vault(), path)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
