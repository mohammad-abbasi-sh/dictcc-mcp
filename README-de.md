# dictcc-mcp 🌐

mcp-name: io.github.mohammad-abbasi-sh/dictcc-mcp

Inoffizieller **nur lesender** MCP-Server für **[dict.cc](https://www.dict.cc)** — dict.cc-Übersetzungen von dict.cc (kostenlos, kein Schlüssel, kein Login): Deutsch-Englisch plus 22 weitere Sprachenpaare, mit Wortart, Genus, Gebrauchshinweisen und Community-Stimmen. Kein Schlüssel, keine Anmeldung.

> Gebaut von Mohammad Abbasi als Teil der "Germany MCP factory". Nicht mit dict.cc verbunden.

## Für KI-Agenten

Zur MCP-Client-Konfiguration hinzufügen (stdio):

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

Oder lokal starten: `python -m dictcc_mcp.server` (benötigt `mcp<2`, `httpx`).

## Tools

| Tool | Beschreibung |
|------|-------------|
| `dictcc_translate` | Ein Wort mit dict.cc übersetzen (23 Sprachenpaare) |
| `dictcc_search` | dict.cc-Stichwörter zu einer Suchanfrage finden |
| `dictcc_health` | Erreichbarkeitsprüfung (ok / blocked / error) — eine höfliche Anfrage |

## Entwicklung

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## Lizenz

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
