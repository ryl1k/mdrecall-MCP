# `find_backlinks` — Test Cases

## Case 1 — Heavy hub concept

- **Input**: `find_backlinks(path="070-concepts/tech/postgresql.md")`
- **Expected**: 18 backlinks (projects + sibling concepts).
- **Validates**: reverse wikilink lookup at scale; context snippet
  included for every hit.

## Case 2 — Small hub concept

- **Input**: `find_backlinks(path="070-concepts/hardware/sdr.md")`
- **Expected**: 3 backlinks (one project, two related hardware concepts).
- **Validates**: correct enumeration when the backlink set is small.

## Case 3 — Uppercase path with `.md`

- **Input**: `find_backlinks(path="070-concepts/llm/MCP.md")`
- **Expected**: 6 results identical to lowercase invocation.
- **Validates**: target path is canonicalized (case-folded) before
  comparison.

## Case 4 — Path without `.md` suffix

- **Input**: `find_backlinks(path="070-concepts/llm/mcp")`
- **Expected**: same 6 results as Case 3.
- **Validates**: `.md` suffix is optional on the target path.

## Case 5 — Leading slash on path

- **Input**: `find_backlinks(path="/070-concepts/tech/python.md")`
- **Expected**: 19 backlinks (heavy hub).
- **Validates**: leading slashes are stripped during canonicalization.

## Case 6 — Nonexistent target

- **Input**: `find_backlinks(path="070-concepts/never-existed.md")`
- **Expected**: `[]`.
- **Validates**: returns empty rather than erroring — usable for "does
  anything point at this future note?" checks before creating it.

## Case 7 — Backlinks to a project (not a concept)

- **Input**: `find_backlinks(path="010-projects/chess.md")`
- **Expected**: 7 backlinks (other projects + concept "used in this
  vault" sections).
- **Validates**: works on any note path, not just concepts; the queried
  note is excluded from its own backlinks.

## Case 8 — Wrong folder with matching basename

- **Input**: `find_backlinks(path="unknown/folder/agentic-loops.md")`
- **Expected**: `[]`.
- **Validates**: full-path match required when both target and link have
  folders; bare-basename matching only activates when the actual link
  is itself bare (`[[agentic-loops]]`).

## Case 9 — `web/jwt` no `.md`

- **Input**: `find_backlinks(path="070-concepts/web/jwt")`
- **Expected**: 10 backlinks across projects and sibling concepts.
- **Validates**: deeper-path canonicalization without `.md`.

## Case 10 — Backslash separator

- **Input**: `find_backlinks(path="070-concepts\\tech\\react.md")`
- **Expected**: 16 backlinks (same as forward-slash form).
- **Validates**: Windows-style path separators are normalized before
  comparison.
