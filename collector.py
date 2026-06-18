"""
HYDRA SUMMARY — Collector
--------------------------
Fetches articles from all RSS sources and stock prices.
Called by main.py at Step 1 and Step 2.
"""

import feedparser
import yfinance as yf
import logging
from datetime import datetime, timedelta, timezone
from sources import NEWS_SOURCES, STOCK_TICKERS

log = logging.getLogger("hydra-summary.collector")

# Only fetch articles published in the last N hours
HOURS_LOOKBACK = 26  # slightly more than 24h to catch overnight articles


def fetch_all_articles() -> list[dict]:
    """
    Reads every RSS source in sources.py and returns a flat list of articles
    published in the last HOURS_LOOKBACK hours.

    Each article dict has:
        title      — headline
        summary    — first paragraph or RSS description
        link       — URL
        source     — publication name
        section    — "news" or "roles"
        published  — datetime string
    """
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)

    for source in NEWS_SOURCES:
        try:
            feed = feedparser.parse(source["rss"])
            count = 0

            for entry in feed.entries:
                # Parse published date
                pub = _parse_date(entry)
                if pub and pub < cutoff:
                    continue  # skip old articles

                article = {
                    "title":     getattr(entry, "title", "").strip(),
                    "summary":   _clean_summary(getattr(entry, "summary", "")),
                    "link":      getattr(entry, "link", ""),
                    "source":    source["name"],
                    "section":   source["section"],
                    "published": pub.isoformat() if pub else "",
                }

                # Skip articles with no title or link
                if not article["title"] or not article["link"]:
                    continue

                articles.append(article)
                count += 1

            log.info(f"  {source['name']:40s} → {count} articles")

        except Exception as e:
            log.warning(f"  Failed to fetch {source['name']}: {e}")

    return articles


def fetch_stock_prices(top_n: int = 5) -> list[dict]:
    """
    Fetches today's price and daily change for every ticker in STOCK_TICKERS,
    then returns only the top_n with the highest absolute 24h % change
    (the "biggest movers" for the Important Numbers section).

    Returns a list of dicts:
        name      — display name (e.g. "LVMH")
        ticker    — e.g. "MC.PA"
        price     — current price as string with currency symbol
        change    — e.g. "+2.3%" or "-1.1%"
        direction — "up", "down", or "flat"
        currency  — e.g. "€", "CHF", "£"
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

            # Currency symbol
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
    """Try to extract a timezone-aware datetime from an RSS entry."""
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
    """Strip HTML tags and truncate summary to 400 chars."""
    import re
    text = re.sub(r"<[^>]+>", "", text)   # remove HTML tags
    text = re.sub(r"\s+", " ", text).strip()
    return text[:400] + "..." if len(text) > 400 else text
