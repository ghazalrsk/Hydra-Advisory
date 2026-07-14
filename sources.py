"""
HYDRA SUMMARY — Sources
------------------------
Define every source here. The collector reads this file.

Source tiers control attribution in the digest:
  Tier 1 — Wire/financial press: always the primary attribution
  Tier 2 — Trade press: primary only when Tier 1 has not covered the story
  Tier 3 — Context/brand sources: "also" attribution only, never primary
"""

NEWS_SOURCES = [
    # ── Tier 1: Wire / financial press — always primary attribution ───────
    {
        "name": "Reuters",
        "rss": "https://feeds.reuters.com/reuters/businessNews",
        "section": "news",
        "tier": 1,
    },
    {
        "name": "Financial Times — Luxury",
        "rss": "https://www.ft.com/luxury/rss",
        "section": "news",
        "tier": 1,
    },
    {
        "name": "Il Sole 24 Ore - Moda",
        "rss": "https://www.ilsole24ore.com/rss/moda.xml",
        "section": "news",
        "tier": 1,
    },
    {
        "name": "Bloomberg Pursuits",
        "rss": "https://feeds.bloomberg.com/luxury/news.rss",
        "section": "news",
        "tier": 1,
    },
    {
        "name": "Vogue Business",
        "rss": "https://www.voguebusiness.com/feed",
        "section": "news",
        "tier": 1,
    },
    {
        "name": "WWD",
        "rss": "https://wwd.com/feed/",
        "section": "news",
        "tier": 1,
    },
    # ── Tier 2: Trade press — primary when Tier 1 absent ─────────────────
    {
        "name": "Business of Fashion",
        "rss": "https://www.businessoffashion.com/feed/",
        "section": "news",
        "tier": 2,
    },
    {
        "name": "Pambianco News",
        "rss": "https://www.pambianconews.com/feed/",
        "section": "news",
        "tier": 2,
    },
    {
        "name": "MFF — Moda Finanza Fashion",
        "rss": "https://www.mffashion.com/rss",
        "section": "news",
        "tier": 2,
    },
    {
        "name": "Luxury Daily",
        "rss": "https://www.luxurydaily.com/feed/",
        "section": "news",
        "tier": 2,
    },
    {
        "name": "The Drinks Business",
        "rss": "https://www.thedrinksbusiness.com/feed/",
        "section": "news",
        "tier": 2,
    },
    # ── Tier 3: Context only — "also" attribution, never primary ─────────
    {
        "name": "Fashion Network",
        "rss": "https://us.fashionnetwork.com/rss/news.xml",
        "section": "news",
        "tier": 3,
    },
    {
        "name": "Luxury Society",
        "rss": "https://luxurysociety.com/en/articles/feed",
        "section": "news",
        "tier": 3,
    },
    {
        "name": "LVMH Newsroom",
        "rss": "https://www.lvmh.com/news-documents/news/feed/",
        "section": "news",
        "tier": 3,
    },
    {
        "name": "Kering Press",
        "rss": "https://www.kering.com/en/news/rss/",
        "section": "news",
        "tier": 3,
    },
    {
        "name": "Richemont News",
        "rss": "https://www.richemont.com/media/press-releases/rss/",
        "section": "news",
        "tier": 3,
    },
    {
        "name": "Skift",
        "rss": "https://skift.com/feed/",
        "section": "news",
        "tier": 3,
    },
    {
        "name": "Dezeen",
        "rss": "https://www.dezeen.com/feed/",
        "section": "news",
        "tier": 3,
    },
    {
        "name": "Fashion United",
        "rss": "https://fashionunited.com/rss",
        "section": "news",
        "tier": 3,
    },
]


# ── STOCK TICKERS ────────────────────────────────────────────────────────
# Broad luxury-sector universe. Each morning, collector.py ranks all of these
# by absolute 24h % change and keeps only the top 6 movers for the digest.
STOCK_TICKERS = {
    "LVMH":               "MC.PA",
    "Kering":             "KER.PA",
    "Hermès":             "RMS.PA",
    "Richemont":          "CFR.SW",
    "Moncler":            "MONC.MI",
    "Brunello Cucinelli": "BC.MI",
    "Burberry":           "BRBY.L",
    "Ferragamo":          "SFER.MI",
    "Prada Group":        "1913.HK",
    "Tod's Group":        "TOD.MI",
    "Swatch Group":       "UHR.SW",
    "Tapestry":           "TPR",
    "Capri Holdings":     "CPRI",
    "L'Oréal":            "OR.PA",
    "Estée Lauder":       "EL",
}


# ── SECTOR DIARY ─────────────────────────────────────────────────────────
SECTOR_DIARY = [
    {
        "event": "Salone del Mobile · Milan",
        "description": "Design Week",
        "dates": "17–22 Jun 2026",
        "link": "https://www.salonemilano.it",
    },
    {
        "event": "Haute Couture Week · Paris",
        "description": "Couture presentations",
        "dates": "1–5 Jul 2026",
        "link": "https://fhcm.paris",
    },
    {
        "event": "Watches & Wonders · Geneva",
        "description": "Annual watch fair",
        "dates": "9–15 Jul 2026",
        "link": "https://www.watchesandwonders.com",
    },
    {
        "event": "Bain Luxury Study · Summer Update",
        "description": "Market sizing report",
        "dates": "23–30 Jun 2026",
        "link": "https://www.bain.com/insights/topics/luxury-goods-and-fashion/",
    },
    {
        "event": "Milan Fashion Week · Women's S/S 2027",
        "description": "Ready-to-wear",
        "dates": "16–22 Sep 2026",
        "link": "https://www.cameramoda.it",
    },
    {
        "event": "Paris Fashion Week · Women's S/S 2027",
        "description": "Ready-to-wear",
        "dates": "25 Sep – 3 Oct 2026",
        "link": "https://fhcm.paris",
    },
]
