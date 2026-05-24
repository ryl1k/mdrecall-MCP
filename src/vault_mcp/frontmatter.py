"""Structured queries over note frontmatter."""

from __future__ import annotations

from typing import Any

from .vault import Note, Vault


def _matches_one(note_value: Any, filter_value: Any) -> bool:
    """Match semantics:

    * If the note value is a list: filter value matches if it intersects (any-of).
      A list filter against a list note also matches if any element overlaps.
    * If the note value is a scalar: exact match. A list filter against a scalar
      matches if the scalar is in the filter list (any-of).
    """

    if isinstance(note_value, list):
        if isinstance(filter_value, list):
            return any(item in note_value for item in filter_value)
        return filter_value in note_value
    if isinstance(filter_value, list):
        return note_value in filter_value
    return note_value == filter_value


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
