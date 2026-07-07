"""
HYDRA SUMMARY — Email Builder
-------------------------------
Clean text-forward layout. Reads like a professional letter at any width.
"""

import logging
import os
import re
from datetime import datetime, timedelta
from urllib.parse import quote

log = logging.getLogger("hydra-summary.builder")

B  = "#3D0C1F"   # burgundy
G  = "#B8922A"   # gold
IN = "#1a1a1a"   # ink
MU = "#777777"   # muted
GR = "#2f7d4f"   # green (up)
RD = "#9a3b3b"   # red (down)
FONT = "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;"


def build_email_html(digest: dict, today: str) -> str:
    try:
        dt = datetime.strptime(today, "%A, %d %B %Y")
        short_date = dt.strftime("%-d %B %Y")
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
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<meta name="format-detection" content="telephone=no,date=no,address=no,email=no,url=no">
<title>Hydra Brief · {today}</title>
<style>
body {{ margin:0; padding:0; background:#f5f5f5; {FONT} }}
.wrap {{ max-width:600px; margin:0 auto; padding:32px 24px; background:#ffffff; }}
.hdr-title {{ font-size:24px; font-weight:600; color:{B}; letter-spacing:.08em; text-transform:uppercase; }}
.hdr-date {{ font-size:14px; color:{MU}; margin-top:2px; }}
.divider {{ border:none; border-top:2px solid {B}; margin:14px 0 20px; }}
.divider-thin {{ border:none; border-top:1px solid rgba(61,12,31,0.25); margin:14px 0 20px; }}
.section-label {{ font-size:12px; font-weight:800; letter-spacing:.18em; text-transform:uppercase; color:{B}; margin:28px 0 10px; padding-left:0; }}
.item {{ margin:0 0 7px 0; font-size:17px; line-height:1.5; color:{IN}; }}
.item-src {{ font-size:14px; color:{MU}; }}
.src-link {{ color:{MU}; text-decoration:none; border-bottom:1px solid #cccccc; }}
.num-row {{ display:flex; justify-content:space-between; font-size:16px; padding:6px 0; border-bottom:1px solid #eeeeee; color:{IN}; }}
.num-ticker {{ color:{MU}; font-size:14px; }}
.cal-link {{ font-size:13px; color:{MU}; text-decoration:none; border-bottom:1px solid #cccccc; }}
.footer {{ font-size:13px; color:#aaaaaa; margin-top:32px; padding-top:16px; border-top:1px solid #eeeeee; }}
@media (max-width:600px) {{
  .wrap {{ padding:20px 16px; }}
  .hdr-title {{ font-size:18px; }}
  .hdr-date {{ font-size:12px; }}
  .section-label {{ font-size:11px; margin:20px 0 8px; }}
  .item {{ font-size:13px; line-height:1.45; }}
  .item-src {{ font-size:11px; }}
  .num-row {{ font-size:13px; }}
  .num-ticker {{ font-size:11px; }}
  .footer {{ font-size:12px; }}
}}
</style>
</head>
<body>
<div class="wrap">

  <div class="hdr-title">Hydra Brief</div>
  <div class="hdr-date">{short_date}</div>
  <hr class="divider">

  {lead_html}
  {news_html}
  {diary_html}
  {numbers_html}

  <div class="footer" style="text-align:center;">
    Hydra Brief is a curated summary of important industry news of the day, provided by <a href="https://hydra-advisory.com" style="color:#aaaaaa;">Hydra Advisory</a>.<br>
    <a href="*|UNSUB|*" style="color:#aaaaaa;">Unsubscribe</a>
  </div>

</div>
</body>
</html>"""


# ── Helpers ───────────────────────────────────────────────────────────────

_SOURCE_ABBR = {
    "business of fashion": "BoF",
    "bof": "BoF",
    "wwd": "WWD",
    "vogue business": "VB",
    "pambianco news": "PAMB",
    "pambianco": "PAMB",
    "mff — moda finanza fashion": "MFF",
    "mffashion": "MFF",
    "il sole 24 ore - moda": "Il Sole",
    "il sole 24 ore": "Il Sole",
    "reuters": "Reuters",
    "financial times — luxury": "FT",
    "financial times": "FT",
    "south china morning post": "SCMP",
    "nikkei asia": "Nikkei",
    "fashion network": "FashNet",
    "luxury society": "LuxSoc",
    "lvmh newsroom": "LVMH",
    "kering press": "Kering",
    "richemont news": "Richemont",
    "brand announcement": "Brand",
}

def _abbr(name: str) -> str:
    return _SOURCE_ABBR.get(name.lower(), name)


def _source_link(text: str, href: str) -> str:
    return f'<a href="{href}" class="src-link">{_abbr(text)}</a>'


def _inline_src(primary: str, link: str, also: list) -> str:
    if not primary:
        return ""
    src = f'<a href="{link}" class="src-link">{_abbr(primary)}</a>' if link else f'<span class="item-src">{_abbr(primary)}</span>'
    also_part = "/" + "/".join(_abbr(_esc(s)) for s in also[:2]) if also else ""
    return f'<span class="item-src" style="white-space:nowrap;padding-left:5px;">{src}{also_part}</span>'



def _also_slash(names: list) -> str:
    if not names:
        return ""
    return "/" + "/".join(_esc(s) for s in names[:3])


_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_diary_dates(dates: str):
    s = dates.strip().replace("–", "-").replace("—", "-")

    m = re.match(r"^(\d{1,2})(?:\s*-\s*(\d{1,2}))?\s+([A-Za-z]{3,})\s+(\d{4})$", s)
    if m:
        d1, d2, mon, year = m.groups()
        month = _MONTHS.get(mon[:3].lower())
        if not month:
            return None
        try:
            start = datetime(int(year), month, int(d1)).date()
            end = datetime(int(year), month, int(d2 or d1)).date()
            return start, end
        except ValueError:
            return None

    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3,})\s*-\s*(\d{1,2})\s+([A-Za-z]{3,}),?\s+(\d{4})$", s)
    if m:
        d1, mon1, d2, mon2, year = m.groups()
        month1 = _MONTHS.get(mon1[:3].lower())
        month2 = _MONTHS.get(mon2[:3].lower())
        if not month1 or not month2:
            return None
        try:
            start = datetime(int(year), month1, int(d1)).date()
            end = datetime(int(year), month2, int(d2)).date()
            return start, end
        except ValueError:
            return None

    return None


def _calendar_links(event: str, desc: str, dates: str) -> dict:
    parsed = _parse_diary_dates(dates)
    if not parsed:
        return {}
    start, end = parsed
    gcal_end = end + timedelta(days=1)

    google = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(event)}&dates={start.strftime('%Y%m%d')}/{gcal_end.strftime('%Y%m%d')}"
        f"&details={quote(desc)}"
    )
    outlook = (
        "https://outlook.live.com/calendar/0/deeplink/compose?path=%2Fcalendar%2Faction%2Fcompose&rru=addevent"
        f"&subject={quote(event)}&startdt={start.strftime('%Y-%m-%d')}&enddt={gcal_end.strftime('%Y-%m-%d')}"
        f"&body={quote(desc)}&allday=true"
    )
    base_url = os.environ.get("ICS_BASE_URL", "").rstrip("/")
    apple = (
        f"{base_url}/ics?event={quote(event)}"
        f"&start={start.strftime('%Y%m%d')}&end={gcal_end.strftime('%Y%m%d')}"
        f"&desc={quote(desc)}"
    ) if base_url else None

    return {"google": google, "outlook": outlook, "apple": apple}


# ── Section builders ──────────────────────────────────────────────────────

def _build_lead(items: list) -> str:
    if not items:
        return ""
    html = '<div class="section-label">What You Should Know Today</div>'
    for item in items[:3]:
        text    = _esc(_truncate_chars(item.get("text", ""), 40))
        link    = item.get("link", "")
        primary = _esc(item.get("primary_source", ""))
        also    = item.get("also", [])

        title_html = f'<a href="{link}" style="color:{IN};text-decoration:none;">{text}</a>' if link else text
        src_html = _inline_src(primary, link, also)

        html += f'<div class="item">&bull;&nbsp;{title_html}{src_html}</div>'
    html += f'<hr class="divider-thin">'
    return html


def _build_news(items: list) -> str:
    if not items:
        return ""
    html = '<div class="section-label">News</div>'
    for item in items[:10]:
        headline = _esc(_truncate_chars(item.get("headline", ""), 40))
        link     = item.get("link", "")
        primary  = _esc(item.get("primary_source", ""))
        also     = item.get("also", [])

        title_html = f'<a href="{link}" style="color:{IN};text-decoration:none;">{headline}</a>' if link else headline
        src_html = _inline_src(primary, link, also)

        html += f'<div class="item">&bull;&nbsp;{title_html}{src_html}</div>'
    html += f'<hr class="divider-thin">'
    return html


def _build_diary(items: list) -> str:
    if not items:
        return ""
    html = '<div class="section-label">Sector Diary</div>'
    for item in items[:4]:
        event = _esc(item.get("event", ""))
        desc  = _esc(item.get("description", ""))
        dates = _esc(item.get("dates", ""))
        link  = item.get("link", "")
        cal   = _calendar_links(item.get("event", ""), item.get("description", ""), item.get("dates", ""))

        event_html = f'<a href="{link}" style="color:{IN};text-decoration:none;">{event}</a>' if link else event

        cal_parts = []
        if cal.get("google"):
            cal_parts.append(f'<a href="{cal["google"]}" data-mc-no-track="true" class="cal-link">Google</a>')
        if cal.get("outlook"):
            cal_parts.append(f'<a href="{cal["outlook"]}" data-mc-no-track="true" class="cal-link">Outlook</a>')
        if cal.get("apple"):
            cal_parts.append(f'<a href="{cal["apple"]}" data-mc-no-track="true" class="cal-link">Apple</a>')
        cal_html = f' &nbsp;<span style="font-size:12px;color:{MU};">{" / ".join(cal_parts)}</span>' if cal_parts else ""

        html += (
            f'<div class="item">'
            f'{event_html}'
            f'<div class="item-src">{desc}</div>'
            f'<div class="item-src"><a href="#" style="color:{MU};text-decoration:none;pointer-events:none;cursor:default;">{dates}</a>{cal_html}</div>'
            f'</div>'
        )
    html += f'<hr class="divider-thin">'
    return html


def _build_numbers(items: list, timestamp: str) -> str:
    if not items:
        return ""
    ts_label = f'<a href="#" style="color:{MU};text-decoration:none;pointer-events:none;cursor:default;">{_esc(timestamp)} · vs. previous day close</a>'
    ts_span = f'<span style="font-size:12px;font-weight:400;letter-spacing:0;text-transform:none;color:{MU};">{ts_label}</span>'
    html = f'<div class="section-label">Important Numbers &nbsp;{ts_span}</div>'
    for item in items[:6]:
        name      = _esc(item.get("name", ""))
        ticker    = _esc(item.get("ticker", ""))
        price     = _esc(item.get("price", ""))
        change    = _esc(item.get("change", ""))
        direction = item.get("direction", "flat")
        context   = _esc(_truncate_words(item.get("context", ""), 6))
        colour    = GR if direction == "up" else (RD if direction == "down" else MU)

        html += (
            f'<div style="padding:7px 0;border-bottom:1px solid #eeeeee;">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="font-size:17px;color:{IN};">{name} <span class="num-ticker">&middot; {ticker}</span></td>'
            f'<td align="right" style="font-size:17px;color:{IN};white-space:nowrap;">{price} <span style="color:{colour};font-size:14px;">{change}</span></td>'
            f'</tr></table>'
            f'<div style="font-size:12px;color:{MU};margin-top:2px;">{context}</div>'
            f'</div>'
        )
    return html


def _truncate_words(text: str, max_words: int) -> str:
    words = str(text).split()
    if len(words) <= max_words:
        return str(text)
    return " ".join(words[:max_words]).rstrip(".,;:")


def _truncate_chars(text: str, max_chars: int) -> str:
    s = str(text).strip()
    if len(s) <= max_chars:
        return s
    # Cut at last word boundary within limit
    cut = s[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:")
    return cut


def _esc(text: str) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
