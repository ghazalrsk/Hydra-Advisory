"""
HYDRA SUMMARY — Email Builder
-------------------------------
Builds the HTML email matching the Hydra Brief template exactly,
with all CSS inlined for email client compatibility.
"""

import logging
from datetime import datetime

log = logging.getLogger("hydra-summary.builder")

B  = "#3D0C1F"   # burgundy
G  = "#B8922A"   # gold
CR = "#F4EFE7"   # cream
IN = "#1f1f1f"   # ink
MU = "#7a7a7a"   # muted
RU = "#e2e2e2"   # rule
BG = "#f4f2ef"   # background
D4 = "#4a4a4a"   # dark grey text
A0 = "#a0a0a0"   # also / dim
GR = "#2f7d4f"   # green (up)
RD = "#9a3b3b"   # red (down)
MONO = "font-family:'DM Mono',monospace;"
JOST = "font-family:'Jost',sans-serif;"


def build_email_html(digest: dict, today: str) -> str:
    try:
        dt = datetime.strptime(today, "%A, %d %B %Y")
        short_date = dt.strftime("%a · %-d %b %Y")
    except Exception:
        short_date = today

    lead_html    = _build_lead(digest.get("lead_items", []))
    numbers_html = _build_numbers(digest.get("numbers", []))
    news_html    = _build_news(digest.get("news", []))
    roles_html   = _build_roles(digest.get("roles", []))
    diary_html   = _build_diary(digest.get("diary", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hydra Brief · {today}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
<body style="box-sizing:border-box;margin:0;padding:20px 12px 44px;background:{BG};{JOST}color:{IN};font-size:14px;line-height:1.45;">

  <div style="max-width:580px;margin:0 auto;background:#fff;padding:0 0 6px;">

    <!-- Header -->
    <div style="display:flex;justify-content:space-between;align-items:baseline;padding:14px 20px 13px;border-bottom:2px solid {B};">
      <div style="font-weight:600;font-size:15px;color:{B};letter-spacing:.14em;text-transform:uppercase;">Hydra Brief</div>
      <div style="{MONO}font-size:11px;color:{MU};">{short_date}</div>
    </div>

    {lead_html}
    {numbers_html}
    {news_html}
    {roles_html}
    {diary_html}

    <!-- Footer -->
    <div style="padding:13px 20px 0;border-top:1px solid {RU};margin-top:2px;{MONO}font-size:10px;color:{A0};">
      <a href="https://hydra-advisory.com" style="color:{MU};">hydra-advisory.com</a> ·
      <a href="*|UNSUB|*" style="color:{MU};">Unsubscribe</a> · Hydra Advisory
    </div>

  </div>
</body>
</html>"""


# ── Helpers ───────────────────────────────────────────────────────────────

def _eyebrow(label: str) -> str:
    return (
        f'<div style="{MONO}font-size:10.5px;font-weight:500;letter-spacing:.18em;'
        f'text-transform:uppercase;color:{CR};background:{B};'
        f'margin:0 -20px 10px;padding:6px 20px;">{label}</div>'
    )

def _story(title: str, desc_html: str) -> str:
    return (
        f'<div style="padding:0 0 9px;">'
        f'<div style="font-size:14px;font-weight:600;line-height:1.15;color:{IN};">{title}</div>'
        f'<div style="font-size:13px;color:{D4};line-height:1.32;margin-top:-1px;">{desc_html}</div>'
        f'</div>'
    )

def _source_link(text: str, href: str) -> str:
    return (
        f'<a href="{href}" style="{MONO}font-size:10px;color:{B};'
        f'text-decoration:none;border-bottom:1px solid {G};white-space:nowrap;">{text}</a>'
    )

def _also(names: list) -> str:
    if not names:
        return ""
    joined = ", ".join(_esc(s) for s in names[:3])
    return f'<span style="{MONO}font-size:10px;color:{A0};">· also {joined}</span>'


# ── Section builders ──────────────────────────────────────────────────────

def _build_lead(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:3]:
        text = _esc(item.get("text", ""))
        link = item.get("link", "")
        title_html = f'<a href="{link}" style="color:{IN};text-decoration:none;">{text}</a>' if link else text
        # lead items: title only, no description line
        rows += (
            f'<div style="padding:0 0 9px;">'
            f'<div style="font-size:14px;font-weight:600;line-height:1.15;color:{IN};">{title_html}</div>'
            f'</div>\n'
        )
    return (
        f'<div style="padding:0 20px 12px;">'
        + _eyebrow("What You Should Know Today")
        + rows
        + '</div>'
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
        colour    = GR if direction == "up" else (RD if direction == "down" else MU)

        rows += (
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
            f'gap:12px;padding:0 0 5px;font-size:13.5px;line-height:1.32;">'
            f'<div style="color:{IN};">{name} <span style="color:{MU};font-size:12px;">· {ticker}</span></div>'
            f'<div style="{MONO}font-size:13px;color:{B};white-space:nowrap;font-weight:500;">'
            f'{price} <span style="color:{colour};">{change}</span></div>'
            f'</div>'
            f'<div style="font-size:12px;color:{D4};line-height:1.3;padding:0 0 8px;">{context}</div>\n'
        )
    return (
        f'<div style="padding:0 20px 12px;">'
        + _eyebrow("Important Numbers")
        + rows
        + '</div>'
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

        src = _source_link(primary, link) if link else primary
        also_html = " " + _also(also) if also else ""

        rows += _story(headline, f'{summary} {src}{also_html}') + "\n"

    return (
        f'<div style="padding:0 20px 12px;">'
        + _eyebrow("News")
        + rows
        + '</div>'
    )


def _build_roles(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:5]:
        title     = _esc(item.get("title", ""))
        role_type = _esc(item.get("type", ""))
        house     = _esc(item.get("house", ""))
        rows += (
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
            f'gap:10px;padding:0 0 8px;font-size:13px;line-height:1.3;">'
            f'<div>'
            f'<div style="font-weight:500;">{title}</div>'
            f'<div style="color:{MU};font-size:12px;">{house} · {role_type}</div>'
            f'</div>'
            f'</div>\n'
        )
    return (
        f'<div style="padding:0 20px 12px;">'
        + _eyebrow("Roles")
        + rows
        + '</div>'
    )


def _build_diary(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:4]:
        event = _esc(item.get("event", ""))
        desc  = _esc(item.get("description", ""))
        dates = _esc(item.get("dates", ""))
        rows += (
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
            f'gap:10px;padding:0 0 8px;font-size:13px;line-height:1.3;">'
            f'<div>'
            f'<div style="font-weight:500;">{event}</div>'
            f'<div style="color:{MU};font-size:12px;">{desc}</div>'
            f'</div>'
            f'<div style="{MONO}font-size:10px;color:{B};white-space:nowrap;">{dates}</div>'
            f'</div>\n'
        )
    return (
        f'<div style="padding:0 20px 12px;">'
        + _eyebrow("Sector Diary")
        + rows
        + '</div>'
    )


def _esc(text: str) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
