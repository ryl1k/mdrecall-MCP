"""Structured queries over note frontmatter."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .vault import Note, Vault


def _normalize(value: Any) -> Any:
    """Normalize a frontmatter value for comparison.

    * Strings are case-folded so filters are case-insensitive (matches
      `search_notes` behavior).
    * `date` / `datetime` become their ISO string form so callers can pass
      a literal like `"2026-05-10"` and have it match the parsed YAML date.
    * Lists recurse element-wise.
    """

    if isinstance(value, str):
        return value.casefold()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def _matches_one(note_value: Any, filter_value: Any) -> bool:
    """Match semantics:

    * If the note value is a list: filter value matches if it intersects (any-of).
      A list filter against a list note also matches if any element overlaps.
    * If the note value is a scalar: exact match (case-insensitive for strings,
      ISO-string for dates). A list filter against a scalar matches if the
      scalar is in the filter list (any-of).
    """

    nv = _normalize(note_value)
    fv = _normalize(filter_value)
    if isinstance(nv, list):
        if isinstance(fv, list):
            return any(item in nv for item in fv)
        return bool(fv in nv)
    if isinstance(fv, list):
        return bool(nv in fv)
    return bool(nv == fv)


def matches_filters(note: Note, filters: dict[str, Any]) -> bool:
    """Returns True iff every (key, value) in `filters` matches the note.

    A filter value of `None` matches notes where the field is null or absent.
    """

    for key, expected in filters.items():
        actual = note.frontmatter.get(key)
        if expected is None:
            if actual is not None:
                return False
            continue
        if actual is None:
            return False
        if not _matches_one(actual, expected):
            return False
    return True


def query_frontmatter(
    vault: Vault,
    filters: dict[str, Any],
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return notes whose frontmatter satisfies all filters.

    Multiple keys combine with AND; list values within one key are any-of.
    A `None` value matches notes where the field is null or absent (e.g.
    `{"github": None}` finds notes without a github remote).
    """

    matched: list[dict[str, Any]] = []
    for note in vault.iter_notes():
        if matches_filters(note, filters):
            matched.append(
                {
                    "path": note.path,
                    "title": note.title,
                    "frontmatter": note.frontmatter,
                }
            )
            if len(matched) >= limit:
                break
    return matched
