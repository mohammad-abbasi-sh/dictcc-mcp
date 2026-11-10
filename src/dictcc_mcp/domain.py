"""Domain logic: shape dict.cc translation pages into compact dicts
(stdlib only).

Data source: dict.cc public search pages
(https://www.dict.cc/?s=<word> for DE-EN,
https://<pair>.dict.cc/?s=<word> for the other pairs) — free, no key,
no login.

Page structure (server-rendered HTML, verified 2026-11-10):
- translation rows are <tr id='tr1'>…<tr id='trN'> with four <td>s:
  [spacer][foreign side][German side][spacer]. The foreign cell
  holds the word (first <a>), <var> word-class markers ({adj}, {n},
  {f} …) and <kbd> bracket notes; the German cell additionally
  carries a <div> with the community vote count. A no-match query
  returns 200 with zero rows.
- dict.cc has NO example sentences and NO verb conjugation on these
  pages (verified: 'Beispiel' 0, no verb links, no audio URLs) — the
  server exposes only what exists: translations + headword search.
- Other pairs share the same structure (verified DE-FR 39 rows,
  DE-ES 15, DE-IT 31, DE-TR/DE-RU 200).
"""
from __future__ import annotations

import html as _html
import re
from urllib.parse import quote

# pair code -> (subdomain, foreign language code). de-en lives on www.
PAIRS = {
    "de-en": ("www", "en"),
    "de-el": ("deel", "el"),
    "de-eo": ("deeo", "eo"),
    "de-es": ("dees", "es"),
    "de-fi": ("defi", "fi"),
    "de-fr": ("defr", "fr"),
    "de-hr": ("dehr", "hr"),
    "de-hu": ("dehu", "hu"),
    "de-is": ("deis", "is"),
    "de-it": ("deit", "it"),
    "de-la": ("dela", "la"),
    "de-nl": ("denl", "nl"),
    "de-no": ("deno", "no"),
    "de-pl": ("depl", "pl"),
    "de-pt": ("dept", "pt"),
    "de-ro": ("dero", "ro"),
    "de-ru": ("deru", "ru"),
    "de-sk": ("desk", "sk"),
    "de-sq": ("desq", "sq"),
    "de-sr": ("desr", "sr"),
    "de-sv": ("desv", "sv"),
    "de-tr": ("detr", "tr"),
    "de-uk": ("deuk", "uk"),
}

LANG_NAMES = {
    "en": "English", "el": "Greek", "eo": "Esperanto", "es": "Spanish",
    "fi": "Finnish", "fr": "French", "hr": "Croatian", "hu": "Hungarian",
    "is": "Icelandic", "it": "Italian", "la": "Latin", "nl": "Dutch",
    "no": "Norwegian", "pl": "Polish", "pt": "Portuguese",
    "ro": "Romanian", "ru": "Russian", "sk": "Slovak", "sq": "Albanian",
    "sr": "Serbian", "sv": "Swedish", "tr": "Turkish",
    "uk": "Ukrainian",
}

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_ROW_RE = re.compile(r"<tr id='tr\d+'>(.*?)</tr>", re.S)
_TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)


def validate_pair(pair: str) -> str:
    p = (pair or "de-en").strip().lower()
    if p not in PAIRS:
        raise ValueError(
            f"unsupported pair: {pair!r} "
            f"(use one of: {', '.join(sorted(PAIRS))})")
    return p


def validate_query(query: str) -> str:
    q = (query or "").strip()
    if not q:
        raise ValueError("query must not be empty")
    if len(q) > 100:
        raise ValueError("query too long (max 100 characters)")
    return q


def validate_limit(limit: int) -> int:
    if not 1 <= limit <= 50:
        raise ValueError(f"limit out of range: {limit} (expected 1..50)")
    return limit


def pair_url(pair: str, query: str) -> str:
    sub, _lang = PAIRS[pair]
    return f"https://{sub}.dict.cc/?s={quote(query)}"


def _clean(text: str) -> str:
    return _WS_RE.sub(" ", _html.unescape(_TAG_RE.sub(" ", text or ""))).strip()


def _parse_cell(cell: str) -> dict:
    """{word, info, votes} — word = first link text; info = <var>
    markers + <kbd> bracket notes; votes = community vote count."""
    m = re.search(r"<a[^>]*>(.*?)</a>", cell, re.S)
    word = _clean(m.group(1)) if m else ""
    # compound marker: <b>Haus</b>- / Akzept-<b>Haus</b> render with a
    # space around the hyphen after tag stripping; rejoin it
    word = re.sub(r"\s*-\s*", "-", word)
    markers = [_clean(v) for v in re.findall(
        r"<var[^>]*>([^<]*)</var>", cell)]
    notes = [_clean(k) for k in re.findall(
        r"<kbd[^>]*>([^<]*)</kbd>", cell)]
    notes = [n for n in notes if n]
    info_parts = [x for x in markers if x]
    if notes:
        info_parts.append(" ".join(notes))
    vm = re.search(r"<div[^>]*>(\d+)</div>", cell)
    return {"word": word,
            "info": " ".join(info_parts),
            "votes": int(vm.group(1)) if vm else 0}


def parse_table(html: str, other_lang: str) -> list[dict]:
    """[{german, german_info, <other_lang>, <other_lang>_info, votes}]
    — row order (dict.cc's own ranking by votes)."""
    out = []
    for row in _ROW_RE.findall(html):
        tds = _TD_RE.findall(row)
        if len(tds) < 3:
            continue
        foreign = _parse_cell(tds[1])
        german = _parse_cell(tds[2])
        if not foreign["word"] and not german["word"]:
            continue
        out.append({
            "german": german["word"],
            "german_info": german["info"],
            other_lang: foreign["word"],
            f"{other_lang}_info": foreign["info"],
            "votes": german["votes"] or foreign["votes"],
        })
    return out


def detect_direction(items: list[dict], query: str, other_lang: str) -> str:
    """Which side the query matched: 'de', the foreign code, or
    'unknown'. Rows are dict.cc's own relevance ranking, so the
    first row that matches decides; within a row, exact beats prefix
    beats substring. (A plain all-German-first scan mislabels an
    English query like 'house' because a German loanword 'House'
    sits further down the list.)"""
    q = query.casefold()
    for it in items:
        de, other = it["german"].casefold(), it[other_lang].casefold()
        if de == q:
            return "de"
        if other == q:
            return other_lang
        if de.startswith(q):
            return "de"
        if other.startswith(q):
            return other_lang
        if q in de:
            return "de"
        if q in other:
            return other_lang
    return "unknown"


def parse_search(html: str, other_lang: str, query: str) -> list[dict]:
    """Distinct headwords containing the query, from both sides of
    the result table, in row order: [{word, lang}]."""
    q = query.casefold()
    out: list[dict] = []
    seen = set()
    for it in parse_table(html, other_lang):
        for word, lang in ((it["german"], "de"),
                           (it[other_lang], other_lang)):
            key = (word.casefold(), lang)
            if word and q in word.casefold() and key not in seen:
                seen.add(key)
                out.append({"word": word, "lang": lang})
    return out
