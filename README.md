# mdrecall

[![CI](https://github.com/ryl1k/mdrecall/actions/workflows/ci.yml/badge.svg)](https://github.com/ryl1k/mdrecall/actions/workflows/ci.yml)

Local MCP server that exposes a folder of markdown notes (e.g. an Obsidian
vault) to Claude Desktop and Claude Code as a queryable memory layer.
Read-only, stdio transport, no network calls.

Six tools: `list_folders`, `list_notes`, `read_note`, `search_notes`,
`query_frontmatter`, `find_backlinks`.

## Requirements

- Python 3.11+
- A directory of markdown files. YAML frontmatter and Obsidian-style
  wikilinks (`[[target]]`, `[[target|alias]]`) are supported but not required.

## Install

```bash
git clone https://github.com/ryl1k/mdrecall.git
cd mdrecall
pip install -e .
```

This registers an `mdrecall` console script that starts the stdio server.

## Configuration

Point the server at your notes via the `VAULT_PATH` environment variable.
If unset, it falls back to `~/Documents/Knowledge`.

The MCP works with any markdown corpus. `query_frontmatter` and the
`search_notes` filters (`types`, `status`, `tech`) become most useful when
notes carry structured frontmatter — the schema this project was designed
around looks like:

```yaml
---
type: project           # project | concept | index | …
status: active          # active | paused | archived | done
role: author            # author | contributor | reader | fork
started: 2026-05-24
ended: null
tech: [python, mcp]
tags: [tooling, knowledge-management]
github: https://github.com/...
local-paths:
  - /path/on/disk
---
```

Any subset of these fields works; `query_frontmatter` is generic and filters
on whatever keys you put in.

## Wiring into Claude Desktop

Edit your config file (create it if missing):

| OS      | Path                                                              |
|---------|-------------------------------------------------------------------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json`                     |
| macOS   | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux   | `~/.config/Claude/claude_desktop_config.json`                     |

Add the server. On Windows the backslashes in `VAULT_PATH` must be doubled
inside the JSON string:

```json
{
  "mcpServers": {
    "mdrecall": {
      "command": "mdrecall",
      "env": { "VAULT_PATH": "D:\\Documents\\Knowledge" }
    }
  }
}
```

macOS / Linux:

```json
{
  "mcpServers": {
    "mdrecall": {
      "command": "mdrecall",
      "env": { "VAULT_PATH": "/Users/you/Documents/Knowledge" }
    }
  }
}
```

If Claude Desktop can't find `mdrecall` on PATH, point it at Python directly:

```json
{
  "mcpServers": {
    "mdrecall": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "mdrecall.server"],
      "env": { "VAULT_PATH": "/path/to/vault" }
    }
  }
}
```

Restart Claude Desktop after editing.

## Wiring into Claude Code

```bash
claude mcp add mdrecall mdrecall -e VAULT_PATH=/path/to/your/vault
```

Quote the path if it contains spaces or special characters. Start a new
Claude Code session — MCP servers load at startup.

## Tools

### `list_folders`
Top-level folders with note counts and short descriptions.

```
list_folders()
→ [{"name": "010-projects", "path": "010-projects", "description": "...", "note_count": 54}, ...]
```

### `list_notes(folder, recursive=false)`
Frontmatter summaries for notes in a folder.

```
list_notes(folder="070-concepts/tech", recursive=false)
→ [{"path": "070-concepts/tech/react.md", "title": "React", "type": "concept", "status": null, "tech": [], "tags": [...]}, ...]
```

### `read_note(path)`
Full content of one note. The `.md` suffix is optional.

```
read_note(path="010-projects/chess")
→ {"path": "...", "frontmatter": {...}, "body": "...", "wikilinks": ["070-concepts/tech/pytorch", ...]}
```

### `search_notes(query, types?, status?, tech?, limit=20)`
Case-insensitive search across body + frontmatter values. Whitespace and
hyphens in the query are interchangeable (`agentic loop` matches `agentic-loop`
and `agentic loops`). Optional filters narrow candidates first. Results ranked
by hit count.

```
search_notes(query="agentic loop")
search_notes(query="auth", types=["project"], status=["active"])
```

### `query_frontmatter(filters, limit=50)`
Structured filter on frontmatter only. Multiple keys combine with AND. A list
value for one key is any-of. A `null` value matches notes where the field is
null *or* absent.

```
query_frontmatter(filters={"status": "active"})
query_frontmatter(filters={"tech": ["postgresql"]})
query_frontmatter(filters={"status": "active", "tech": ["python"]})
query_frontmatter(filters={"status": "active", "github": null})  # actives with no remote
```

### `find_backlinks(path)`
Notes that wikilink to a given note. Matches `[[070-concepts/tech/react]]`,
`[[070-concepts/tech/react.md]]`, and `[[react|React]]`. Bare-basename links
also match. The `.md` suffix on `path` is optional.

```
find_backlinks(path="070-concepts/tech/react")
→ [{"path": "010-projects/traceflow.md", "title": "...", "context": "..."}, ...]
```

## Conventions

- Vault-relative paths use forward slashes. The `.md` suffix is optional for
  `read_note` and `find_backlinks`.
- Folders starting with `.` or `_` (e.g. `_archive/`) are excluded from
  listings, searches, and backlinks.
- Wikilink resolution is case-insensitive and treats `.md` as optional.
- Notes are parsed once and cached in memory; the cache invalidates per file
  when the file's mtime changes.

## Semantics worth knowing

These are quiet behaviors that surprised the author during dogfooding. None
are bugs; calling them out so they don't bite:

- **`search_notes` is literal substring, not regex.** The query is escaped and
  ranked by hit count. Whitespace and hyphens in the query are treated as one
  separator class (`agentic loop` matches `agentic-loop` and `agentic loops`).
  Regex metacharacters in the query match literally.
- **`query_frontmatter` empty list = no filter.** A falsy value (`[]`, `""`,
  `null` *in the `search_notes` filter args*) is ignored, not "match nothing".
  Use a missing key when you mean "don't filter". Use explicit `null` in
  `query_frontmatter` filters to mean "field must be null or absent".
- **Path case-sensitivity follows the OS.** On Windows the filesystem is
  case-insensitive, so `Chess.md` resolves to `chess.md`. On Linux/macOS the
  same lookup would fail. Returned `path` fields are always the canonical
  on-disk casing; pass them back verbatim.
- **Wikilinks inside fenced code blocks and inline code spans are ignored.**
  Prose like `` `[[react]]` `` in a code span won't pollute `read_note.wikilinks`
  or appear as a backlink. Only real graph edges are extracted.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff format src tests
mypy src
```

### Test cases

In addition to the pytest suite, [`docs/testcases/`](docs/testcases/README.md)
documents 51 manual integration cases used to validate every tool against
a live vault. Each case lists the exact call, the expected outcome, and
the behavior it certifies.

## Logging

The server logs to stderr only. stdio MCP servers must never write to stdout —
that channel is reserved for JSON-RPC.

## License

MIT
