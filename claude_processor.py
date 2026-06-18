"""
HYDRA SUMMARY — Claude Processor
----------------------------------
Sends all collected articles to the Anthropic Claude API.
Claude deduplicates, selects, summarises, and returns structured JSON.
"""

import os
import json
import re
import logging
import anthropic
from sources import SECTOR_DIARY

log = logging.getLogger("hydra-summary.claude")


def process_with_claude(articles: list[dict], stocks: list[dict], today: str, numbers_timestamp: str = "") -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = _build_prompt(articles, stocks, today)
    log.info(f"  Sending {len(articles)} articles to Claude...")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text
    result = _parse_response(raw)
    result["numbers_timestamp"] = numbers_timestamp
    return result


def _build_prompt(articles: list[dict], stocks: list[dict], today: str) -> str:
    articles_text = json.dumps(articles, ensure_ascii=False, indent=2)
    stocks_text   = json.dumps(stocks,   ensure_ascii=False, indent=2)
    diary_text    = json.dumps(SECTOR_DIARY, ensure_ascii=False, indent=2)

    return f"""You are the editor of Hydra Brief, a daily intelligence digest for luxury industry professionals — executives, investors, analysts, and M&A advisors at the senior level.

Today's date: {today}

Return a single JSON object. No prose, no explanation, no markdown fences. Raw JSON only.

════════════════════════════════════════
SECTION A — SOURCE PRIORITY
════════════════════════════════════════

When multiple sources cover the same story, choose the primary source in this order:
1. Reuters / Bloomberg / Financial Times — for financial, earnings, M&A, tariff news
2. Business of Fashion — for creative direction, brand strategy, CD appointments
3. Pambianco / MFF — for Italian market news (use if they broke it first)
4. WWD — for US market, retail, wholesale trade news
5. Vogue Business — for digital, sustainability, consumer strategy
6. If the source that broke the story first is identifiable, always use that one regardless of tier

Attribution format in output:
  primary_source: "BoF"
  also: ["WWD", "Pambianco"]
Maximum 3 sources in the "also" list.
Brand press releases: use only if no editorial coverage exists. Label as "Brand announcement".

════════════════════════════════════════
SECTION B — STORY SELECTION
════════════════════════════════════════

ALWAYS INCLUDE:
- CEO / Creative Director appointment, departure, or confirmed search at any tracked maison
- Earnings, revenue updates, or full-year guidance changes for any listed luxury group
- M&A: acquisitions, mergers, minority stakes, divestments, PE entry/exit
- IPO announcements or cancellations in luxury sector
- Strategic restructuring, brand discontinuation, or group review announcements
- Major flagship openings (first in market, or 500sqm+)
- Wholesale exits or DTC pivots — distribution strategy changes
- EU regulations: Digital Product Passport, sustainability mandates
- Tariff changes (US, EU, China) affecting luxury goods
- China consumption policy with direct luxury demand implication
- Raw material moves: gold ±1.5%+, leather, cashmere, diamond supply signals
- Supply chain acquisitions: tanneries, textile mills, artisan ateliers
- Secondary market data: watch/handbag premium movements, major auction results

INCLUDE ONLY WITH EXPLICIT BUSINESS ANGLE:
- Collaboration / capsule collections — only if brand strategy context is explicit
- Campaign launches — only if they signal a strategic repositioning
- Sustainability initiatives — only if they include specific metrics or regulatory deadlines
- Consumer trend reports — only from Bain, McKinsey, Altagamma, BCG

ALWAYS REJECT:
- Celebrity wearing a brand (unless it is a new ambassador deal)
- Street style coverage of any kind
- Fashion week runway reviews with no business context
- Pure aesthetic or design commentary
- Social media viral moments with no commercial implication
- Personal lifestyle pieces about designers or executives
- Listicles: "top 10 bags", "best watches under €5,000"
- Beauty tutorials, styling guides, how-to content
- Travel content not linked to retail or brand expansion
- Brand content or advertorial disguised as editorial
- Sports sponsorships unless a new major strategic deal
- General tech or finance news with no luxury link

════════════════════════════════════════
SECTION C — DEDUPLICATION
════════════════════════════════════════

Every distinct event appears EXACTLY ONCE in the digest.
If BoF, WWD, Pambianco, and Vogue Business all cover the same appointment — it becomes one item with one primary source and an "also" line listing the others.
A story appearing in lead_items must NOT appear again in the news array.

════════════════════════════════════════
SECTION D — BRAND UNIVERSE
════════════════════════════════════════

News involving these brands is ALWAYS prioritised:

Tier 1 Groups: LVMH, Kering, Richemont, Hermès, Chanel
Independents: Moncler, Brunello Cucinelli, Zegna, Prada Group, Burberry, Ferragamo, Tod's Group
Key Maisons: Valentino, Armani Group, Dolce & Gabbana, Versace, Max Mara Group, OTB Group
Watches: Rolex, Patek Philippe, Audemars Piguet, Vacheron Constantin, Richard Mille, F.P. Journe, Omega, Breitling
Key Markets: China, Japan, Saudi Arabia, UAE, United States, South Korea

Stories about other brands are included only if there is a clear market-wide implication.

════════════════════════════════════════
SECTION E — NUMBERS
════════════════════════════════════════

The STOCK DATA below is already the 5 biggest movers (highest absolute 24h % change) in the luxury sector — selected programmatically, not by you.
Return all 5, in the same order given, under "numbers". Do not add, drop, or reorder them.
For each stock, write one sentence explaining WHY it moved (using the articles as context).
If you cannot find a reason in the articles, write a brief factual note about the company's recent performance.

════════════════════════════════════════
SECTION F — WRITING RULES
════════════════════════════════════════

Lead items: one clause only — the headline fact, no elaboration.
  CORRECT: "Gucci creative director search enters final round"
  WRONG: "Gucci is reportedly in the final stages of a lengthy search following the departure of..."

News summaries: exactly 1–2 sentences.
  Sentence 1: key fact — who, what, when/where
  Sentence 2: one-line implication or context
  CORRECT: "Richemont has named a single CEO to oversee all specialist watchmakers. The move consolidates six MDs under one P&L, signalling a margin-first restructuring."
  WRONG: "In an exciting development, Richemont has made a bold strategic move..."

BANNED WORDS — never use:
iconic · stunning · exciting · bold · groundbreaking · luxury powerhouse · giant · titan
Use "announces" not "unveils". Use "releases" not "drops".
Never use adjectives that are not measurable facts.

Brand name standards:
- "LVMH" — not "Louis Vuitton Moët Hennessy"
- "Brunello Cucinelli" — not "BC" or "the brand"
- "Richemont" — not "Compagnie Financière Richemont"
- "Kering" — not "the French group"

SECTOR DIARY:
From the diary list provided, select the 3–4 most immediately upcoming events closest to today's date.

════════════════════════════════════════
ARTICLES ({len(articles)} total):
════════════════════════════════════════
{articles_text}

════════════════════════════════════════
STOCK DATA:
════════════════════════════════════════
{stocks_text}

════════════════════════════════════════
SECTOR DIARY:
════════════════════════════════════════
{diary_text}

════════════════════════════════════════
RETURN THIS EXACT JSON — no other text:
════════════════════════════════════════

{{
  "lead_items": [
    {{"text": "One-clause headline fact.", "link": "https://..."}},
    {{"text": "One-clause headline fact.", "link": "https://..."}},
    {{"text": "One-clause headline fact.", "link": "https://..."}}
  ],
  "numbers": [
    {{
      "name": "LVMH",
      "ticker": "MC.PA",
      "price": "€618.40",
      "change": "▲ +2.3%",
      "direction": "up",
      "context": "One sentence explaining the move or relevant context."
    }}
  ],
  "news": [
    {{
      "headline": "Full headline of the story.",
      "summary": "1–2 sentence summary. Factual. Key development and one line of context.",
      "link": "https://...",
      "primary_source": "Publication Name",
      "also": ["Other Source 1", "Other Source 2"]
    }}
  ],
  "roles": [
    {{
      "title": "Role title",
      "type": "New appointment",
      "house": "Brand Name"
    }}
  ],
  "diary": [
    {{
      "event": "Event name · City",
      "description": "One-line description.",
      "dates": "Date range"
    }}
  ]
}}
"""


def _parse_response(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse Claude response as JSON: {e}")
        log.debug(f"Raw response:\n{raw[:500]}")
        return {
            "lead_items": [{"text": "Digest generation encountered an issue — please check logs.", "link": ""}],
            "numbers": [],
            "news": [],
            "roles": [],
            "diary": [],
            "numbers_timestamp": "",
        }
