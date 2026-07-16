"""
HYDRA SUMMARY — Claude Processor
----------------------------------
Sends all collected articles to the Anthropic Claude API.
Claude deduplicates, selects, summarises, and returns structured JSON.
"""

import os
import json
import re
import time
import logging
import anthropic
from sources import select_upcoming_events

log = logging.getLogger("hydra-summary.claude")


def process_with_claude(articles: list[dict], stocks: list[dict], today: str, numbers_timestamp: str = "", is_monday: bool = False) -> dict:
    from datetime import date
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    upcoming_events = select_upcoming_events(date.today(), n=3)
    prompt = _build_prompt(articles, stocks, today, is_monday, upcoming_events)
    log.info(f"  Sending {len(articles)} articles to Claude...")

    # Retry up to 4 times on overload (529)
    raw = None
    for attempt in range(4):
        try:
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=6000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text
            break
        except anthropic.OverloadedError:
            wait = 15 * (2 ** attempt)
            log.warning(f"  Claude overloaded (attempt {attempt+1}/4), retrying in {wait}s...")
            time.sleep(wait)

    if raw is None:
        raise RuntimeError("Claude API overloaded after 4 retries")

    result = _parse_response(raw)
    result["numbers_timestamp"] = numbers_timestamp

    # Override diary with pre-selected events directly — don't trust Claude to echo them correctly
    result["diary"] = upcoming_events

    # Hard-enforce per-source caps regardless of what Claude returned
    result = _enforce_source_caps(result)

    # Merge raw_change back from original stock data (Claude doesn't echo it)
    raw_change_map = {s["ticker"]: s.get("raw_change", 0) for s in stocks}
    for item in result.get("numbers", []):
        item["raw_change"] = raw_change_map.get(item.get("ticker", ""), 0)

    result = _validate_and_fix_headlines(client, result)
    return result


def _build_prompt(articles: list[dict], stocks: list[dict], today: str, is_monday: bool = False, upcoming_events: list = None) -> str:
    articles_text = json.dumps(articles, ensure_ascii=False, indent=2)
    stocks_text   = json.dumps(stocks,   ensure_ascii=False, indent=2)
    diary_text    = json.dumps(upcoming_events or [], ensure_ascii=False, indent=2)

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

TIER 1 — Reuters, Financial Times, Il Sole 24 Ore, Bloomberg Pursuits, Vogue Business, WWD
  → Always the primary_source, regardless of who broke the story first.
  → If a Tier 1 source covered it, it is the primary. No exceptions.

TIER 2 — Business of Fashion, Pambianco, MFF, Luxury Daily, The Drinks Business
  → Primary only when NO Tier 1 source covers the same story.
  → Among Tier 2 sources covering the same story, prefer BoF for brand/creative news,
    Pambianco/MFF for Italian-only stories, Luxury Daily for cross-sector luxury, The Drinks Business for wines & spirits.

TIER 3 — Fashion Network, Luxury Society, Skift, Dezeen, Fashion United, brand newsrooms (LVMH, Kering, Richemont)
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
  1. Luxury, fashion, high-end goods — always first. Stories about the brand universe, luxury M&A, luxury retail, luxury market data, watches, jewellery, leather goods, couture, premium beauty, wines & spirits, luxury hospitality, premium real estate.
  2. Broader financial/macro news with a DIRECT, NAMED luxury demand implication (e.g. China tariffs explicitly affecting luxury imports, consumer confidence data from Bain/McKinsey, currency moves explicitly affecting luxury pricing). The luxury link must be stated in the article — do not infer it.
  3. Adjacent premium business: high-end hospitality (5-star/ultra-luxury hotels), premium F&B (fine wine, spirits, Michelin), luxury real estate, art market, premium travel operators. Only if no more tier-1 stories exist.
  4. General business or macro news — MAXIMUM 1 item, only as absolute last resort if tiers 1–3 genuinely leave fewer than 10 stories. Stories about tech companies, Asian politics, defence, general consumer electronics, or mass-market retail do NOT qualify under any tier.

CRITICAL: All slots must always be filled. Never leave a slot empty because "no qualifying luxury story exists." Work through the priority tiers until every slot is filled. The email must always send.

SOURCE CAPS — hard limits on how many items per source may appear in the final email:
- The Drinks Business: maximum 1 item total across lead_items and news combined. Pick only the single most relevant story to luxury/premium F&B strategy or M&A — skip pure trade/retail wine news.

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
- General tech or finance news with no luxury link (Huawei, Samsung, Tesla, chip stocks, etc.)
- Geopolitical or defence news — reject entirely (missile tests, military deals, nuclear policy, territorial disputes, elections, sanctions unless they explicitly name a luxury brand or luxury market)
- Asian general news not involving a luxury brand or luxury market data (Chinese automakers, Korean tech, Japanese politics, Singapore courts, etc.)
- Mass-market retail, fast fashion, or consumer electronics
- Mass-market travel platforms or booking services (Omio, Booking.com, Expedia, Airbnb, etc.) — only luxury/ultra-premium travel operators qualify
- Legal/court cases not involving a luxury brand directly

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

The STOCK DATA below contains exactly 6 stocks: the 3 top gainers and 3 biggest decliners in the luxury sector — selected programmatically, not by you.
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

1. ONE LINE ON MOBILE — HARD CHARACTER LIMIT
   Every headline must be 35 characters or fewer, including spaces and punctuation.
   The source label (e.g. "BoF", "Reuters") appears on the same line after the headline — leave room for it.
   Count every character before submitting. If over 35, rewrite with shorter words — never cut the sentence.
   Example: "Hugo Boss rejects Frasers bid" = 29 chars ✓
   Example: "Kering cuts costs on weak China demand" = 38 chars ✗ → rewrite as "Kering cuts costs on China weakness" = 35 chars ✓

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
The 3 events below have already been pre-selected as the nearest upcoming or ongoing events.
Copy them into the "diary" array exactly as provided — do not add, remove, or reorder them.
Each diary item must carry the "link" field copied exactly from the entry below.

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


SOURCE_CAPS = {
    "the drinks business": 1,
}

def _enforce_source_caps(result: dict) -> dict:
    """Hard-cap how many items any single source may contribute across lead_items + news."""
    counts = {}
    for section, field in [("lead_items", "primary_source"), ("news", "primary_source")]:
        kept = []
        for item in result.get(section, []):
            src = item.get(field, "").lower()
            cap = SOURCE_CAPS.get(src)
            if cap is not None:
                counts[src] = counts.get(src, 0) + 1
                if counts[src] > cap:
                    log.info(f"  Source cap: dropped extra {item.get(field)} item (cap={cap})")
                    continue
            kept.append(item)
        result[section] = kept
    return result


_BAD_ENDINGS = {
    # prepositions
    "amid", "with", "for", "on", "at", "by", "of", "in", "to", "into",
    "from", "through", "about", "against", "between", "under", "over",
    "within", "without", "beyond", "across", "behind", "during",
    # conjunctions
    "and", "but", "or", "while", "as", "since", "although", "despite",
    "because", "though", "yet", "nor", "so", "than", "whether",
    # articles / possessives
    "the", "a", "an", "its", "their", "his", "her", "our", "your",
    # adjectives that need a noun (common in luxury news)
    "natural", "strong", "new", "major", "key", "first", "second",
    "higher", "lower", "wider", "broader", "further", "additional",
}


MAX_HEADLINE_CHARS = 35

def _headline_is_bad(text: str) -> str | None:
    """Returns a description of the problem if headline is bad, else None."""
    if not text:
        return "empty"
    if len(text) > MAX_HEADLINE_CHARS:
        return f"too long ({len(text)} chars) — must be {MAX_HEADLINE_CHARS} or fewer"
    last_word = text.rstrip(".,;:!?").split()[-1].lower()
    if last_word in _BAD_ENDINGS:
        return f"ends on '{last_word}' — incomplete sentence"
    return None


def _validate_and_fix_headlines(client, result: dict) -> dict:
    """Check every headline and fix bad ones with a targeted Claude call."""
    fixes_needed = []

    for item in result.get("lead_items", []):
        problem = _headline_is_bad(item.get("text", ""))
        if problem:
            fixes_needed.append(("lead", item, "text", problem))

    for item in result.get("news", []):
        problem = _headline_is_bad(item.get("headline", ""))
        if problem:
            fixes_needed.append(("news", item, "headline", problem))

    if not fixes_needed:
        log.info("  Headline validation: all clean")
        return result

    log.warning(f"  Headline validation: {len(fixes_needed)} bad headline(s) — fixing...")

    for section, item, field, problem in fixes_needed:
        bad = item[field]
        fix_prompt = f"""This news headline has a problem: "{bad}"
Problem: {problem}

Rewrite it as a complete, grammatically correct English sentence.
Rules:
- Must be {MAX_HEADLINE_CHARS} characters or fewer (count every character including spaces)
- Must NOT end on a preposition, conjunction, article, or adjective without its noun
- Must make complete sense on its own — who did what
- Do NOT include the source publication name in the headline
- Return ONLY the rewritten headline text, nothing else"""

        try:
            msg = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=100,
                messages=[{"role": "user", "content": fix_prompt}],
            )
            fixed = msg.content[0].text.strip().strip('"')
            log.info(f"  Fixed: '{bad}' → '{fixed}'")
            item[field] = fixed
        except Exception as e:
            log.warning(f"  Could not fix headline '{bad}': {e}")

    return result


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
