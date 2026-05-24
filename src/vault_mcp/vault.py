"""Vault filesystem abstraction: walk, parse frontmatter, cache by mtime."""

from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import frontmatter

logger = logging.getLogger(__name__)

WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]+)?(?:\|[^\]]+)?\]\]")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def strip_code_spans(text: str) -> str:
    """Replace fenced and inline code regions with spaces of equal length.

    Equal-length replacement preserves character offsets so callers can use
    match positions from the masked text against the original body for snippets.
    """

    def _blank(m: re.Match[str]) -> str:
        return " " * (m.end() - m.start())

    text = FENCED_CODE_RE.sub(_blank, text)
    text = INLINE_CODE_RE.sub(_blank, text)
    return text


@dataclass(frozen=True)
class Note:
    """Parsed representation of a single markdown note."""

    path: str
    abs_path: Path
    mtime: float
    title: str
    frontmatter: dict[str, Any]
    body: str

    @property
    def type(self) -> str | None:
        value = self.frontmatter.get("type")
        return value if isinstance(value, str) else None

    @property
    def status(self) -> str | None:
        value = self.frontmatter.get("status")
        return value if isinstance(value, str) else None

    @property
    def tech(self) -> list[str]:
        value = self.frontmatter.get("tech")
        return list(value) if isinstance(value, list) else []

    @property
    def tags(self) -> list[str]:
        value = self.frontmatter.get("tags")
        return list(value) if isinstance(value, list) else []

    def summary(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "title": self.title,
            "type": self.type,
            "status": self.status,
            "tech": self.tech,
            "tags": self.tags,
        }

    def linkable_body(self) -> str:
        """Body with fenced/inline code regions blanked out. Offsets preserved."""
        return strip_code_spans(self.body)

    def wikilink_targets(self) -> list[str]:
        return [
            _canonicalize_target(m.group(1)) for m in WIKILINK_RE.finditer(self.linkable_body())
        ]


@dataclass
class _CacheEntry:
    note: Note
    mtime: float


def _canonicalize_target(target: str) -> str:
    """Normalize a wikilink target to canonical vault-relative form (no `.md`, lowercase, /)."""

    cleaned = target.strip().replace("\\", "/")
    if cleaned.lower().endswith(".md"):
        cleaned = cleaned[:-3]
    return cleaned.lower().strip("/")


def canonical_path(path: str) -> str:
    """Canonical form for both wikilink targets and vault-relative `.md` paths."""

    return _canonicalize_target(path)


def _first_heading(body: str) -> str | None:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


class Vault:
    """Read-only view over an Obsidian vault rooted at `root`.

    Caches parsed notes in memory; re-parses a file when its mtime changes.
    Hidden folders (names starting with `.` or `_`) are skipped.
    """

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        if not self.root.is_dir():
            raise FileNotFoundError(f"Vault path does not exist: {self.root}")
        self._cache: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()

    def _iter_markdown_files(self, base: Path) -> list[Path]:
        results: list[Path] = []
        for entry in base.iterdir():
            name = entry.name
            if name.startswith(".") or name.startswith("_"):
                continue
            if entry.is_dir():
                results.extend(self._iter_markdown_files(entry))
            elif entry.is_file() and entry.suffix.lower() == ".md":
                results.append(entry)
        return results

    def _rel_path(self, abs_path: Path) -> str:
        return abs_path.resolve().relative_to(self.root).as_posix()

    def _load_note(self, abs_path: Path) -> Note:
        mtime = abs_path.stat().st_mtime
        rel = self._rel_path(abs_path)
        with self._lock:
            cached = self._cache.get(rel)
            if cached is not None and cached.mtime == mtime:
                return cached.note
        try:
            post = frontmatter.load(str(abs_path))
        except Exception as exc:
            logger.warning("Failed to parse frontmatter for %s: %s", rel, exc)
            post = frontmatter.Post(content=abs_path.read_text(encoding="utf-8", errors="replace"))
        body = post.content or ""
        title = _first_heading(body) or abs_path.stem
        note = Note(
            path=rel,
            abs_path=abs_path,
            mtime=mtime,
            title=title,
            frontmatter=dict(post.metadata),
            body=body,
        )
        with self._lock:
            self._cache[rel] = _CacheEntry(note=note, mtime=mtime)
        return note

    def resolve(self, path: str) -> Path:
        """Resolve a vault-relative path to an absolute path; ensure it stays inside the vault."""

        normalized = path.replace("\\", "/").lstrip("/")
        abs_path = (self.root / normalized).resolve()
        if self.root not in abs_path.parents and abs_path != self.root:
            raise ValueError(f"Path escapes vault: {path}")
        return abs_path

    def get_note(self, path: str) -> Note:
        """Read and parse a single note. The `.md` suffix is optional."""

        abs_path = self.resolve(path)
        if not abs_path.is_file() and not path.lower().endswith(".md"):
            abs_path = self.resolve(path + ".md")
        if not abs_path.is_file():
            raise FileNotFoundError(f"Note not found: {path}")
        return self._load_note(abs_path)

    def iter_notes(self, folder: str | None = None, recursive: bool = True) -> list[Note]:
        """All notes in `folder` (vault-relative), recursive by default."""

        base = self.root if folder in (None, "", ".") else self.resolve(folder or "")
        if not base.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder}")
        if recursive:
            files = self._iter_markdown_files(base)
        else:
            files = [
                p
                for p in base.iterdir()
                if p.is_file() and p.suffix.lower() == ".md" and not p.name.startswith((".", "_"))
            ]
        return [self._load_note(p) for p in files]

    def top_level_folders(self) -> list[Path]:
        return sorted(
            (p for p in self.root.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))),
            key=lambda p: p.name,
        )

    def count_notes(self, folder: Path) -> int:
        return len(self._iter_markdown_files(folder))
