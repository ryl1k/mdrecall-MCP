"""Smoke tests against the real vault. Run with: python scripts/smoke.py"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vault_mcp.backlinks import find_backlinks
from vault_mcp.frontmatter import query_frontmatter
from vault_mcp.search import search_notes
from vault_mcp.vault import Vault


def main() -> None:
    root = Path(os.environ.get("VAULT_PATH", r"D:\Documents\Knowledge"))
    v = Vault(root)
    print(f"=== Vault: {v.root}")

    print("\n[1] Projects with tech contains 'postgresql':")
    rows = query_frontmatter(v, {"type": "project", "tech": ["postgresql"]})
    for r in rows:
        print(f"  - {r['path']}  ({r['title']})")

    print("\n[2] Active projects (status=active):")
    rows = query_frontmatter(v, {"type": "project", "status": "active"})
    print(f"  count={len(rows)}")
    for r in rows:
        print(f"  - {r['path']}")

    print("\n[3] Backlinks to 070-concepts/tech/react.md:")
    rows = find_backlinks(v, "070-concepts/tech/react.md")
    for r in rows:
        print(f"  - {r['path']}")

    print("\n[4] read_note('010-projects/chess.md'):")
    n = v.get_note("010-projects/chess.md")
    print(f"  title:  {n.title}")
    print(f"  status: {n.status}")
    print(f"  tech:   {n.tech}")
    print(f"  body length: {len(n.body)} chars")

    print("\n[5] search_notes('agentic loop'):")
    rows = search_notes(v, "agentic loop")
    for r in rows:
        print(f"  - {r['path']}  score={r['score']}")


if __name__ == "__main__":
    main()
