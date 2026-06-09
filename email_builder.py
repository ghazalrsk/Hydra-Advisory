"""
HYDRA SUMMARY — Email Builder
-------------------------------
Takes Claude's structured digest dict and builds the final HTML email.
Uses the Hydra Summary v8 visual template — the approved design.
"""

import logging

log = logging.getLogger("hydra-summary.builder")


def build_email_html(digest: dict, today: str) -> str:
    """
    Assembles all sections into the complete HTML email string.
    Returns a full HTML document ready to send.
    """

    lead_html    = _build_lead(digest.get("lead_items", []))
    numbers_html = _build_numbers(digest.get("numbers", []))
    news_html    = _build_news(digest.get("news", []))
    roles_html   = _build_roles(digest.get("roles", []))
    diary_html   = _build_diary(digest.get("diary", []))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hydra Summary · {today}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=DM+Mono:wght@300;400&family=Jost:wght@200;300;400&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink:  #1A1A1A;
    --mute: #666;
    --rule: #DEDAD5;
    --gold: #8A5A10;
    --bg:   #FAFAF8;
    --pos:  #1A5E3A;
    --neg:  #8A2020;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: var(--bg);
    color: var(--ink);
    font-family: 'Jost', sans-serif;
    font-weight: 300;
    font-size: 13px;
    line-height: 1.5;
    max-width: 660px;
    margin: 0 auto;
    padding: 48px 32px 64px;
  }}
  /* Header */
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding-bottom: 16px;
    border-bottom: 1.5px solid var(--ink);
    margin-bottom: 32px;
  }}
  .header-brand {{
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink);
  }}
  .header-date {{
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 300;
    letter-spacing: 0.08em;
    color: var(--mute);
  }}
  /* Section label */
  .section-label {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 400;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 11px;
  }}
  .section {{
    padding-bottom: 24px;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--rule);
  }}
  .section:last-of-type {{ border-bottom: none; }}
  /* Lead items */
  .glance-item {{
    display: flex;
    gap: 12px;
    align-items: baseline;
    margin-bottom: 8px;
    line-height: 1.4;
  }}
  .glance-item:last-child {{ margin-bottom: 0; }}
  .glance-num {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: var(--gold);
    letter-spacing: 0.05em;
    flex-shrink: 0;
    padding-top: 1px;
  }}
  .glance-text {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 15.5px;
    font-weight: 400;
    line-height: 1.35;
  }}
  .glance-text a {{
    color: var(--ink);
    text-decoration: none;
    border-bottom: 1px solid var(--rule);
  }}
  /* Numbers grid */
  .numbers-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
  }}
  .number-item {{
    padding: 10px 0;
    border-bottom: 1px solid var(--rule);
  }}
  .number-item:nth-child(odd) {{ padding-right: 20px; border-right: 1px solid var(--rule); }}
  .number-item:nth-child(even) {{ padding-left: 20px; }}
  .number-item:nth-last-child(-n+2) {{ border-bottom: none; }}
  .number-name {{
    font-family: 'DM Mono', monospace;
    font-size: 9.5px;
    letter-spacing: 0.08em;
    color: var(--mute);
    text-transform: uppercase;
    margin-bottom: 3px;
  }}
  .number-value {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 500;
    line-height: 1;
    color: var(--ink);
    margin-bottom: 4px;
  }}
  .number-delta {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    margin-right: 6px;
  }}
  .delta-up   {{ color: var(--pos); }}
  .delta-down {{ color: var(--neg); }}
  .delta-flat {{ color: var(--mute); }}
  .number-context {{
    font-size: 11px;
    color: var(--mute);
    line-height: 1.4;
  }}
  /* News items */
  .news-item {{
    padding: 10px 0;
    border-bottom: 1px solid var(--rule);
  }}
  .news-item:first-child {{ padding-top: 0; }}
  .news-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .news-headline {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 14.5px;
    font-weight: 500;
    line-height: 1.3;
    margin-bottom: 3px;
  }}
  .news-headline a {{
    color: var(--ink);
    text-decoration: none;
  }}
  .news-summary {{
    font-size: 12px;
    color: var(--mute);
    line-height: 1.45;
    margin-bottom: 4px;
  }}
  .news-sources {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 300;
    color: #aaa;
    letter-spacing: 0.04em;
  }}
  .news-sources span {{ color: var(--mute); font-weight: 400; }}
  /* Roles */
  .role-item {{
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
    align-items: baseline;
    padding: 8px 0;
    border-bottom: 1px solid var(--rule);
  }}
  .role-item:first-child {{ padding-top: 0; }}
  .role-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .role-name {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.3;
  }}
  .role-name em {{
    font-style: normal;
    color: var(--mute);
    font-size: 13px;
  }}
  .role-house {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 400;
    letter-spacing: 0.06em;
    color: var(--gold);
    white-space: nowrap;
    text-align: right;
  }}
  /* Diary */
  .diary-item {{
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
    align-items: baseline;
    padding: 8px 0;
    border-bottom: 1px solid var(--rule);
  }}
  .diary-item:first-child {{ padding-top: 0; }}
  .diary-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .diary-event {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 14px;
    font-weight: 400;
  }}
  .diary-event em {{
    display: block;
    font-style: normal;
    font-size: 11px;
    color: var(--mute);
    margin-top: 1px;
  }}
  .diary-date {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 300;
    color: var(--mute);
    white-space: nowrap;
    text-align: right;
  }}
  /* Footer */
  .footer {{
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid var(--rule);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .footer-brand {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--mute);
  }}
  .footer-links {{ display: flex; gap: 16px; }}
  .footer-links a {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.08em;
    color: var(--mute);
    text-decoration: none;
    text-transform: uppercase;
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-brand">Hydra Summary</div>
  <div class="header-date">{today}</div>
</div>

{lead_html}
{numbers_html}
{news_html}
{roles_html}
{diary_html}

<div class="footer">
  <div class="footer-brand">Hydra Advisory · Milan</div>
  <div class="footer-links">
    <a href="https://hydra-advisory.com/signal">Signal</a>
    <a href="https://hydra-advisory.com/dossier">Dossier</a>
    <a href="*|UNSUB|*">Unsubscribe</a>
  </div>
</div>

</body>
</html>"""

    return html


# ── Section builders ──────────────────────────────────────────────────────

def _build_lead(items: list) -> str:
    if not items:
        return ""

    rows = ""
    for i, item in enumerate(items[:3], 1):
        text = _esc(item.get("text", ""))
        link = item.get("link", "")
        if link:
            text = f'<a href="{link}">{text}</a>'
        rows += f"""
    <div class="glance-item">
      <span class="glance-num">0{i}</span>
      <span class="glance-text">{text}</span>
    </div>"""

    return f"""<div class="section">
  <div class="section-label">What You Should Know Today</div>
  {rows}
</div>"""


def _build_numbers(items: list) -> str:
    if not items:
        return ""

    rows = ""
    for item in items[:4]:
        direction = item.get("direction", "flat")
        delta_class = f"delta-{direction}"
        change = _esc(item.get("change", ""))
        rows += f"""
    <div class="number-item">
      <div class="number-name">{_esc(item.get('name', ''))} · {_esc(item.get('ticker', ''))}</div>
      <div class="number-value">{_esc(item.get('price', ''))}</div>
      <span class="number-delta {delta_class}">{change}</span>
      <div class="number-context">{_esc(item.get('context', ''))}</div>
    </div>"""

    return f"""<div class="section">
  <div class="section-label">Important Numbers</div>
  <div class="numbers-grid">
    {rows}
  </div>
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
            also_str = f" · also {also_names}"

        rows += f"""
  <div class="news-item">
    <div class="news-headline"><a href="{link}">{headline}</a></div>
    <div class="news-summary">{summary}</div>
    <div class="news-sources">via <span>{primary}</span>{also_str}</div>
  </div>"""

    return f"""<div class="section">
  <div class="section-label">News</div>
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
        rows += f"""
  <div class="role-item">
    <div class="role-name">{title} <em>· {role_type}</em></div>
    <div class="role-house">{house}</div>
  </div>"""

    return f"""<div class="section">
  <div class="section-label">Roles</div>
  {rows}
</div>"""


def _build_diary(items: list) -> str:
    if not items:
        return ""

    rows = ""
    for item in items[:4]:
        event = _esc(item.get("event", ""))
        desc  = _esc(item.get("description", ""))
        dates = _esc(item.get("dates", ""))
        rows += f"""
  <div class="diary-item">
    <div class="diary-event">
      {event}
      <em>{desc}</em>
    </div>
    <div class="diary-date">{dates}</div>
  </div>"""

    return f"""<div class="section">
  <div class="section-label">Sector Diary</div>
  {rows}
</div>"""


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
