"""Full-text search across notes with optional frontmatter filters."""

from __future__ import annotations

import re
from typing import Any

from .frontmatter import matches_filters
from .vault import Note, Vault


def _snippet(body: str, match_start: int, match_end: int, width: int = 200) -> str:
    half = width // 2
    start = max(0, match_start - half)
    end = min(len(body), match_end + half)
    text = body[start:end].replace("\n", " ").strip()
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(body) else ""
    return f"{prefix}{text}{suffix}"


def _frontmatter_haystack(note: Note) -> str:
    parts: list[str] = []
    for value in note.frontmatter.values():
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value is not None:
            parts.append(str(value))
    return "\n".join(parts)


def search_notes(
    vault: Vault,
    query: str,
    types: list[str] | None = None,
    status: list[str] | None = None,
    tech: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Case-insensitive substring search over body + frontmatter values.

    Filters: `types`, `status`, `tech` restrict candidates before searching.
    `score` is the total hit count across body + frontmatter (descending).
    """

    if not query:
        return []

    filters: dict[str, Any] = {}
    if types:
        filters["type"] = list(types)
    if status:
        filters["status"] = list(status)
    if tech:
        filters["tech"] = list(tech)

    tokens = [re.escape(t) for t in query.split() if t]
    if not tokens:
        return []
    pattern = re.compile(r"[\s\-]+".join(tokens), re.IGNORECASE)
    results: list[dict[str, Any]] = []

    for note in vault.iter_notes():
        if filters and not matches_filters(note, filters):
            continue
        body_matches = list(pattern.finditer(note.body))
        fm_haystack = _frontmatter_haystack(note)
        fm_matches = list(pattern.finditer(fm_haystack))
        score = len(body_matches) + len(fm_matches)
        if score == 0:
            continue
        if body_matches:
            first = body_matches[0]
            snippet = _snippet(note.body, first.start(), first.end())
        else:
            first = fm_matches[0]
            snippet = _snippet(fm_haystack, first.start(), first.end())
        results.append(
            {
                "path": note.path,
                "title": note.title,
                "snippet": snippet,
                "score": score,
            }
        )

    results.sort(key=lambda r: (-int(r["score"]), str(r["path"])))
    return results[:limit]
