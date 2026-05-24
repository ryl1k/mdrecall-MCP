# `search_notes` — Test Cases

## Case 1 — Simple keyword

- **Input**: `search_notes(query="CIFAR", limit=5)`
- **Expected**: 5 results sorted by hit count descending; top hit is
  `010-projects/chess.md` (score 6).
- **Validates**: substring matching; hit-count ranking.

## Case 2 — Multi-word query with hyphen equivalence

- **Input**: `search_notes(query="agentic loop", limit=5)`
- **Expected**: 5 project notes referencing the agentic-loop concept,
  matching both `agentic loop` and `agentic-loop` and `agentic loops`.
- **Validates**: whitespace and hyphens treated as one separator class;
  no need to know the exact punctuation.

## Case 3 — Unicode query

- **Input**: `search_notes(query="МТРС", limit=5)`
- **Expected**: `[]` (string not present); no crash.
- **Validates**: Cyrillic / non-ASCII queries are accepted and processed.

## Case 4 — Case-insensitive query

- **Input**: `search_notes(query="POSTGRESQL", limit=5)`
- **Expected**: same hits as lowercase `postgresql`.
- **Validates**: query is case-folded before matching.

## Case 5 — With `types` filter

- **Input**: `search_notes(query="python", types=["concept"], limit=3)`
- **Expected**: only `070-concepts/...` notes.
- **Validates**: type filter narrows candidates before body search.

## Case 6 — With `status` filter (list)

- **Input**: `search_notes(query="react", status=["active", "paused"], limit=3)`
- **Expected**: 3 results, none with `status: archived`.
- **Validates**: list filter is any-of; archived notes correctly excluded.

## Case 7 — With `tech` filter

- **Input**: `search_notes(query="jwt", tech=["postgresql"], limit=5)`
- **Expected**: only notes that have `postgresql` in `tech` and also
  contain `jwt` in body or frontmatter.
- **Validates**: tech filter intersects with body match.

## Case 8 — All filters combined

- **Input**: `search_notes(query="docker", types=["project"], status=["active"], tech=["python"], limit=3)`
- **Expected**: 1 result (`010-projects/lpnu-connect.md`).
- **Validates**: multi-filter AND semantics; correctly narrows to the
  intersection.

## Case 9 — No-match query

- **Input**: `search_notes(query="zzz-no-such-string-anywhere", limit=5)`
- **Expected**: `[]`.
- **Validates**: empty result is returned cleanly, not an error.

## Case 10 — Aggressive `limit`

- **Input**: `search_notes(query="ML", limit=1)`
- **Expected**: exactly 1 result, the highest-scored match.
- **Validates**: limit clamps result count; sort order preserved before
  truncation. Note: 2-letter queries can match inside larger words
  (`HTML`, `XML`, `YAML`) — substring behavior, by design.
