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
import logging
import math
import os
import requests
try:
    import yfinance as yf
    _YF_AVAILABLE = True
except ImportError:
    _YF_AVAILABLE = False
from datetime import datetime, timedelta, timezone
from sources import NEWS_SOURCES, STOCK_TICKERS

log = logging.getLogger("hydra-summary.collector")

HOURS_LOOKBACK_NORMAL = 26
HOURS_LOOKBACK_MONDAY = 72
MAX_PER_SOURCE = 5


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

            # Sort newest first, cap at MAX_PER_SOURCE (higher for Tier 1)
            source_articles.sort(key=lambda a: a["published"], reverse=True)
            cap = 8 if tier == 1 else MAX_PER_SOURCE
            kept = source_articles[:cap]
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


def _parse_closes_polygon(ticker: str):
    """Primary: Polygon.io previous-day close. Returns (today_close, prev_close) or raises."""
    api_key = os.environ.get("POLYGON_API_KEY", "")
    if not api_key:
        raise ValueError("no POLYGON_API_KEY")
    # Polygon uses plain US tickers; skip non-US tickers (they contain a dot)
    base = ticker.split(".")[0]
    if "." in ticker and not ticker.endswith(".US"):
        raise ValueError(f"non-US ticker {ticker}, skip Polygon")
    url = f"https://api.polygon.io/v2/aggs/ticker/{base}/prev?adjusted=true&apiKey={api_key}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if len(results) < 1:
        raise ValueError("no results from Polygon")
    today = float(results[0]["c"])
    prev  = float(results[0]["o"])   # open as proxy for prev close
    if math.isnan(today) or math.isnan(prev) or prev == 0:
        raise ValueError("NaN or zero")
    return today, prev


def _parse_closes_fmp(ticker: str):
    """Secondary: Financial Modeling Prep EOD. Returns (today_close, prev_close) or raises."""
    api_key = os.environ.get("FMP_API_KEY", "")
    if not api_key:
        raise ValueError("no FMP_API_KEY")
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?timeseries=2&apikey={api_key}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    hist = data.get("historical", [])
    if len(hist) < 2:
        raise ValueError("insufficient FMP data")
    today = float(hist[0]["close"])
    prev  = float(hist[1]["close"])
    if math.isnan(today) or math.isnan(prev) or prev == 0:
        raise ValueError("NaN or zero")
    return today, prev


def _parse_closes_stooq(ticker: str):
    """Tertiary fallback: Stooq CSV API. Returns (today_close, prev_close) or raises."""
    url  = f"https://stooq.com/q/d/l/?s={ticker.lower()}&i=d"
    resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    lines = [l for l in resp.text.strip().splitlines() if l and not l.startswith("Date")]
    if len(lines) < 2:
        raise ValueError("insufficient Stooq data")
    def _close(row):
        parts = row.split(",")
        return float(parts[4]) if len(parts) >= 5 else None
    today = _close(lines[-1])
    prev  = _close(lines[-2])
    if today is None or prev is None or math.isnan(today) or math.isnan(prev) or prev == 0:
        raise ValueError("NaN or unparseable")
    return today, prev


def fetch_stock_prices(top_n: int = 6) -> list[dict]:
    """
    Primary:   Polygon.io (US tickers only on free plan).
    Secondary: Financial Modeling Prep (all tickers including European).
    Tertiary:  Stooq CSV API.
    Returns all fetched stocks; caller selects top/bottom performers.
    """
    stocks = []

    currency_map = {
        ".PA": "€",
        ".MI": "€",
        ".SW": "CHF",
        ".L":  "£",
        ".HK": "HK$",
        ".US": "$",
        "":    "$",
    }

    for name, ticker in STOCK_TICKERS.items():
        today_close = prev_close = None
        source = "?"

        try:
            today_close, prev_close = _parse_closes_polygon(ticker)
            source = "Polygon"
        except Exception as e:
            log.info(f"  Polygon skipped for {ticker}: {e}")

        if today_close is None:
            try:
                today_close, prev_close = _parse_closes_fmp(ticker)
                source = "FMP"
            except Exception as e:
                log.warning(f"  FMP failed for {ticker}: {e} — trying Stooq")

        if today_close is None:
            try:
                today_close, prev_close = _parse_closes_stooq(ticker)
                source = "Stooq"
            except Exception as e:
                log.warning(f"  Stooq failed for {ticker}: {e} — trying yfinance")

        if today_close is None:
            try:
                if not _YF_AVAILABLE:
                    raise ValueError("yfinance not installed")
                data = yf.Ticker(ticker)
                hist = data.history(period="2d")
                if len(hist) < 2:
                    raise ValueError("insufficient yf data")
                prev_close  = float(hist["Close"].iloc[-2])
                today_close = float(hist["Close"].iloc[-1])
                if math.isnan(prev_close) or math.isnan(today_close) or prev_close == 0:
                    raise ValueError("NaN or zero")
                source = "yfinance"
            except Exception as e:
                log.warning(f"  yfinance also failed for {ticker}: {e} — skipping")
                continue

        suffix = f".{ticker.split('.')[-1]}" if "." in ticker else ""
        currency   = currency_map.get(suffix, "$")
        pct_change = ((today_close - prev_close) / prev_close) * 100
        direction  = "up" if pct_change > 0.1 else ("down" if pct_change < -0.1 else "flat")
        sign       = "▲ +" if pct_change > 0 else ("▼ " if pct_change < 0 else "")

        stocks.append({
            "name":       name,
            "ticker":     ticker,
            "price":      f"{currency}{today_close:,.2f}",
            "change":     f"{sign}{pct_change:.1f}%",
            "direction":  direction,
            "currency":   currency,
            "raw_price":  round(today_close, 2),
            "raw_change": round(pct_change, 2),
        })
        log.info(f"  {name} ({ticker}) [{source}]: {currency}{today_close:.2f} {sign}{pct_change:.1f}%")

    return stocks


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
