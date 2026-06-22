"""
HYDRA SUMMARY — Email Builder
-------------------------------
Builds the HTML email matching the Hydra Brief template, using
table-based layout so the design (full-width section bars, consistent
alignment, single-line rows on mobile) renders reliably across email
clients — flexbox and negative-margin "bleed" tricks are unreliable
in Gmail/Outlook/mobile mail apps, so everything here uses <table>.
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
    news_html    = _build_news(digest.get("news", []))
    diary_html   = _build_diary(digest.get("diary", []))
    numbers_html = _build_numbers(digest.get("numbers", []), digest.get("numbers_timestamp", ""))

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
<body style="margin:0;padding:20px 12px 44px;background:{BG};{JOST}color:{IN};font-size:16px;line-height:1.45;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;margin:0 auto;background:#ffffff;">
<tr><td style="padding:0 0 6px;">

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-bottom:2px solid {B};">
    <tr>
      <td style="padding:16px 20px 15px;font-weight:500;font-size:18px;color:{B};letter-spacing:.1em;text-transform:uppercase;">Hydra Brief</td>
      <td align="right" style="padding:16px 20px 15px;{MONO}font-size:13px;color:{MU};white-space:nowrap;">{short_date}</td>
    </tr>
  </table>

  {lead_html}
  {news_html}
  {diary_html}
  {numbers_html}

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid {RU};margin-top:8px;">
    <tr><td style="padding:10px 20px 0;{MONO}font-size:11px;color:{A0};">
      <a href="https://hydra-advisory.com" style="color:{MU};">hydra-advisory.com</a> ·
      <a href="*|UNSUB|*" style="color:{MU};">Unsubscribe</a> · Hydra Advisory
    </td></tr>
  </table>

</td></tr>
</table>

</body>
</html>"""


# ── Helpers ───────────────────────────────────────────────────────────────

def _eyebrow(label: str, right_label: str = "") -> str:
    if right_label:
        inner = (
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="{MONO}font-size:12px;font-weight:500;letter-spacing:.16em;text-transform:uppercase;color:{CR};">{label}</td>'
            f'<td align="right" style="{MONO}font-size:10px;font-weight:400;letter-spacing:.05em;text-transform:none;color:#d8c9a8;white-space:nowrap;">{right_label}</td>'
            f'</tr></table>'
        )
    else:
        inner = label
    return (
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        f'<tr><td style="background:{B};padding:6px 20px;{MONO}font-size:12px;font-weight:500;'
        f'letter-spacing:.16em;text-transform:uppercase;color:{CR};">{inner}</td></tr></table>'
    )


def _section(label: str, rows_html: str, right_label: str = "") -> str:
    return (
        _eyebrow(label, right_label)
        + f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        f'<tr><td style="padding:8px 20px 0;">{rows_html}</td></tr></table>'
    )


def _row_table(inner: str) -> str:
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td>{inner}</td></tr></table>'


def _source_link(text: str, href: str) -> str:
    return (
        f'<a href="{href}" style="{MONO}font-size:13px;color:{B};'
        f'text-decoration:none;border-bottom:1px solid {G};white-space:nowrap;">{text}</a>'
    )


def _also(names: list) -> str:
    if not names:
        return ""
    joined = ", ".join(_esc(s) for s in names[:3])
    return f'<span style="color:{A0};"> · also {joined}</span>'


def _also_slash(names: list) -> str:
    if not names:
        return ""
    joined = "/".join(_esc(s) for s in names[:3])
    return f'/{joined}'


# ── Section builders ──────────────────────────────────────────────────────

def _build_lead(items: list) -> str:
    if not items:
        return ""
    rows = ""
    sliced = items[:3]
    for i, item in enumerate(sliced):
        text    = _esc(_truncate_words(item.get("text", ""), 6))
        link    = item.get("link", "")
        primary = _esc(item.get("primary_source", ""))
        also    = item.get("also", [])

        title_html = f'<a href="{link}" style="color:{IN};text-decoration:none;">{text}</a>' if link else text
        src_html = (_source_link(primary, link) if link else primary) if primary else ""
        also_html = _also(also) if also else ""
        suffix = f' <span style="{MONO}font-size:13px;font-weight:400;color:{MU};">{src_html}{also_html}</span>' if src_html else ""

        pad = "0 0 10px" if i == len(sliced) - 1 else "0 0 7px"
        rows += _row_table(
            f'<div style="padding:{pad};font-size:15px;font-weight:400;line-height:1.35;color:{IN};">'
            f'&bull;&nbsp; {title_html}{suffix}</div>'
        )
    return _section("What You Should Know Today", rows)


def _build_news(items: list) -> str:
    if not items:
        return ""
    rows = ""
    sliced = items[:10]
    for i, item in enumerate(sliced):
        headline = _esc(_truncate_words(item.get("headline", ""), 8))
        link     = item.get("link", "")
        primary  = _esc(item.get("primary_source", ""))
        also     = item.get("also", [])

        title_html = f'<a href="{link}" style="color:{IN};text-decoration:none;">{headline}</a>' if link else headline
        src = _source_link(primary, link) if link else primary
        also_html = _also_slash(also) if also else ""
        src_html = f' <span style="{MONO}font-size:13px;font-weight:400;color:{MU};">{src}{also_html}</span>' if src else ""
        pad = "6px 8px 6px" if i == len(sliced) - 1 else "6px 8px"
        bg = f'background:#f7f6f4;border-radius:3px;' if i % 2 == 0 else ""

        rows += (
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td style="{bg}padding:{pad};">'
            f'<div style="font-size:15px;font-weight:400;line-height:1.35;color:{IN};'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'&bull;&nbsp; {title_html}{src_html}</div>'
            f'</td></tr></table>'
        )
        if i < len(sliced) - 1:
            rows += '<div style="height:4px;line-height:4px;font-size:0;">&nbsp;</div>'
    return _section("News", rows)


def _build_diary(items: list) -> str:
    if not items:
        return ""
    rows = ""
    sliced = items[:4]
    for i, item in enumerate(sliced):
        event = _esc(item.get("event", ""))
        desc  = _esc(item.get("description", ""))
        dates = _esc(item.get("dates", ""))
        pad = "0 0 10px" if i == len(sliced) - 1 else "0 0 7px"
        rows += (
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="padding:{pad};font-size:15px;line-height:1.35;">'
            f'<div style="font-weight:500;">{event}</div>'
            f'<div style="color:{MU};font-size:14px;">{desc}</div>'
            f'</td>'
            f'<td align="right" valign="top" style="padding:{pad};{MONO}font-size:13px;color:{B};white-space:nowrap;">{dates}</td>'
            f'</tr></table>'
        )
    return _section("Sector Diary", rows)


def _build_numbers(items: list, timestamp: str) -> str:
    if not items:
        return ""
    sliced = items[:6]
    rows = ""
    for i, item in enumerate(sliced):
        name      = _esc(item.get("name", ""))
        ticker    = _esc(item.get("ticker", ""))
        price     = _esc(item.get("price", ""))
        change    = _esc(item.get("change", ""))
        direction = item.get("direction", "flat")
        context   = _esc(_truncate_words(item.get("context", ""), 5))
        colour    = GR if direction == "up" else (RD if direction == "down" else MU)
        pad = "0" if i == len(sliced) - 1 else "0 0 8px"

        rows += (
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="font-size:15px;font-weight:400;color:{IN};">{name} <span style="color:{MU};{MONO}font-size:13px;font-weight:400;">&middot; {ticker}</span></td>'
            f'<td align="right" style="{MONO}font-size:13px;color:{B};white-space:nowrap;font-weight:400;">{price} <span style="color:{colour};">{change}</span></td>'
            f'</tr></table>'
            f'<div style="font-size:14px;color:{MU};line-height:1.3;padding:{pad};">{context}</div>'
        )

    return _section("Important Numbers", rows, right_label=_esc(timestamp))


def _truncate_words(text: str, max_words: int) -> str:
    words = str(text).split()
    if len(words) <= max_words:
        return str(text)
    return " ".join(words[:max_words]).rstrip(".,;:") + "…"


def _esc(text: str) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
