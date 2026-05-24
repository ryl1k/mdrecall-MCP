# `query_frontmatter` — Test Cases

## Case 1 — Single scalar filter

- **Input**: `query_frontmatter(filters={"status": "active"}, limit=100)`
- **Expected**: 13 results spanning projects and active coursework.
- **Validates**: scalar match against a list-typed expected value is not
  required; AND across one key works.

## Case 2 — Multi-key AND

- **Input**: `query_frontmatter(filters={"type": "project", "role": "contributor"}, limit=10)`
- **Expected**: 4 contributor projects.
- **Validates**: multiple filters combine with AND.

## Case 3 — List any-of

- **Input**: `query_frontmatter(filters={"tech": ["python", "go"]}, limit=3)`
- **Expected**: notes whose `tech` array contains `python` OR `go`.
- **Validates**: list filter is any-of, not all-of.

## Case 4 — `null` matches absent or null field

- **Input**: `query_frontmatter(filters={"github": null, "type": "project"}, limit=3)`
- **Expected**: projects with `github: null` or no `github` key at all.
- **Validates**: `null` sentinel matches both null-valued and absent
  fields; closes the "find notes without a github remote" use case.

## Case 5 — Date filter via ISO string

- **Input**: `query_frontmatter(filters={"started": "2026-05-24"}, limit=3)`
- **Expected**: `010-projects/vault-mcp.md` (the only note started that
  day).
- **Validates**: YAML-parsed `datetime.date` values match the ISO string
  form of the filter — no type mismatch.

## Case 6 — Case-insensitive scalar match

- **Input**: `query_frontmatter(filters={"status": "PaUsEd"}, limit=3)`
- **Expected**: paused notes returned (3 in limit).
- **Validates**: strings are case-folded on both sides before comparison.

## Case 7 — Filter on concept-only fields

- **Input**: `query_frontmatter(filters={"maturity": "stable", "subpath": "tech"}, limit=3)`
- **Expected**: 3 tech concept notes with `maturity: stable`.
- **Validates**: schema-agnostic — works on any frontmatter keys, not
  just the project schema.

## Case 8 — No-match filter value

- **Input**: `query_frontmatter(filters={"type": "nonexistent-type"}, limit=3)`
- **Expected**: `[]`.
- **Validates**: filter on absent value class returns empty cleanly.

## Case 9 — Filter on list field with single string

- **Input**: `query_frontmatter(filters={"local-paths": "A:/050-labs/auto-labs"}, limit=3)`
- **Expected**: `010-projects/auto-labs.md`.
- **Validates**: scalar filter against a list note-value matches when the
  scalar appears in the list.

## Case 10 — Four-key combined filter

- **Input**: `query_frontmatter(filters={"type": "project", "status": "active", "tech": "python", "github": null}, limit=10)`
- **Expected**: 6 active python projects with no github remote.
- **Validates**: complex multi-key queries combining scalar, list, and
  null filters all interact correctly.
