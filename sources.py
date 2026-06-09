"""
HYDRA SUMMARY — Sources
------------------------
Define every source here. The collector reads this file.

HOW TO ADD A SOURCE:
  1. Find the RSS feed URL for the publication (usually site.com/feed or site.com/rss)
  2. Add it to the NEWS_SOURCES list below
  3. Set the section: "news", "roles", or "both"

HOW TO ADD A STOCK:
  Add the ticker symbol to STOCK_TICKERS. The collector uses Yahoo Finance.
  Format: "TICKER.EXCHANGE" — e.g. "MC.PA" for LVMH on Paris, "CFR.SW" for Richemont on Swiss.
"""

# ── NEWS SOURCES ────────────────────────────────────────────────────────
# Each entry: name, RSS url, section (news / roles / both)
NEWS_SOURCES = [
    {
        "name": "Business of Fashion",
        "rss": "https://www.businessoffashion.com/feed/",
        "section": "news",
    },
    {
        "name": "Vogue Business",
        "rss": "https://www.voguebusiness.com/feed",
        "section": "news",
    },
    {
        "name": "WWD",
        "rss": "https://wwd.com/feed/",
        "section": "news",
    },
    {
        "name": "Pambianco News",
        "rss": "https://www.pambianconews.com/feed/",
        "section": "news",
    },
    {
        "name": "Il Sole 24 Ore - Moda",
        "rss": "https://www.ilsole24ore.com/rss/moda.xml",
        "section": "news",
    },
    {
        "name": "Luxury Society",
        "rss": "https://luxurysociety.com/en/articles/feed",
        "section": "news",
    },
    {
        "name": "Luxe Digital",
        "rss": "https://luxe.digital/feed/",
        "section": "news",
    },
    {
        "name": "The Business of Luxury",
        "rss": "https://www.ft.com/luxury/rss",
        "section": "news",
    },
    {
        "name": "Reuters Luxury",
        "rss": "https://feeds.reuters.com/reuters/businessNews",
        "section": "news",
    },
    {
        "name": "LVMH Newsroom",
        "rss": "https://www.lvmh.com/news-documents/news/feed/",
        "section": "news",
    },
    {
        "name": "Kering Press",
        "rss": "https://www.kering.com/en/news/rss/",
        "section": "news",
    },
    {
        "name": "Richemont News",
        "rss": "https://www.richemont.com/media/press-releases/rss/",
        "section": "news",
    },
    # Add more sources below ↓
    # {
    #     "name": "My New Source",
    #     "rss": "https://example.com/feed",
    #     "section": "news",
    # },
]


# ── STOCK TICKERS ────────────────────────────────────────────────────────
# Format: { "display_name": "TICKER.EXCHANGE" }
# Exchange suffixes: .PA = Paris, .SW = Swiss, .MI = Milan, .L = London
STOCK_TICKERS = {
    "LVMH":              "MC.PA",
    "Kering":            "KER.PA",
    "Hermès":            "RMS.PA",
    "Richemont":         "CFR.SW",
    "Moncler":           "MONC.MI",
    "Brunello Cucinelli": "BC.MI",
    "Burberry":          "BRBY.L",
    "Ferragamo":         "SFER.MI",
}


# ── SECTOR DIARY ─────────────────────────────────────────────────────────
# Static calendar of upcoming events.
# Update this list each month. Claude will pick the next 3–4 relevant ones.
SECTOR_DIARY = [
    {
        "event": "Salone del Mobile · Milan",
        "description": "Design Week — brand activations across Brera and Tortona districts",
        "dates": "17–22 Jun 2026",
    },
    {
        "event": "Haute Couture Week · Paris",
        "description": "F/W 2026 Haute Couture presentations",
        "dates": "1–5 Jul 2026",
    },
    {
        "event": "Watches & Wonders · Geneva",
        "description": "Richemont-led annual watch fair — all major maisons present",
        "dates": "9–15 Jul 2026",
    },
    {
        "event": "Bain Luxury Study · Summer Update",
        "description": "Mid-year luxury market sizing — embargoed release",
        "dates": "Est. late Jun 2026",
    },
    {
        "event": "Milan Fashion Week · Women's S/S 2027",
        "description": "Ready-to-wear collections",
        "dates": "16–22 Sep 2026",
    },
    {
        "event": "Paris Fashion Week · Women's S/S 2027",
        "description": "Ready-to-wear collections",
        "dates": "25 Sep – 3 Oct 2026",
    },
]
