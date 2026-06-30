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
import re
from datetime import datetime, timedelta
from urllib.parse import quote

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
LG = "#f7f6f4"   # light grey row highlight
JOST = "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;"

_RESPONSIVE_STYLE = """<style>
@media screen and (max-width: 600px) {
  .hdr-title    { font-size:38px !important; }
  .hdr-date     { font-size:26px !important; }
  .eyebrow-lbl  { font-size:25px !important; }
  .eyebrow-rgt  { font-size:21px !important; }
  .lead-title   { font-size:30px !important; }
  .lead-suffix  { font-size:26px !important; }
  .news-title   { font-size:30px !important; }
  .news-suffix  { font-size:26px !important; }
  .diary-event  { font-size:30px !important; }
  .diary-desc   { font-size:27px !important; }
  .diary-date   { font-size:26px !important; }
  .numbers-name { font-size:30px !important; }
  .numbers-tick { font-size:26px !important; }
  .numbers-px   { font-size:26px !important; }
  .numbers-ctx  { font-size:27px !important; }
  .src-link     { font-size:26px !important; }
  .footer-txt   { font-size:22px !important; }
}
</style>"""


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
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<meta name="format-detection" content="telephone=no,date=no,address=no,email=no,url=no">
<title>Hydra Brief · {today}</title>
{_RESPONSIVE_STYLE}
</head>
<body style="margin:0;padding:0;background:{BG};{JOST}color:{IN};font-size:18px;line-height:1.5;">
{_RESPONSIVE_STYLE}

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="background:{BG};">
<tr><td align="center" style="padding:20px 12px 44px;">

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" align="center" style="max-width:600px;background:#ffffff;">
<tr><td style="padding:0 0 6px;">

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-bottom:2px solid {B};">
    <tr>
      <td class="hdr-title" style="padding:16px 20px 15px;font-weight:500;font-size:20px;color:{B};letter-spacing:.1em;text-transform:uppercase;">Hydra Brief</td>
      <td align="right" class="hdr-date" style="padding:16px 20px 15px;font-size:15px;color:{MU};white-space:nowrap;">{short_date}</td>
    </tr>
  </table>

  {lead_html}
  {news_html}
  {diary_html}
  {numbers_html}

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid {RU};margin-top:8px;">
    <tr><td class="footer-txt" style="padding:10px 20px 0;font-size:13px;color:{A0};">
      <a href="https://hydra-advisory.com" style="color:{MU};">hydra-advisory.com</a> ·
      <a href="*|UNSUB|*" style="color:{MU};">Unsubscribe</a> · Hydra Advisory
    </td></tr>
  </table>

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
            f'<td class="eyebrow-lbl" style="font-size:14px;font-weight:500;letter-spacing:.16em;text-transform:uppercase;color:{CR} !important;">{label}</td>'
            f'<td align="right" class="eyebrow-rgt" style="font-size:12px;font-weight:400;letter-spacing:.05em;text-transform:none;color:{CR} !important;background:{B} !important;white-space:nowrap;">{right_label}</td>'
            f'</tr></table>'
        )
    else:
        inner = label
    return (
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        f'<tr><td class="eyebrow-lbl" style="background:{B};padding:6px 20px;font-size:14px;font-weight:500;'
        f'letter-spacing:.16em;text-transform:uppercase;color:{CR} !important;">{inner}</td></tr></table>'
    )


def _section(label: str, rows_html: str, right_label: str = "", side_padding: int = 20) -> str:
    return (
        _eyebrow(label, right_label)
        + f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        f'<tr><td style="padding:8px {side_padding}px 0;">{rows_html}</td></tr></table>'
    )


def _row_table(inner: str) -> str:
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td>{inner}</td></tr></table>'


def _source_link(text: str, href: str) -> str:
    return (
        f'<a href="{href}" class="src-link" style="font-size:14px;color:{B};'
        f'text-decoration:none;border-bottom:1px solid {G};white-space:nowrap;">{text}</a>'
    )


def _also_slash(names: list) -> str:
    if not names:
        return ""
    joined = "/".join(_esc(s) for s in names[:3])
    return f'/{joined}'


_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_diary_dates(dates: str):
    """Best-effort parse of a free-text diary date range into (start, end) dates.
    Returns None if the format isn't recognised (e.g. "Est. late Jun 2026")."""
    s = dates.strip().replace("–", "-").replace("—", "-")

    # "D[-D] Mon YYYY" e.g. "17-22 Jun 2026"
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

    # "D Mon - D Mon, YYYY" e.g. "25 Sep - 3 Oct 2026"
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
    gcal_end = end + timedelta(days=1)  # all-day end date is exclusive for Google/Outlook

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
    ics_content = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Hydra Advisory//Hydra Brief//EN",
        "BEGIN:VEVENT",
        f"DTSTART:{start.strftime('%Y%m%d')}",
        f"DTEND:{gcal_end.strftime('%Y%m%d')}",
        f"SUMMARY:{event}",
        f"DESCRIPTION:{desc}",
        "END:VEVENT", "END:VCALENDAR",
    ])
    apple = "data:text/calendar;charset=utf8," + quote(ics_content)

    return {"google": google, "outlook": outlook, "apple": apple}


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
        also_html = _also_slash(also) if also else ""
        suffix = f' <span class="lead-suffix" style="font-size:14px;font-weight:400;color:{MU};">{src_html}{also_html}</span>' if src_html else ""

        pad = "0 0 10px" if i == len(sliced) - 1 else "0 0 7px"
        rows += _row_table(
            f'<div class="lead-title" style="padding:{pad};font-size:16px;font-weight:400;line-height:1.35;color:{IN};'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'&bull;&nbsp; {title_html}{suffix}</div>'
        )
    return _section("What You Should Know Today", rows)


def _build_news(items: list) -> str:
    if not items:
        return ""
    rows = ""
    sliced = items[:10]
    n = len(sliced)
    for i, item in enumerate(sliced):
        headline = _esc(_truncate_words(item.get("headline", ""), 8))
        link     = item.get("link", "")
        primary  = _esc(item.get("primary_source", ""))
        also     = item.get("also", [])

        title_html = f'<a href="{link}" style="color:{IN};text-decoration:none;">{headline}</a>' if link else headline
        src = _source_link(primary, link) if link else primary
        also_html = _also_slash(also) if also else ""
        src_html = f' <span class="news-suffix" style="font-size:14px;font-weight:400;color:{MU};">{src}{also_html}</span>' if src else ""
        bg = f'background:{LG};' if i % 2 == 0 else ""
        pad_top = "10px" if i == 0 else "8px"
        pad_bottom = "12px" if i == n - 1 else "8px"

        rows += (
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td style="{bg}padding:{pad_top} 20px {pad_bottom};">'
            f'<div class="news-title" style="font-size:16px;font-weight:400;line-height:1.35;color:{IN};'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'&bull;&nbsp; {title_html}{src_html}</div>'
            f'</td></tr></table>'
        )
    return _eyebrow("News") + rows


def _build_diary(items: list) -> str:
    if not items:
        return ""
    rows = ""
    sliced = items[:4]
    for i, item in enumerate(sliced):
        event = _esc(item.get("event", ""))
        desc  = _esc(item.get("description", ""))
        dates = _esc(item.get("dates", ""))
        link  = item.get("link", "")
        cal_links = _calendar_links(item.get("event", ""), item.get("description", ""), item.get("dates", ""))

        event_html = f'<a href="{link}" style="color:inherit;text-decoration:none;">{event}</a>' if link else event
        if cal_links:
            dates_html = (
                f'{dates}<br>'
                f'<a href="{cal_links["google"]}" style="color:inherit;text-decoration:underline;">Google</a> / '
                f'<a href="{cal_links["outlook"]}" style="color:inherit;text-decoration:underline;">Outlook</a> / '
                f'<a href="{cal_links["apple"]}" style="color:inherit;text-decoration:underline;">Apple</a>'
            )
        else:
            dates_html = dates

        pad = "0 0 10px" if i == len(sliced) - 1 else "0 0 7px"
        rows += (
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="diary-event" style="padding:{pad};font-size:16px;line-height:1.35;">'
            f'<div style="font-weight:500;">{event_html}</div>'
            f'<div class="diary-desc" style="color:{MU};font-size:15px;">{desc}</div>'
            f'</td>'
            f'<td align="right" valign="top" class="diary-date" style="padding:{pad};font-size:14px;color:{B};white-space:nowrap;">{dates_html}</td>'
            f'</tr></table>'
        )
    return _section("Sector Diary", rows)


def _build_numbers(items: list, timestamp: str) -> str:
    if not items:
        return ""
    sliced = items[:6]
    rows = ""
    n = len(sliced)
    for i, item in enumerate(sliced):
        name      = _esc(item.get("name", ""))
        ticker    = _esc(item.get("ticker", ""))
        price     = _esc(item.get("price", ""))
        change    = _esc(item.get("change", ""))
        direction = item.get("direction", "flat")
        context   = _esc(_truncate_words(item.get("context", ""), 5))
        colour    = GR if direction == "up" else (RD if direction == "down" else MU)
        bg = f'background:{LG};' if i % 2 == 0 else ""
        pad_top = "10px" if i == 0 else "8px"
        pad_bottom = "12px" if i == n - 1 else "8px"

        rows += (
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
            f'<tr><td style="{bg}padding:{pad_top} 20px {pad_bottom};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="numbers-name" style="font-size:16px;font-weight:400;color:{IN};">{name} <span class="numbers-tick" style="color:{MU};font-size:14px;font-weight:400;">&middot; {ticker}</span></td>'
            f'<td align="right" class="numbers-px" style="font-size:14px;color:{B};white-space:nowrap;font-weight:400;">{price} <span style="color:{colour};">{change}</span></td>'
            f'</tr></table>'
            f'<div class="numbers-ctx" style="font-size:15px;color:{MU};line-height:1.3;margin-top:2px;">{context}</div>'
            f'</td></tr></table>'
        )

    ts_html = f'<span style="color:{CR};text-decoration:none !important;font-style:normal;">{_esc(timestamp)}</span>'
    return _eyebrow("Important Numbers", right_label=ts_html) + rows


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
