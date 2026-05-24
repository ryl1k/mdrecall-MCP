# vault-mcp

Local MCP server that exposes an Obsidian-style markdown knowledge vault to
Claude Desktop as a queryable memory layer. Read-only, stdio transport, no
network calls.

## Installation

```powershell
pip install -e .
```

This registers a `vault-mcp` console script that starts the stdio server.

## Wiring into Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "vault": {
      "command": "vault-mcp",
      "env": { "VAULT_PATH": "D:\\Documents\\Knowledge" }
    }
  }
}
```

If `vault-mcp` is not on the PATH that Claude Desktop sees, point at Python
directly:

```json
{
  "mcpServers": {
    "vault": {
      "command": "C:\\Users\\ryl1k\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": ["-m", "vault_mcp.server"],
      "env": { "VAULT_PATH": "D:\\Documents\\Knowledge" }
    }
  }
}
```

`VAULT_PATH` defaults to `D:\Documents\Knowledge` when unset.

## Tools

### `list_folders`
Top-level folders with note counts and short descriptions.

```
list_folders()
→ [{"name": "010-projects", "path": "010-projects", "description": "...", "note_count": 50}, ...]
```

### `list_notes(folder, recursive=false)`
Frontmatter summaries for notes in a folder.

```
list_notes(folder="070-concepts/tech", recursive=false)
→ [{"path": "070-concepts/tech/react.md", "title": "React", "type": "concept", "status": null, "tech": [], "tags": [...]}, ...]
```

### `read_note(path)`
Full content of one note.

```
read_note(path="010-projects/chess.md")
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
also match.

```
find_backlinks(path="070-concepts/tech/react.md")
→ [{"path": "010-projects/traceflow.md", "title": "...", "context": "..."}, ...]
```

## Conventions

- Vault-relative paths use forward slashes. The `.md` suffix is optional for
  `read_note` (`010-projects/chess` and `010-projects/chess.md` both work).
- Folders starting with `.` or `_` (e.g. `_archive/`) are excluded from
  listings, searches, and backlinks.
- Wikilink resolution is case-insensitive and treats `.md` as optional.
- Notes are parsed once and cached in memory; the cache invalidates per file
  when the file's mtime changes.

## Semantics worth knowing

These are quiet behaviors that surprised the author during dogfooding. None
are bugs; calling them out so they don't bite:

- **`search_notes` is literal substring, not regex.** Query is escaped and
  ranked by hit count. Whitespace and hyphens in the query are treated as one
  separator class (`agentic loop` matches `agentic-loop` and `agentic loops`).
  Regex metacharacters in the query match literally.
- **`query_frontmatter` empty list = no filter.** A falsy value (`[]`, `""`,
  `null` *in the search-filter list-args*) is ignored, not "match nothing".
  Use a missing key when you mean "don't filter". Use explicit `null` in
  `filters` to mean "field must be null or absent".
- **Path case-sensitivity follows the OS.** On Windows the filesystem is
  case-insensitive, so `Chess.md` resolves to `chess.md`. On Linux/macOS the
  same lookup would fail. Returned `path` fields are always the canonical
  on-disk casing; pass them back verbatim.
- **Wikilinks inside fenced code blocks and inline code spans are ignored.**
  Prose like `[[react]]` in a code span won't pollute `read_note.wikilinks`
  or appear as a backlink. Only real graph edges are extracted.

## Development

```powershell
pip install -e ".[dev]"
pytest
ruff format src tests
mypy src
```

## Logging

The server logs to stderr only. stdio MCP servers must never write to stdout —
that channel is reserved for JSON-RPC.
