# dictcc-mcp 🌐

mcp-name: io.github.mohammad-abbasi-sh/dictcc-mcp

Unofficial **read-only** MCP server for **[dict.cc](https://www.dict.cc)** — dict.cc translations from dict.cc (free, no key, no login): German-English plus 22 more pairs, with word class, gender, usage notes and community votes. No key, no login.

> Built by Mohammad Abbasi as part of the "Germany MCP factory". Not affiliated with dict.cc.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "dictcc": {
      "command": "uvx",
      "args": ["dictcc-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m dictcc_mcp.server` (needs `mcp<2`, `httpx`).

## Tools

| Tool | Description |
|------|-------------|
| `dictcc_translate` | Translate a word or phrase with dict.cc: translations with word class, gender, usage notes & community votes — `query`, `pair` (de-en default; de-el, de-eo, de-es, de-fi, de-fr, de-hr, de-hu, de-is, de-it, de-la, de-nl, de-no, de-pl, de-pt, de-ro, de-ru, de-sk, de-sq, de-sr, de-sv, de-tr, de-uk), `limit` 1..50 |
| `dictcc_search` | Find dict.cc headwords matching a query (prefix/containment) — `query`, `pair` (de-en default), `limit` 1..50 |
| `dictcc_health` | Reachability probe (ok / blocked / error) — one polite request |

## Notes

- All data comes from **dict.cc's public search pages** (free, no key, no login).
- Translation rows carry the word, `<var>` word-class markers (`{adj}`, `{n}`, `{f}` …), `<kbd>` bracket notes and the community vote count; rows are returned in dict.cc's own vote ranking.
- 23 language pairs share the same page structure (DE-EN on `www.dict.cc`, the rest on `<deXX>.dict.cc`); the query direction is auto-detected from which side matches first in dict.cc's ranking.
- dict.cc has NO example sentences and NO verb conjugation on these pages (verified 2026-11-10) — only translations and headword search are exposed. For verb conjugation use `duden-mcp`.
- A query with no matches returns 200 with zero rows (not an error).

Tests: 23/23 green (18 offline + 5 live, 2026-11-10).

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
