# `read_note` — Test Cases

## Case 1 — Existing note with `.md`

- **Input**: `read_note(path="010-projects/chess.md")`
- **Expected**: `{path, frontmatter, body, wikilinks}` with parsed YAML
  frontmatter, full body, and resolved canonical wikilink targets.
- **Validates**: basic read path; frontmatter parsing; wikilink extraction.

## Case 2 — Existing note without `.md` suffix

- **Input**: `read_note(path="010-projects/chess")`
- **Expected**: same result as Case 1.
- **Validates**: optional `.md` suffix — natural-language paths from LLMs
  don't require the extension.

## Case 3 — Nonexistent note

- **Input**: `read_note(path="does-not-exist.md")`
- **Expected**: error `Note not found: does-not-exist.md`.
- **Validates**: missing-file errors are clear.

## Case 4 — Leading `./` prefix

- **Input**: `read_note(path="./010-projects/chess.md")`
- **Expected**: same as Case 1.
- **Validates**: relative-path prefixes resolve to canonical form.

## Case 5 — Mixed-case path (Windows)

- **Input**: `read_note(path="010-projects/CHESS.md")`
- **Expected**: returns chess.md; output `path` field is the canonical
  lowercase form.
- **Validates**: filesystem case-folding on Windows; canonical-path
  guarantee in the response.

## Case 6 — Backslash path separator

- **Input**: `read_note(path="010-projects\\chess.md")`
- **Expected**: same as Case 1.
- **Validates**: Windows-style paths normalize to forward slashes.

## Case 7 — Note with no frontmatter

- **Input**: `read_note(path="README.md")`
- **Expected**: `frontmatter: {}`, body returned, `wikilinks: []`.
- **Validates**: degrades gracefully when YAML block is absent.

## Case 8 — Concept note without `.md`

- **Input**: `read_note(path="070-concepts/tech/python")`
- **Expected**: returns python concept note with 18 unique wikilinks
  resolved.
- **Validates**: suffix-optional behavior on concept notes; wikilink
  extraction at scale (concept notes link extensively).

## Case 9 — Template note with placeholder values

- **Input**: `read_note(path="999-meta/templates/project-template.md")`
- **Expected**: returns note; `frontmatter` includes null-valued and
  list-with-null fields (e.g. `local-paths: [null]`) preserved as-is.
- **Validates**: malformed-but-valid YAML doesn't crash the parser;
  frontmatter is returned verbatim.

## Case 10 — Path inside excluded `_archive/`

- **Input**: `read_note(path="010-projects/_archive/old-thing.md")`
- **Expected**: error `Note not found`.
- **Validates**: `_`-prefixed folders are skipped consistently — both
  during enumeration and during direct path resolution.
