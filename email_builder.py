"""
HYDRA SUMMARY — Email Builder
-------------------------------
Builds the HTML email using the Hydra Brief visual design.
All styles are inlined for email client compatibility.
"""

import logging
from datetime import datetime

log = logging.getLogger("hydra-summary.builder")

# ── Colour palette ────────────────────────────────────────────────────────
BURGUNDY = "#3D0C1F"
GOLD     = "#B8922A"
CREAM    = "#F4EFE7"
INK      = "#1f1f1f"
MUTED    = "#7a7a7a"
RULE     = "#e2e2e2"
BG       = "#f4f2ef"
GREEN    = "#2f7d4f"
RED      = "#9a3b3b"
DIM      = "#4a4a4a"
ALSO     = "#a0a0a0"

MONO  = "font-family:'DM Mono',monospace;"
SERIF = "font-family:'Jost',sans-serif;"


def build_email_html(digest: dict, today: str) -> str:
    lead_html    = _build_lead(digest.get("lead_items", []))
    numbers_html = _build_numbers(digest.get("numbers", []))
    news_html    = _build_news(digest.get("news", []))
    roles_html   = _build_roles(digest.get("roles", []))
    diary_html   = _build_diary(digest.get("diary", []))

    try:
        dt = datetime.strptime(today, "%A, %d %B %Y")
        short_date = dt.strftime("%a · %-d %b %Y")
    except Exception:
        short_date = today

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hydra Brief · {today}</title>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:20px 12px 44px;background:{BG};{SERIF}color:{INK};font-size:14px;line-height:1.45;">

<div style="max-width:580px;margin:0 auto;background:#ffffff;padding:0 0 6px;">

  <!-- Header -->
  <div style="display:flex;justify-content:space-between;align-items:baseline;padding:14px 20px 13px;border-bottom:2px solid {BURGUNDY};">
    <div style="font-weight:600;font-size:15px;color:{BURGUNDY};letter-spacing:.14em;text-transform:uppercase;">Hydra Brief</div>
    <div style="{MONO}font-size:11px;color:{MUTED};">{short_date}</div>
  </div>

  {lead_html}
  {numbers_html}
  {news_html}
  {roles_html}
  {diary_html}

  <!-- Footer -->
  <div style="padding:13px 20px 0;border-top:1px solid {RULE};margin-top:2px;{MONO}font-size:10px;color:{ALSO};">
    <a href="https://hydra-advisory.com" style="color:{MUTED};text-decoration:none;">hydra-advisory.com</a>
    &nbsp;·&nbsp;
    <a href="*|UNSUB|*" style="color:{MUTED};text-decoration:none;">Unsubscribe</a>
    &nbsp;·&nbsp;Hydra Advisory · Milan
  </div>

</div>
</body>
</html>"""


# ── Helpers ───────────────────────────────────────────────────────────────

def _eyebrow(label: str) -> str:
    return f'<div style="margin:0 -20px 10px;padding:6px 20px;background:{BURGUNDY};{MONO}font-size:10.5px;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:{CREAM};">{label}</div>'


def _sec_open() -> str:
    return f'<div style="padding:0 20px 12px;">'


def _sec_close() -> str:
    return '</div>'


# ── Section builders ──────────────────────────────────────────────────────

def _build_lead(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:3]:
        text = _esc(item.get("text", ""))
        link = item.get("link", "")
        if link:
            headline = f'<a href="{link}" style="color:{INK};text-decoration:none;">{text}</a>'
        else:
            headline = text
        rows += f'<div style="padding:0 0 9px;"><div style="font-size:14px;font-weight:600;line-height:1.15;color:{INK};">{headline}</div></div>\n'

    return (
        _sec_open()
        + _eyebrow("What You Should Know Today")
        + rows
        + _sec_close()
    )


def _build_numbers(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:4]:
        name      = _esc(item.get("name", ""))
        ticker    = _esc(item.get("ticker", ""))
        price     = _esc(item.get("price", ""))
        change    = _esc(item.get("change", ""))
        direction = item.get("direction", "flat")
        context   = _esc(item.get("context", ""))
        colour    = GREEN if direction == "up" else (RED if direction == "down" else MUTED)

        rows += f"""<div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:0 0 3px;font-size:13.5px;line-height:1.32;">
  <div style="color:{INK};">{name} <span style="color:{MUTED};font-size:12px;">· {ticker}</span></div>
  <div style="{MONO}font-size:13px;color:{BURGUNDY};white-space:nowrap;font-weight:500;">{price} <span style="color:{colour};">{change}</span></div>
</div>
<div style="font-size:12px;color:{DIM};padding:0 0 10px;line-height:1.3;">{context}</div>\n"""

    return (
        _sec_open()
        + _eyebrow("Important Numbers")
        + rows
        + _sec_close()
    )


def _build_news(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:7]:
        headline = _esc(item.get("headline", ""))
        link     = item.get("link", "")
        summary  = _esc(item.get("summary", ""))
        primary  = _esc(item.get("primary_source", ""))
        also     = item.get("also", [])

        also_str = ""
        if also:
            also_names = ", ".join(_esc(s) for s in also[:3])
            also_str = f' <span style="{MONO}font-size:10px;color:{ALSO};">· also {also_names}</span>'

        src_link = f'<a href="{link}" style="{MONO}font-size:10px;color:{BURGUNDY};text-decoration:none;border-bottom:1px solid {GOLD};white-space:nowrap;">{primary}</a>' if link else primary

        rows += f"""<div style="padding:0 0 9px;">
  <div style="font-size:14px;font-weight:600;line-height:1.15;color:{INK};">{headline}</div>
  <div style="font-size:13px;color:{DIM};line-height:1.32;margin-top:1px;">{summary} {src_link}{also_str}</div>
</div>\n"""

    return (
        _sec_open()
        + _eyebrow("News")
        + rows
        + _sec_close()
    )


def _build_roles(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:5]:
        title     = _esc(item.get("title", ""))
        role_type = _esc(item.get("type", ""))
        house     = _esc(item.get("house", ""))

        rows += f"""<div style="display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:0 0 8px;font-size:13px;line-height:1.3;">
  <div>
    <div style="font-weight:500;">{title}</div>
    <div style="color:{MUTED};font-size:12px;">{house} · {role_type}</div>
  </div>
</div>\n"""

    return (
        _sec_open()
        + _eyebrow("Roles")
        + rows
        + _sec_close()
    )


def _build_diary(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:4]:
        event = _esc(item.get("event", ""))
        desc  = _esc(item.get("description", ""))
        dates = _esc(item.get("dates", ""))

        rows += f"""<div style="display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:0 0 8px;font-size:13px;line-height:1.3;">
  <div>
    <div style="font-weight:500;">{event}</div>
    <div style="color:{MUTED};font-size:12px;">{desc}</div>
  </div>
  <div style="{MONO}font-size:10px;color:{BURGUNDY};white-space:nowrap;">{dates}</div>
</div>\n"""

    return (
        _sec_open()
        + _eyebrow("Sector Diary")
        + rows
        + _sec_close()
    )


def _esc(text: str) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
