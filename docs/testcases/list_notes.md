# `list_notes` — Test Cases

## Case 1 — Existing folder, non-recursive

- **Input**: `list_notes(folder="010-projects", recursive=False)`
- **Expected**: 54 notes; each summary includes `path`, `title`, `type`,
  `status`, `tech`, `tags`.
- **Validates**: basic folder enumeration; count matches
  `list_folders.note_count` for the same folder.

## Case 2 — Existing folder, recursive

- **Input**: `list_notes(folder="070-concepts", recursive=True)`
- **Expected**: 74 notes spanning `hardware/`, `llm/`, `ml/`, `patterns/`,
  `tech/`, `web/` subfolders.
- **Validates**: recursive traversal across multiple subdirectories.

## Case 3 — Leaf subfolder

- **Input**: `list_notes(folder="070-concepts/web", recursive=False)`
- **Expected**: 2 notes (`jwt.md`, `oauth.md`).
- **Validates**: deep paths resolve correctly.

## Case 4 — Empty folder

- **Input**: `list_notes(folder="020-work", recursive=False)`
- **Expected**: `[]`.
- **Validates**: empty folders return empty list, not an error.

## Case 5 — Nonexistent folder

- **Input**: `list_notes(folder="090-daily/2026/05", recursive=False)`
- **Expected**: error `Folder not found: 090-daily/2026/05`.
- **Validates**: clear, actionable error for missing paths.

## Case 6 — Excluded `_archive` folder

- **Input**: `list_notes(folder="010-projects/_archive", recursive=True)`
- **Expected**: `[]`.
- **Validates**: folders starting with `_` (or `.`) are skipped even when
  explicitly requested.

## Case 7 — Trailing slash on folder

- **Input**: `list_notes(folder="070-concepts/tech/", recursive=False)`
- **Expected**: 47 tech concept notes (same as without trailing slash).
- **Validates**: trailing separator tolerated.

## Case 8 — Case-different folder (Windows)

- **Input**: `list_notes(folder="050-University", recursive=True)`
- **Expected**: 5 university notes resolve via Windows case-insensitive FS.
- **Validates**: path normalization on case-insensitive filesystems.

## Case 9 — Vault root, non-recursive

- **Input**: `list_notes(folder=".", recursive=False)`
- **Expected**: root-level `README.md` only.
- **Validates**: vault-root listing without descending into subfolders.

## Case 10 — Meta folder with nested templates

- **Input**: `list_notes(folder="999-meta", recursive=True)`
- **Expected**: 8 notes including `templates/concept-template.md` and
  `templates/project-template.md`.
- **Validates**: recursive traversal includes nested template directory.
