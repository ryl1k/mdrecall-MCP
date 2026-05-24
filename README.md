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
value for one key is any-of.

```
query_frontmatter(filters={"status": "active"})
query_frontmatter(filters={"tech": ["postgresql"]})
query_frontmatter(filters={"status": "active", "tech": ["python"]})
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

- Vault-relative paths use forward slashes and include `.md`
  (e.g. `010-projects/chess.md`).
- Folders starting with `.` or `_` (e.g. `_archive/`) are excluded from
  listings, searches, and backlinks.
- Wikilink resolution is case-insensitive and treats `.md` as optional.
- Notes are parsed once and cached in memory; the cache invalidates per file
  when the file's mtime changes.

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
