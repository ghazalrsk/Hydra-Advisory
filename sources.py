"""
HYDRA SUMMARY — Sources
------------------------
Define every source here. The collector reads this file.
"""

NEWS_SOURCES = [
    # ── Tier 1: English-language trade ──────────────────────────────────
    {
        "name": "Business of Fashion",
        "rss": "https://www.businessoffashion.com/feed/",
        "section": "news",
    },
    {
        "name": "WWD",
        "rss": "https://wwd.com/feed/",
        "section": "news",
    },
    {
        "name": "Vogue Business",
        "rss": "https://www.voguebusiness.com/feed",
        "section": "news",
    },
    # ── Italian market ───────────────────────────────────────────────────
    {
        "name": "Pambianco News",
        "rss": "https://www.pambianconews.com/feed/",
        "section": "news",
    },
    {
        "name": "MFF — Moda Finanza Fashion",
        "rss": "https://www.mffashion.com/rss",
        "section": "news",
    },
    {
        "name": "Il Sole 24 Ore - Moda",
        "rss": "https://www.ilsole24ore.com/rss/moda.xml",
        "section": "news",
    },
    # ── Financial wire / broad market ────────────────────────────────────
    {
        "name": "Reuters",
        "rss": "https://feeds.reuters.com/reuters/businessNews",
        "section": "news",
    },
    {
        "name": "Financial Times — Luxury",
        "rss": "https://www.ft.com/luxury/rss",
        "section": "news",
    },
    # ── Asia signals ─────────────────────────────────────────────────────
    {
        "name": "South China Morning Post",
        "rss": "https://www.scmp.com/rss/91/feed",
        "section": "news",
    },
    {
        "name": "Nikkei Asia",
        "rss": "https://asia.nikkei.com/rss/feed/nar",
        "section": "news",
    },
    # ── European trade ───────────────────────────────────────────────────
    {
        "name": "Fashion Network",
        "rss": "https://us.fashionnetwork.com/rss/news.xml",
        "section": "news",
    },
    {
        "name": "Luxury Society",
        "rss": "https://luxurysociety.com/en/articles/feed",
        "section": "news",
    },
    # ── Group newsrooms ──────────────────────────────────────────────────
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
]


# ── STOCK TICKERS ────────────────────────────────────────────────────────
# Broad luxury-sector universe. Each morning, collector.py ranks all of these
# by absolute 24h % change and keeps only the top 5 movers for the digest.
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
