"""
HYDRA SUMMARY — Collector
--------------------------
Fetches articles from all RSS sources and stock prices.
Called by server.py each morning.

Article pool rules:
  - Max 3 articles per source (newest first) to prevent high-volume
    sources from dominating the pool Claude sees.
  - Articles are sorted by tier then recency before being passed to Claude,
    so Tier 1 sources appear first and carry more weight.
  - Monday editions fetch 72 hours of content (to catch weekend stories).
"""

import feedparser
import yfinance as yf
import logging
from datetime import datetime, timedelta, timezone
from sources import NEWS_SOURCES, STOCK_TICKERS

log = logging.getLogger("hydra-summary.collector")

HOURS_LOOKBACK_NORMAL = 26
HOURS_LOOKBACK_MONDAY = 72
MAX_PER_SOURCE = 3


def fetch_all_articles(is_monday: bool = False) -> list[dict]:
    """
    Reads every RSS source in sources.py and returns a flat list of articles.

    Each article dict has:
        title      — headline
        summary    — first paragraph or RSS description
        link       — URL
        source     — publication name
        tier       — source tier (1, 2, or 3)
        section    — "news"
        published  — datetime string
    """
    hours = HOURS_LOOKBACK_MONDAY if is_monday else HOURS_LOOKBACK_NORMAL
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    log.info(f"  Fetching articles from last {hours}h (monday={is_monday})")

    articles = []

    for source in NEWS_SOURCES:
        tier = source.get("tier", 2)
        try:
            feed = feedparser.parse(source["rss"])
            source_articles = []

            for entry in feed.entries:
                pub = _parse_date(entry)
                if pub and pub < cutoff:
                    continue

                article = {
                    "title":     getattr(entry, "title", "").strip(),
                    "summary":   _clean_summary(getattr(entry, "summary", "")),
                    "link":      getattr(entry, "link", ""),
                    "source":    source["name"],
                    "tier":      tier,
                    "section":   source["section"],
                    "published": pub.isoformat() if pub else "",
                }

                if not article["title"] or not article["link"]:
                    continue

                source_articles.append(article)

            # Sort newest first, cap at MAX_PER_SOURCE
            source_articles.sort(key=lambda a: a["published"], reverse=True)
            kept = source_articles[:MAX_PER_SOURCE]
            articles.extend(kept)
            log.info(f"  {source['name']:40s} tier={tier} → {len(kept)}/{len(source_articles)} articles")

        except Exception as e:
            log.warning(f"  Failed to fetch {source['name']}: {e}")

    # Sort final pool: tier ascending (Tier 1 first), then newest first
    articles.sort(key=lambda a: (a["tier"], a["published"]), reverse=False)
    articles.sort(key=lambda a: a["published"], reverse=True)
    # Final sort: tier first so Claude sees Tier 1 articles at the top
    articles.sort(key=lambda a: a["tier"])

    return articles


def fetch_stock_prices(top_n: int = 6) -> list[dict]:
    """
    Fetches today's price and daily change for every ticker in STOCK_TICKERS,
    then returns only the top_n with the highest absolute 24h % change.
    """
    stocks = []

    currency_map = {
        ".PA": "€",
        ".MI": "€",
        ".SW": "CHF",
        ".L":  "£",
        "":    "$",
    }

    for name, ticker in STOCK_TICKERS.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="2d")

            if len(hist) < 2:
                log.warning(f"  Not enough data for {ticker}")
                continue

            prev_close = hist["Close"].iloc[-2]
            today_close = hist["Close"].iloc[-1]
            pct_change = ((today_close - prev_close) / prev_close) * 100

            suffix = "." + ticker.split(".")[-1] if "." in ticker else ""
            currency = currency_map.get(f".{ticker.split('.')[-1]}", "€")

            direction = "up" if pct_change > 0.1 else ("down" if pct_change < -0.1 else "flat")
            sign = "▲ +" if pct_change > 0 else ("▼ " if pct_change < 0 else "")

            stocks.append({
                "name":      name,
                "ticker":    ticker,
                "price":     f"{currency}{today_close:,.2f}",
                "change":    f"{sign}{pct_change:.1f}%",
                "direction": direction,
                "currency":  currency,
                "raw_price": round(today_close, 2),
                "raw_change": round(pct_change, 2),
            })

        except Exception as e:
            log.warning(f"  Failed to fetch {ticker}: {e}")

    stocks.sort(key=lambda s: abs(s["raw_change"]), reverse=True)
    return stocks[:top_n]


# ── Helpers ──────────────────────────────────────────────────────────────

def _parse_date(entry) -> datetime | None:
    import time
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, field, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _clean_summary(text: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:400] + "..." if len(text) > 400 else text
