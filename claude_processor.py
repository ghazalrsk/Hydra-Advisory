"""
HYDRA SUMMARY — Claude Processor
----------------------------------
Sends all collected articles to the Anthropic Claude API.
Claude deduplicates, selects, summarises, and returns structured JSON.

This is the intelligence layer — the only place editorial judgment happens.
"""

import os
import json
import logging
import anthropic
from sources import SECTOR_DIARY

log = logging.getLogger("hydra-summary.claude")


def process_with_claude(articles: list[dict], stocks: list[dict], today: str) -> dict:
    """
    Sends articles + stocks to Claude and returns a structured digest dict.

    Returns:
    {
        "lead_items": [
            {"text": "...", "link": "..."},   # max 3
        ],
        "numbers": [
            {"name": "LVMH", "price": "€618", "change": "▲ +2.3%",
             "direction": "up", "context": "..."},  # max 4
        ],
        "news": [
            {"headline": "...", "summary": "...", "link": "...",
             "primary_source": "...", "also": ["...", "..."]},  # 4-7 items
        ],
        "roles": [
            {"title": "...", "type": "...", "house": "..."},  # 3-5 items
        ],
        "diary": [
            {"event": "...", "description": "...", "dates": "..."},
        ],
    }
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Build the prompt
    prompt = _build_prompt(articles, stocks, today)

    log.info(f"  Sending {len(articles)} articles to Claude...")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    raw = message.content[0].text

    # Claude is instructed to return pure JSON — parse it
    digest = _parse_response(raw)
    return digest


# ── Prompt builder ────────────────────────────────────────────────────────

def _build_prompt(articles: list[dict], stocks: list[dict], today: str) -> str:

    # Serialise articles for the prompt
    articles_text = json.dumps(articles, ensure_ascii=False, indent=2)
    stocks_text   = json.dumps(stocks,   ensure_ascii=False, indent=2)
    diary_text    = json.dumps(SECTOR_DIARY, ensure_ascii=False, indent=2)

    return f"""You are the editor of Hydra Summary, a daily intelligence briefing for luxury industry professionals (executives, investors, analysts, M&A advisors).

Today's date: {today}

Your task is to process the raw articles and stock data below and return a single JSON object — the structured content for today's Hydra Summary email. No prose, no explanation, no markdown fences. Return only raw JSON.

─────────────────────────────────────
EDITORIAL RULES (follow strictly):
─────────────────────────────────────

DEDUPLICATION:
- Multiple sources often cover the same story. Group them. Show each story ONCE.
- When several sources cover the same event, pick the best article as the primary source. List the others in the "also" array.
- A story appearing in the lead_items must NOT appear again in the news array.

SELECTION CRITERIA — prioritise stories that:
- Involve leadership changes (CEO, Creative Director, CFO, CMO appointments or departures)
- Involve M&A, acquisitions, minority stakes, or restructuring
- Involve earnings, revenue updates, or guidance changes
- Involve major retail openings, closings, or expansion into new markets
- Involve regulatory or trade changes affecting luxury (tariffs, EU regulations, digital passports)
- Come from or affect: LVMH, Kering, Hermès, Richemont, Moncler, Brunello Cucinelli, Chanel, Dior, Gucci, Valentino, Prada, Burberry, Zegna, Rolex, Patek Philippe, Cartier

AVOID:
- Celebrity gossip, street style, purely creative/aesthetic pieces with no business angle
- Repetitive trend pieces with no new information
- Press releases that are pure marketing with no news value

TONE FOR SUMMARIES:
- Neutral, factual, precise. No opinion. No adjectives like "iconic" or "stunning".
- Summaries: exactly 1–2 sentences. Include the key fact + one line of context or implication.
- Lead items: one clause — the headline fact only, no elaboration.

ROLES:
- From the articles, extract any mentions of executive appointments, departures, searches, or open roles.
- Type options: "New appointment", "Departure", "Open search", "Vacancy"

NUMBERS:
- For each stock, write a one-line context note explaining WHY the stock moved today (use the articles as context).
- If you cannot find a reason in the articles, write a brief factual note about the company's recent performance.
- Select only 4 stocks to show — the ones with the most interesting movements or most relevant news today.

SECTOR DIARY:
- From the diary list provided, select the 3–4 most immediately upcoming events (closest to today's date).

─────────────────────────────────────
ARTICLES TO PROCESS ({len(articles)} total):
─────────────────────────────────────
{articles_text}

─────────────────────────────────────
STOCK DATA:
─────────────────────────────────────
{stocks_text}

─────────────────────────────────────
SECTOR DIARY (full list — you select the most relevant):
─────────────────────────────────────
{diary_text}

─────────────────────────────────────
RETURN THIS JSON STRUCTURE — no other text:
─────────────────────────────────────

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
      "summary": "1–2 sentence summary. Factual. The key development and one line of context.",
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


# ── Response parser ────────────────────────────────────────────────────────

def _parse_response(raw: str) -> dict:
    """Parse Claude's JSON response. Falls back gracefully if malformed."""
    import re

    # Strip any accidental markdown fences
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse Claude response as JSON: {e}")
        log.debug(f"Raw response:\n{raw[:500]}")

        # Return a minimal fallback structure so the pipeline doesn't crash
        return {
            "lead_items": [{"text": "Digest generation encountered an issue — please check logs.", "link": ""}],
            "numbers": [],
            "news": [],
            "roles": [],
            "diary": [],
        }
