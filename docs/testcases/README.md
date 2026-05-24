# Test Cases

Manual validation matrix used to certify `mdrecall` against a real Obsidian
vault. Every tool was exercised across 10 use cases (1 for `list_folders`
since it takes no parameters) covering happy paths, filters, error paths,
and known edge cases.

Each file in this folder documents the cases for one tool. Format per case:

- **Input** — the exact call.
- **Expected** — observable outcome.
- **Validates** — what behavior the case proves.

| Tool | Cases | File |
|---|---:|---|
| `list_folders` | 1 | [list_folders.md](list_folders.md) |
| `list_notes` | 10 | [list_notes.md](list_notes.md) |
| `read_note` | 10 | [read_note.md](read_note.md) |
| `search_notes` | 10 | [search_notes.md](search_notes.md) |
| `query_frontmatter` | 10 | [query_frontmatter.md](query_frontmatter.md) |
| `find_backlinks` | 10 | [find_backlinks.md](find_backlinks.md) |

These cases supplement the 36 pytest unit tests under `tests/`. The pytest
suite covers determinism against a fixed fixture vault; this matrix covers
integration against the live 144-note knowledge vault and exercises
parameter combinations that fixture coverage alone misses.

To reproduce, point `VAULT_PATH` at a similarly-structured Obsidian vault
and replay any case through Claude Desktop, Claude Code, or a direct
stdio JSON-RPC client.
