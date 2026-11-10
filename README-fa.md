# dictcc-mcp 🌐

mcp-name: io.github.mohammad-abbasi-sh/dictcc-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **[dict.cc](https://www.dict.cc)** — ترجمه‌های dict.cc از dict.cc (رایگان، بدون کلید): آلمانی–انگلیسی و ۲۲ زبان دیگر، با نوع کلمه، جنسیت، توضیحات کاربرد و آرای کاربران. بدون کلید، بدون ورود.

> ساختهٔ محمد عباسی، بخشی از «کارخانهٔ MCP آلمان». وابسته به dict.cc نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP کلاینت اضافه کنید (stdio):

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

یا به‌صورت محلی اجرا کنید: `python -m dictcc_mcp.server` (نیازمند `mcp<2` و `httpx`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `dictcc_translate` | ترجمهٔ واژه با dict.cc (۲۳ زبان) |
| `dictcc_search` | یافتن سرخط‌های dict.cc مطابق پرس‌وجو |
| `dictcc_health` | بررسی دسترس‌پذیری (ok / blocked / error) — یک درخواست مؤدبانه |

## توسعه

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## لایسنس

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
