"""MCP server: unofficial read-only access to dict.cc translations.
No key, no login. NOTE: dict.cc translation pages are server-rendered
HTML — rows are <tr id='trN'> with [foreign side][German side] cells
carrying the word, <var> word-class markers, <kbd> bracket notes and
a community vote count. dict.cc has NO example sentences and NO verb
conjugation on these pages (verified 2026-11-10), so the server
exposes only translations + headword search. 23 language pairs share
the same structure (DE-EN on www.dict.cc, the rest on
<deXX>.dict.cc); the query direction (de->xx or xx->de) is detected
from which side the query matches first in dict.cc's own ranking."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import domain as _dom
from . import http as _http

INSTRUCTIONS = """\
Unofficial read-only MCP server for dict.cc translations via its \
public search pages (no key, no login): translate a word or phrase \
in 23 language pairs (German-English plus German-French, -Spanish, \
-Italian, -Portuguese, -Dutch, -Swedish, -Russian, -Polish, -Turkish \
and more), with word class, gender, usage notes and community votes; \
or find headwords matching a query. NOTE: dict.cc has no example \
sentences and no verb conjugation on these pages — only translations \
and headwords are exposed. The query direction is auto-detected from \
which side matches first in dict.cc's ranking. Built by Mohammad \
Abbasi (mohammad-abbasi-sh) — https://almanibama.ir · \
https://mabbasi.ir — Germany MCP factory.\
"""

_SOURCE = "dict.cc"
_DISCLAIMER = "Unofficial read-only data from dict.cc; verify on the site before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


mcp = FastMCP("dictcc-mcp", instructions=INSTRUCTIONS)


@mcp.tool()
def dictcc_translate(query: str, pair: str = "de-en", limit: int = 10) -> str:
    """Translate a word or phrase with dict.cc: translations with
    word class, gender, usage notes and community votes.
    query: e.g. Haus, laufen, house. pair: de-en (default), de-el,
    de-eo, de-es, de-fi, de-fr, de-hr, de-hu, de-is, de-it, de-la,
    de-nl, de-no, de-pl, de-pt, de-ro, de-ru, de-sk, de-sq, de-sr,
    de-sv, de-tr, de-uk. limit: 1..50 (default 10)."""
    try:
        q = _dom.validate_query(query)
        p = _dom.validate_pair(pair)
        lim = _dom.validate_limit(limit)
        _sub, lang = _dom.PAIRS[p]
        items = _dom.parse_table(_http.fetch_text(_dom.pair_url(p, q)), lang)
        direction = _dom.detect_direction(items, q, lang)
    except (_http.DictccMcpError, ValueError) as e:
        return _err(e)
    return _ok({"query": q, "pair": p,
                "languages": f"de-{lang} ({_dom.LANG_NAMES[lang]})",
                "direction": (f"{direction} -> "
                              f"{lang if direction == 'de' else 'de'}"
                              if direction != "unknown" else "unknown"),
                "total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def dictcc_search(query: str, pair: str = "de-en", limit: int = 10) -> str:
    """Find dict.cc headwords containing a query (prefix or
    substring), in dict.cc's own ranking order.
    query: e.g. Hau, Haus. pair: de-en (default) or any supported
    pair (see dictcc_translate). limit: 1..50 (default 10)."""
    try:
        q = _dom.validate_query(query)
        p = _dom.validate_pair(pair)
        lim = _dom.validate_limit(limit)
        _sub, lang = _dom.PAIRS[p]
        hits = _dom.parse_search(_http.fetch_text(_dom.pair_url(p, q)),
                                 lang, q)
    except (_http.DictccMcpError, ValueError) as e:
        return _err(e)
    return _ok({"query": q, "pair": p,
                "total_results": len(hits),
                "count": min(lim, len(hits)), "items": hits[:lim]})


@mcp.tool()
def dictcc_health() -> str:
    """Check whether dict.cc is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    sys.exit(main())
