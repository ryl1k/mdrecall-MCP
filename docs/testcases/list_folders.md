# `list_folders` — Test Cases

`list_folders` takes no parameters; one meaningful invocation exists.

## Case 1 — Enumerate top-level vault folders

- **Input**: `list_folders()`
- **Expected**: array of `{name, path, description, note_count}` for every
  non-hidden top-level directory; counts equal the recursive note count
  for each folder; descriptions come from a built-in mapping.
- **Validates**: folder discovery, count consistency with `list_notes`,
  exclusion of hidden / underscore-prefixed folders, deterministic output.
