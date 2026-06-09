"""
HYDRA SUMMARY — Email Builder
-------------------------------
Builds the HTML email using the Hydra Brief visual design.
"""

import logging

log = logging.getLogger("hydra-summary.builder")


def build_email_html(digest: dict, today: str) -> str:
    lead_html   = _build_lead(digest.get("lead_items", []))
    numbers_html = _build_numbers(digest.get("numbers", []))
    news_html   = _build_news(digest.get("news", []))
    roles_html  = _build_roles(digest.get("roles", []))
    diary_html  = _build_diary(digest.get("diary", []))

    # Format date as "Tue · 9 Jun 2026"
    from datetime import datetime
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{{
    --burgundy:#3D0C1F;
    --gold:#B8922A;
    --cream:#F4EFE7;
    --ink:#1f1f1f;
    --muted:#7a7a7a;
    --rule:#e2e2e2;
    --bg:#f4f2ef;
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{
    background:var(--bg);
    font-family:'Jost',sans-serif;color:var(--ink);
    font-size:14px;line-height:1.45;padding:20px 12px 44px;
  }}
  .sheet{{max-width:580px;margin:0 auto;background:#fff;padding:0 0 6px;}}
  header{{
    display:flex;justify-content:space-between;align-items:baseline;
    padding:14px 20px 13px;border-bottom:2px solid var(--burgundy);
  }}
  .name{{font-weight:600;font-size:15px;color:var(--burgundy);letter-spacing:.14em;text-transform:uppercase;}}
  .date{{font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);}}
  .sec{{padding:0 20px 12px;}}
  .eyebrow{{
    font-family:'DM Mono',monospace;font-size:10.5px;font-weight:500;letter-spacing:.18em;
    text-transform:uppercase;color:var(--cream);
    background:var(--burgundy);
    margin:0 -20px 10px;padding:6px 20px;
  }}
  .story{{padding:0 0 9px;}}
  .story:last-child{{padding-bottom:0;}}
  .story .t{{font-size:14px;font-weight:600;line-height:1.15;color:var(--ink);}}
  .story .d{{font-size:13px;color:#4a4a4a;line-height:1.32;margin-top:1px;}}
  .story .d a{{font-family:'DM Mono',monospace;font-size:10px;color:var(--burgundy);text-decoration:none;border-bottom:1px solid var(--gold);white-space:nowrap;}}
  .story .d .also{{font-family:'DM Mono',monospace;font-size:10px;color:#a0a0a0;}}
  .flow{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:0 0 5px;font-size:13.5px;line-height:1.32;}}
  .flow:last-child{{padding-bottom:0;}}
  .flow .lab{{color:var(--ink);}}
  .flow .val{{font-family:'DM Mono',monospace;font-size:13px;color:var(--burgundy);white-space:nowrap;font-weight:500;}}
  .up{{color:#2f7d4f;}}
  .down{{color:#9a3b3b;}}
  .job,.ev{{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:0 0 8px;font-size:13px;line-height:1.3;}}
  .job:last-child,.ev:last-child{{padding-bottom:0;}}
  .job .r,.ev .t{{font-weight:500;}}
  .job .c,.ev .w{{color:var(--muted);font-size:12px;}}
  .job .l{{font-family:'DM Mono',monospace;font-size:10px;color:#a0a0a0;white-space:nowrap;}}
  .ev .d{{font-family:'DM Mono',monospace;font-size:10px;color:var(--burgundy);white-space:nowrap;}}
  footer{{
    padding:13px 20px 0;border-top:1px solid var(--rule);margin-top:2px;
    font-family:'DM Mono',monospace;font-size:10px;color:#a0a0a0;
  }}
  footer a{{color:var(--muted);}}
</style>
</head>
<body>
  <div class="sheet">
    <header>
      <div class="name">Hydra Brief</div>
      <div class="date">{short_date}</div>
    </header>
    {lead_html}
    {numbers_html}
    {news_html}
    {roles_html}
    {diary_html}
    <footer>
      <a href="https://hydra-advisory.com">hydra-advisory.com</a> · <a href="*|UNSUB|*">Unsubscribe</a> · Hydra Advisory · Milan
    </footer>
  </div>
</body>
</html>"""


def _build_lead(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:3]:
        title = _esc(item.get("text", ""))
        link = item.get("link", "")
        source = _esc(item.get("source", ""))
        summary = _esc(item.get("summary", ""))
        link_html = f'<a href="{link}">{source}</a>' if link and source else (f'<a href="{link}">↗</a>' if link else "")
        rows += f'<div class="story"><div class="t">{title}</div><div class="d">{summary} {link_html}</div></div>\n'
    return f"""<div class="sec">
      <div class="eyebrow">What You Should Know Today</div>
      {rows}
    </div>"""


def _build_numbers(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:4]:
        name = _esc(item.get("name", ""))
        ticker = _esc(item.get("ticker", ""))
        price = _esc(item.get("price", ""))
        change = _esc(item.get("change", ""))
        direction = item.get("direction", "flat")
        context = _esc(item.get("context", ""))
        delta_class = "up" if direction == "up" else ("down" if direction == "down" else "")
        rows += f"""<div class="flow">
        <div class="lab">{name} <span style="color:var(--muted);font-size:12px">· {ticker}</span></div>
        <div class="val">{price} <span class="{delta_class}">{change}</span></div>
      </div>
      <div style="font-size:12px;color:#4a4a4a;padding:0 0 8px;line-height:1.3;">{context}</div>\n"""
    return f"""<div class="sec">
      <div class="eyebrow">Important Numbers</div>
      {rows}
    </div>"""


def _build_news(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:7]:
        headline = _esc(item.get("headline", ""))
        link = item.get("link", "")
        summary = _esc(item.get("summary", ""))
        primary = _esc(item.get("primary_source", ""))
        also = item.get("also", [])
        also_str = ""
        if also:
            also_names = ", ".join(_esc(s) for s in also[:3])
            also_str = f' <span class="also">· also {also_names}</span>'
        source_link = f'<a href="{link}">{primary}</a>' if link else primary
        rows += f'<div class="story"><div class="t">{headline}</div><div class="d">{summary} {source_link}{also_str}</div></div>\n'
    return f"""<div class="sec">
      <div class="eyebrow">News</div>
      {rows}
    </div>"""


def _build_roles(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:5]:
        title = _esc(item.get("title", ""))
        role_type = _esc(item.get("type", ""))
        house = _esc(item.get("house", ""))
        rows += f"""<div class="job"><div><div class="r">{title}</div><div class="c">{house} · {role_type}</div></div></div>\n"""
    return f"""<div class="sec">
      <div class="eyebrow">Roles</div>
      {rows}
    </div>"""


def _build_diary(items: list) -> str:
    if not items:
        return ""
    rows = ""
    for item in items[:4]:
        event = _esc(item.get("event", ""))
        desc = _esc(item.get("description", ""))
        dates = _esc(item.get("dates", ""))
        rows += f"""<div class="ev"><div><div class="t">{event}</div><div class="w">{desc}</div></div><div class="d">{dates}</div></div>\n"""
    return f"""<div class="sec">
      <div class="eyebrow">Sector Diary</div>
      {rows}
    </div>"""


def _esc(text: str) -> str:
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
