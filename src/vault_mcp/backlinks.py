"""Reverse wikilink lookup."""

from __future__ import annotations

import re
from typing import Any

from .vault import WIKILINK_RE, Vault, canonical_path


def _snippet_around(body: str, start: int, end: int, width: int = 200) -> str:
    half = width // 2
    s = max(0, start - half)
    e = min(len(body), end + half)
    text = body[s:e].replace("\n", " ").strip()
    prefix = "…" if s > 0 else ""
    suffix = "…" if e < len(body) else ""
    return f"{prefix}{text}{suffix}"


def find_backlinks(vault: Vault, path: str) -> list[dict[str, Any]]:
    """Notes that wikilink to `path` (vault-relative).

    Matches by canonicalized target: case-insensitive, `.md` stripped, forward
    slashes. Bare-basename wikilinks (no folder) also match when the basename
    is the same.
    """

    target = canonical_path(path)
    target_basename = target.rsplit("/", 1)[-1]
    results: list[dict[str, Any]] = []

    for note in vault.iter_notes():
        if note.path == path:
            continue
        hits: list[re.Match[str]] = []
        for match in WIKILINK_RE.finditer(note.body):
            link_target = match.group(1)
            canonical = canonical_path(link_target)
            if canonical == target:
                hits.append(match)
            elif "/" not in canonical and canonical == target_basename:
                hits.append(match)
        if not hits:
            continue
        first = hits[0]
        results.append(
            {
                "path": note.path,
                "title": note.title,
                "context": _snippet_around(note.body, first.start(), first.end()),
            }
        )
    results.sort(key=lambda r: str(r["path"]))
    return results
