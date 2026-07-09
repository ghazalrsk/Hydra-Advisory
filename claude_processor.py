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


def process_with_claude(articles: list[dict], stocks: list[dict], today: str, numbers_timestamp: str = "", is_monday: bool = False) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = _build_prompt(articles, stocks, today, is_monday)
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


def _build_prompt(articles: list[dict], stocks: list[dict], today: str, is_monday: bool = False) -> str:
    articles_text = json.dumps(articles, ensure_ascii=False, indent=2)
    stocks_text   = json.dumps(stocks,   ensure_ascii=False, indent=2)
    diary_text    = json.dumps(SECTOR_DIARY, ensure_ascii=False, indent=2)

    monday_note = """
════════════════════════════════════════
MONDAY EDITION — SPECIAL RULES
════════════════════════════════════════

Today is Monday. The article pool covers the last 72 hours (Friday evening through Sunday).
"What You Should Know Today" MUST feature only stories that broke on Saturday or Sunday.
Do NOT surface any story that would have appeared in Friday's edition.
Friday holdovers — stories published before Saturday 00:00 — must be excluded from lead_items entirely.
News items may include Friday stories only if they represent a genuinely new development (e.g. a follow-up, a confirmation, or new data published over the weekend on a Friday story).
""" if is_monday else ""

    return f"""You are the editor of Hydra Brief, a daily intelligence digest for luxury industry professionals — executives, investors, analysts, and M&A advisors at the senior level.

Today's date: {today}

Return a single JSON object. No prose, no explanation, no markdown fences. Raw JSON only.
{monday_note}

════════════════════════════════════════
SECTION A — SOURCE TIERS & ATTRIBUTION
════════════════════════════════════════

Every article in the pool carries a "tier" field. Attribution rules are strict:

TIER 1 — Reuters, Financial Times, Il Sole 24 Ore
  → Always the primary_source, regardless of who broke the story first.
  → If a Tier 1 source covered it, it is the primary. No exceptions.

TIER 2 — Business of Fashion, WWD, Pambianco, MFF, SCMP, Nikkei Asia
  → Primary only when NO Tier 1 source covers the same story.
  → Among Tier 2 sources covering the same story, prefer BoF for brand/creative news,
    WWD for US/retail news, Pambianco/MFF for Italian-only stories, SCMP/Nikkei for Asia.

TIER 3 — Vogue Business, Fashion Network, Luxury Society, brand newsrooms (LVMH, Kering, Richemont)
  → NEVER the primary_source. Place in "also" list only.
  → Brand newsrooms: include in "also" only if no editorial source covered the story,
    and label as "Brand announcement" in that edge case only.

Attribution format in output:
  primary_source: "Reuters"
  also: ["BoF", "WWD"]
Maximum 2 sources in the "also" list. Tier 3 sources may appear in "also" but count toward the limit.
This attribution is required for BOTH "lead_items" and "news" — every item must carry primary_source.

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

INDUSTRY PRIORITY — apply this before anything else:
Hydra Brief serves a luxury advisory boutique. The digest must stay within the luxury, high-end fashion, and premium goods industry first. Fill all available slots with stories from this universe before considering anything outside it.

Priority order for story selection — work through these in order until all slots are filled:
  1. Luxury, fashion, high-end goods — always first. Stories about the brand universe, luxury M&A, luxury retail, luxury market data, watches, jewellery, leather goods, couture, premium beauty.
  2. Broader financial/macro news with a direct luxury demand implication (e.g. China tariffs, consumer confidence in key luxury markets, currency moves affecting luxury pricing).
  3. Adjacent business news relevant to luxury executives — retail, consumer goods, hospitality, art market, real estate in key luxury cities, high-end travel.
  4. General business, economic, or geopolitical news that any senior executive would want to know — use this tier to fill any remaining slots if tiers 1–3 are exhausted.

CRITICAL: All slots must always be filled. Never leave a slot empty because "no qualifying luxury story exists." Work through the priority tiers until every slot is filled. The email must always send.

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
- Geopolitical or defence news (missile tests, military deals, nuclear policy) — reject entirely unless there is an explicit, named luxury market impact

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

The STOCK DATA below is already the 6 biggest movers (highest absolute 24h % change) in the luxury sector — selected programmatically, not by you.
Return all 6, in the same order given, under "numbers". Do not add, drop, or reorder them.
For each stock, write a MAXIMUM 5-word fragment explaining WHY it moved (using the articles as context). No full sentence, no period needed — just the reason.
  CORRECT: "Gains tied to easing trade tensions"
  WRONG: "Shares rallied today amid broader luxury sector gains following the announcement of easing trade tensions between major markets"
If you cannot find a reason in the articles, write a brief 5-word-max factual note about the company's recent performance.

════════════════════════════════════════
SECTION F — WRITING RULES
════════════════════════════════════════

════════════════════════════════════════
HEADLINE WRITING RULES
════════════════════════════════════════

Every headline must obey ALL of the following without exception:

1. ONE LINE ON MOBILE — HARD LIMIT
   Every headline must fit on a single line on a mobile phone screen. Never wrap to a second line.
   Mobile screens are narrow. Keep headlines concise. If a headline feels long, shorten it.
   Never wrap to a second line under any circumstances.

2. COMPLETE ENGLISH SENTENCE — NO EXCEPTIONS
   Every headline must be a grammatically complete sentence in plain professional English.
   A reader must understand the full story from the headline alone: who did what, and what it means.

   GRAMMAR RULES — all mandatory:
   a) Never end on a preposition (amid, with, for, on, at, by, of, in, to, into, from, through, about).
      WRONG: "Kering cuts costs amid"  WRONG: "LVMH expands into"  WRONG: "Chanel plans for"
   b) Never end on a conjunction (and, but, or, while, as, since, although, despite, because).
      WRONG: "Gucci grows but"  WRONG: "Sales rise despite"  WRONG: "Brands expand while"
   c) Never end on an adjective or modifier without the noun it describes.
      WRONG: "De Beers backs natural"  WRONG: "Hermès reports strong"
   d) Never end on a possessive or article.
      WRONG: "Richemont raises its"  WRONG: "LVMH cuts the"
   e) Subject and verb must both be present. A headline is not a title or a label.
      WRONG: "Chanel couture season"  WRONG: "LVMH Q2 results"
      RIGHT: "Chanel opens couture season in Paris"  RIGHT: "LVMH reports Q2 sales rise"
   f) Verb tense: use simple present for current news ("Gucci names", "LVMH cuts", "Chanel opens").

   WRONG: "Tokopedia denies layoffs amid"  — ends on preposition ✗
   WRONG: "De Beers sale advances amid natural"  — ends on adjective without noun ✗
   WRONG: "Reda posts growth despite merino"  — ends on noun mid-clause ✗
   RIGHT: "Tokopedia denies layoffs amid restructuring"  ✓
   RIGHT: "De Beers nears sale, backs natural diamonds"  ✓
   RIGHT: "Reda grows H1 despite merino price rises"  ✓

3. NEVER PUT THE SOURCE IN THE HEADLINE
   The source tag (BoF, WWD, PAMB etc.) is added automatically after the headline.
   Never write the source name inside the headline text itself.
   WRONG: "Hermès plans couture show in Jan BoF"  — BoF is in the headline text. ✗
   RIGHT: "Hermès to debut couture show in January"  — clean headline, source added separately. ✓

4. IF IT FEELS TOO LONG, REWRITE — NEVER TRUNCATE
   If a headline is too long to fit on one mobile line, rephrase it using simpler or shorter
   words that preserve the full meaning. Never cut a sentence short to make it fit.

5. ABBREVIATIONS ARE FINE IF THEY MAKE SENSE IN CONTEXT
   "in Jan" is acceptable. "Jan" alone at the end of a sentence is not.
   Use brand abbreviations: LVMH, BoF, H1, Q1, CEO, M&A.
   Drop articles (a, an, the) to save space where natural.

Return exactly 10 news items (after lead_items are excluded, per SECTION C).
If the article pool contains fewer than 10 clearly luxury-relevant stories, include the next most relevant stories that have any connection to luxury demand, luxury consumers, or the business of fashion and premium goods — do not leave slots empty.

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
Each diary item must carry the "link" field copied exactly from the matching entry in the SECTOR DIARY list below.

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
    {{"text": "One-clause headline fact.", "link": "https://...", "primary_source": "Publication Name", "also": ["Other Source 1"]}},
    {{"text": "One-clause headline fact.", "link": "https://...", "primary_source": "Publication Name", "also": []}},
    {{"text": "One-clause headline fact.", "link": "https://...", "primary_source": "Publication Name", "also": []}}
  ],
  "numbers": [
    {{
      "name": "LVMH",
      "ticker": "MC.PA",
      "price": "€618.40",
      "change": "▲ +2.3%",
      "direction": "up",
      "context": "5-word-max reason for the move."
    }}
  ],
  "news": [
    {{
      "headline": "Full headline of the story, 8 words max.",
      "link": "https://...",
      "primary_source": "Publication Name",
      "also": ["Other Source 1", "Other Source 2"]
    }}
  ],
  "diary": [
    {{
      "event": "Event name · City",
      "description": "One-line description.",
      "dates": "Date range as exact dates only, e.g. '9–15 Jul 2026' or '22 Sep 2026'. Never use vague formats like 'Est. late Jun' — always use specific day and month numbers.",
      "link": "Copy the exact 'link' value for this event from the SECTOR DIARY list above."
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
            "diary": [],
            "numbers_timestamp": "",
        }
