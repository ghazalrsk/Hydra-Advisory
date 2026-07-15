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
# Each entry has machine-readable start/end (YYYY-MM-DD) for auto-selection.
# select_upcoming_events() below picks the 3 nearest events each morning.
SECTOR_DIARY = [
    # ── JANUARY ──────────────────────────────────────────────────────────
    {"event": "Pitti Uomo 109 · Florence", "description": "Menswear FW26/27", "dates": "13–16 Jan 2026", "start": "2026-01-13", "end": "2026-01-16", "link": "https://pittimmagine.com"},
    {"event": "Maison&Objet · Paris", "description": "Design & interiors trade fair", "dates": "15–19 Jan 2026", "start": "2026-01-15", "end": "2026-01-19", "link": "https://www.maison-objet.com"},
    {"event": "Milan Menswear FW26/27 · Milan", "description": "Men's fashion week", "dates": "16–20 Jan 2026", "start": "2026-01-16", "end": "2026-01-20", "link": "https://cameramoda.it"},
    {"event": "VicenzaOro · Vicenza", "description": "International jewellery fair", "dates": "16–20 Jan 2026", "start": "2026-01-16", "end": "2026-01-20", "link": "https://www.vicenzaoro.com"},
    {"event": "Paris Menswear FW26/27 · Paris", "description": "Men's fashion week", "dates": "20–25 Jan 2026", "start": "2026-01-20", "end": "2026-01-25", "link": "https://www.fhcm.paris"},
    {"event": "Paris Haute Couture SS26 · Paris", "description": "Couture presentations", "dates": "26–29 Jan 2026", "start": "2026-01-26", "end": "2026-01-29", "link": "https://www.fhcm.paris"},
    {"event": "Copenhagen Fashion Week FW26/27 · Copenhagen", "description": "Women's & menswear", "dates": "27–30 Jan 2026", "start": "2026-01-27", "end": "2026-01-30", "link": "https://copenhagenfashionweek.com"},
    {"event": "Cosmoprof North America · Miami", "description": "Beauty trade fair", "dates": "27–29 Jan 2026", "start": "2026-01-27", "end": "2026-01-29", "link": "https://cosmoprofnorthamerica.com/miami"},
    # ── FEBRUARY ─────────────────────────────────────────────────────────
    {"event": "Berlin Fashion Week FW26/27 · Berlin", "description": "Women's & menswear", "dates": "30 Jan–2 Feb 2026", "start": "2026-01-30", "end": "2026-02-02", "link": "https://fashionweek.berlin"},
    {"event": "Seoul Fashion Week FW26/27 · Seoul", "description": "Women's & menswear", "dates": "3–8 Feb 2026", "start": "2026-02-03", "end": "2026-02-08", "link": "https://seoulfashionweek.org"},
    {"event": "Art Basel Qatar · Doha", "description": "Contemporary art fair", "dates": "5–7 Feb 2026", "start": "2026-02-05", "end": "2026-02-07", "link": "https://www.artbasel.com"},
    {"event": "Wine Paris · Paris", "description": "International wine trade fair", "dates": "9–11 Feb 2026", "start": "2026-02-09", "end": "2026-02-11", "link": "https://wine-paris.com"},
    {"event": "New York Fashion Week FW26/27 · New York", "description": "Women's RTW", "dates": "11–16 Feb 2026", "start": "2026-02-11", "end": "2026-02-16", "link": "https://cfda.com"},
    {"event": "London Fashion Week FW26/27 · London", "description": "Women's RTW", "dates": "19–23 Feb 2026", "start": "2026-02-19", "end": "2026-02-23", "link": "https://londonfashionweek.co.uk"},
    {"event": "Frieze Los Angeles · Los Angeles", "description": "Contemporary art fair", "dates": "26 Feb–1 Mar 2026", "start": "2026-02-26", "end": "2026-03-01", "link": "https://frieze.com"},
    {"event": "Milan Fashion Week FW26/27 · Milan", "description": "Women's RTW", "dates": "24 Feb–2 Mar 2026", "start": "2026-02-24", "end": "2026-03-02", "link": "https://cameramoda.it"},
    # ── MARCH ────────────────────────────────────────────────────────────
    {"event": "Paris Fashion Week FW26/27 · Paris", "description": "Women's RTW", "dates": "2–10 Mar 2026", "start": "2026-03-02", "end": "2026-03-10", "link": "https://www.fhcm.paris"},
    {"event": "MIPIM · Cannes", "description": "International property market", "dates": "9–13 Mar 2026", "start": "2026-03-09", "end": "2026-03-13", "link": "https://www.mipim.com"},
    {"event": "TEFAF Maastricht · Maastricht", "description": "Fine art & antiques fair", "dates": "14–19 Mar 2026", "start": "2026-03-14", "end": "2026-03-19", "link": "https://www.tefaf.com"},
    {"event": "ProWein · Düsseldorf", "description": "International wine & spirits trade fair", "dates": "15–17 Mar 2026", "start": "2026-03-15", "end": "2026-03-17", "link": "https://www.prowein.com"},
    {"event": "Tokyo Fashion Week SS26 · Tokyo", "description": "Women's & menswear", "dates": "16–21 Mar 2026", "start": "2026-03-16", "end": "2026-03-21", "link": "https://rakutenfashionweek.tokyo"},
    {"event": "Shanghai Fashion Week SS26 · Shanghai", "description": "Women's & menswear", "dates": "24–31 Mar 2026", "start": "2026-03-24", "end": "2026-03-31", "link": "https://shanghai-fashionweek.com"},
    {"event": "Cosmoprof Worldwide Bologna · Bologna", "description": "Global beauty trade fair", "dates": "26–29 Mar 2026", "start": "2026-03-26", "end": "2026-03-29", "link": "https://www.cosmoprof.com"},
    {"event": "Art Basel Hong Kong · Hong Kong", "description": "Contemporary art fair", "dates": "27–29 Mar 2026", "start": "2026-03-27", "end": "2026-03-29", "link": "https://www.artbasel.com"},
    # ── APRIL ────────────────────────────────────────────────────────────
    {"event": "NYFW Bridal · New York", "description": "Bridal collections", "dates": "7–10 Apr 2026", "start": "2026-04-07", "end": "2026-04-10", "link": "https://cfda.com"},
    {"event": "ILTM Africa · Cape Town", "description": "Luxury travel market", "dates": "10–12 Apr 2026", "start": "2026-04-10", "end": "2026-04-12", "link": "https://www.iltm.com/africa"},
    {"event": "Vinitaly · Verona", "description": "International wine & spirits fair", "dates": "12–15 Apr 2026", "start": "2026-04-12", "end": "2026-04-15", "link": "https://www.vinitaly.com"},
    {"event": "Watches & Wonders · Geneva", "description": "Annual watch & jewellery fair", "dates": "14–20 Apr 2026", "start": "2026-04-14", "end": "2026-04-20", "link": "https://www.watchesandwonders.com"},
    {"event": "Salone del Mobile · Milan", "description": "Milan Design Week", "dates": "21–26 Apr 2026", "start": "2026-04-21", "end": "2026-04-26", "link": "https://www.salonemilano.it"},
    {"event": "South African Fashion Week · Johannesburg", "description": "Women's SS26", "dates": "22–25 Apr 2026", "start": "2026-04-22", "end": "2026-04-25", "link": "https://www.safashionweek.co.za"},
    # ── MAY ──────────────────────────────────────────────────────────────
    {"event": "ILTM Latin America · São Paulo", "description": "Luxury travel market", "dates": "4–7 May 2026", "start": "2026-05-04", "end": "2026-05-07", "link": "https://www.iltm.com/latin-america"},
    {"event": "Australian Fashion Week · Sydney", "description": "Women's SS27", "dates": "11–15 May 2026", "start": "2026-05-11", "end": "2026-05-15", "link": "https://australianfashionweek.org"},
    {"event": "Frieze New York · New York", "description": "Contemporary art fair", "dates": "13–17 May 2026", "start": "2026-05-13", "end": "2026-05-17", "link": "https://frieze.com"},
    {"event": "TEFAF New York · New York", "description": "Fine art & antiques fair", "dates": "14–19 May 2026", "start": "2026-05-14", "end": "2026-05-19", "link": "https://www.tefaf.com"},
    {"event": "Paraiso Miami Swim Week · Miami Beach", "description": "Swimwear & resort collections", "dates": "28–31 May 2026", "start": "2026-05-28", "end": "2026-05-31", "link": "https://paraisomiamibeach.com"},
    {"event": "JCK Las Vegas · Las Vegas", "description": "Jewellery & watches trade fair", "dates": "29 May–1 Jun 2026", "start": "2026-05-29", "end": "2026-06-01", "link": "https://lasvegas.jckonline.com"},
    # ── JUNE ─────────────────────────────────────────────────────────────
    {"event": "3 Days of Design · Copenhagen", "description": "Design fair", "dates": "10–12 Jun 2026", "start": "2026-06-10", "end": "2026-06-12", "link": "https://3daysofdesign.dk"},
    {"event": "Pitti Uomo 110 · Florence", "description": "Menswear SS27", "dates": "16–19 Jun 2026", "start": "2026-06-16", "end": "2026-06-19", "link": "https://pittimmagine.com"},
    {"event": "Milan Menswear SS27 · Milan", "description": "Men's fashion week", "dates": "18–23 Jun 2026", "start": "2026-06-18", "end": "2026-06-23", "link": "https://cameramoda.it"},
    {"event": "Art Basel Basel · Basel", "description": "Contemporary art fair", "dates": "18–21 Jun 2026", "start": "2026-06-18", "end": "2026-06-21", "link": "https://www.artbasel.com"},
    {"event": "Paris Menswear SS27 · Paris", "description": "Men's fashion week", "dates": "23–28 Jun 2026", "start": "2026-06-23", "end": "2026-06-28", "link": "https://www.fhcm.paris"},
    {"event": "Cosmoprof CBE ASEAN · Bangkok", "description": "Beauty trade fair", "dates": "24–26 Jun 2026", "start": "2026-06-24", "end": "2026-06-26", "link": "https://www.cosmoprof.com"},
    {"event": "ILTM Asia Pacific · Singapore", "description": "Luxury travel market", "dates": "29 Jun–2 Jul 2026", "start": "2026-06-29", "end": "2026-07-02", "link": "https://www.iltm.com/asia-pacific"},
    # ── JULY ─────────────────────────────────────────────────────────────
    {"event": "Paris Haute Couture FW26/27 · Paris", "description": "Couture presentations", "dates": "6–9 Jul 2026", "start": "2026-07-06", "end": "2026-07-09", "link": "https://www.fhcm.paris"},
    {"event": "Cosmoprof North America · Las Vegas", "description": "Beauty trade fair", "dates": "13–15 Jul 2026", "start": "2026-07-13", "end": "2026-07-15", "link": "https://cosmoprofnorthamerica.com"},
    {"event": "Monaco Red Cross Gala · Monaco", "description": "77th edition of the annual charity gala", "dates": "18 Jul 2026", "start": "2026-07-18", "end": "2026-07-18", "link": "https://croix-rouge.mc/en/evenements/le-gala/"},
    {"event": "Milano Summer Fashion Exhibitions · Milan", "description": "Summer fashion exhibitions", "dates": "25 Jul 2026", "start": "2026-07-25", "end": "2026-07-25", "link": ""},
    # ── AUGUST ───────────────────────────────────────────────────────────
    {"event": "Copenhagen Fashion Week SS27 · Copenhagen", "description": "Women's & menswear", "dates": "3–7 Aug 2026", "start": "2026-08-03", "end": "2026-08-07", "link": "https://copenhagenfashionweek.com"},
    {"event": "Tokyo Fashion Week SS27 · Tokyo", "description": "Women's & menswear", "dates": "31 Aug–5 Sep 2026", "start": "2026-08-31", "end": "2026-09-05", "link": "https://rakutenfashionweek.tokyo"},
    # ── SEPTEMBER ────────────────────────────────────────────────────────
    {"event": "Seoul Fashion Week SS27 · Seoul", "description": "Women's & menswear", "dates": "1–6 Sep 2026", "start": "2026-09-01", "end": "2026-09-06", "link": "https://seoulfashionweek.org"},
    {"event": "Frieze Seoul · Seoul", "description": "Contemporary art fair", "dates": "2–5 Sep 2026", "start": "2026-09-02", "end": "2026-09-05", "link": "https://frieze.com"},
    {"event": "VicenzaOro September · Vicenza", "description": "International jewellery fair", "dates": "4–8 Sep 2026", "start": "2026-09-04", "end": "2026-09-08", "link": "https://www.vicenzaoro.com"},
    {"event": "New York Fashion Week SS27 · New York", "description": "Women's RTW", "dates": "10–15 Sep 2026", "start": "2026-09-10", "end": "2026-09-15", "link": "https://cfda.com"},
    {"event": "Maison&Objet September · Paris", "description": "Design & interiors trade fair", "dates": "10–14 Sep 2026", "start": "2026-09-10", "end": "2026-09-14", "link": "https://www.maison-objet.com"},
    {"event": "London Design Festival · London", "description": "Design week", "dates": "12–20 Sep 2026", "start": "2026-09-12", "end": "2026-09-20", "link": "https://londondesignfestival.com"},
    {"event": "London Fashion Week SS27 · London", "description": "Women's RTW", "dates": "17–21 Sep 2026", "start": "2026-09-17", "end": "2026-09-21", "link": "https://londonfashionweek.co.uk"},
    {"event": "Milan Fashion Week SS27 · Milan", "description": "Women's RTW", "dates": "22–28 Sep 2026", "start": "2026-09-22", "end": "2026-09-28", "link": "https://cameramoda.it"},
    {"event": "ILTM North America · Nassau", "description": "Luxury travel market", "dates": "28 Sep–1 Oct 2026", "start": "2026-09-28", "end": "2026-10-01", "link": "https://www.iltm.com/north-america"},
    {"event": "Paris Fashion Week SS27 · Paris", "description": "Women's RTW", "dates": "28 Sep–6 Oct 2026", "start": "2026-09-28", "end": "2026-10-06", "link": "https://www.fhcm.paris"},
    # ── OCTOBER ──────────────────────────────────────────────────────────
    {"event": "Beautyworld Middle East · Dubai", "description": "Beauty & wellness trade fair", "dates": "6–8 Oct 2026", "start": "2026-10-06", "end": "2026-10-08", "link": "https://www.beautyworldme.com"},
    {"event": "Frieze London & Frieze Masters · London", "description": "Contemporary & modern art fair", "dates": "14–18 Oct 2026", "start": "2026-10-14", "end": "2026-10-18", "link": "https://frieze.com"},
    {"event": "Art Basel Paris · Paris", "description": "Contemporary art fair", "dates": "20–25 Oct 2026", "start": "2026-10-20", "end": "2026-10-25", "link": "https://www.artbasel.com"},
    {"event": "Design Miami/Paris · Paris", "description": "Design fair", "dates": "20–25 Oct 2026", "start": "2026-10-20", "end": "2026-10-25", "link": "https://designmiami.com"},
    {"event": "MIPIM Middle East · Riyadh", "description": "Property market", "dates": "20–21 Oct 2026", "start": "2026-10-20", "end": "2026-10-21", "link": "https://www.mipim.com"},
    {"event": "Lagos Fashion Week · Lagos", "description": "Women's & menswear", "dates": "28 Oct–1 Nov 2026", "start": "2026-10-28", "end": "2026-11-01", "link": "https://lagosfashionweek.ng"},
    {"event": "Artissima · Turin", "description": "Contemporary art fair", "dates": "30 Oct–1 Nov 2026", "start": "2026-10-30", "end": "2026-11-01", "link": "https://www.artissima.it"},
    # ── NOVEMBER ─────────────────────────────────────────────────────────
    {"event": "Cosmoprof Asia · Hong Kong", "description": "Beauty trade fair", "dates": "11–13 Nov 2026", "start": "2026-11-11", "end": "2026-11-13", "link": "https://www.cosmoprof-asia.com"},
    {"event": "ILTM Cannes · Cannes", "description": "International luxury travel market", "dates": "30 Nov–3 Dec 2026", "start": "2026-11-30", "end": "2026-12-03", "link": "https://www.iltm.com"},
    # ── DECEMBER ─────────────────────────────────────────────────────────
    {"event": "Design Miami · Miami Beach", "description": "Design fair", "dates": "1–6 Dec 2026", "start": "2026-12-01", "end": "2026-12-06", "link": "https://designmiami.com"},
    {"event": "Art Basel Miami Beach · Miami", "description": "Contemporary art fair", "dates": "2–6 Dec 2026", "start": "2026-12-02", "end": "2026-12-06", "link": "https://www.artbasel.com"},
    {"event": "MIPIM Asia Summit · Hong Kong", "description": "Asia property market summit", "dates": "2–3 Dec 2026", "start": "2026-12-02", "end": "2026-12-03", "link": "https://www.mipim-asia.com"},
    {"event": "Cosmoprof India · Mumbai", "description": "Beauty trade fair", "dates": "10–12 Dec 2026", "start": "2026-12-10", "end": "2026-12-12", "link": "https://www.cosmoprof.com"},
]


def select_upcoming_events(today=None, n: int = 3) -> list[dict]:
    """Return the n nearest events that are ongoing or upcoming."""
    from datetime import date
    if today is None:
        today = date.today()
    elif isinstance(today, str):
        today = date.fromisoformat(today)

    candidates = []
    for event in SECTOR_DIARY:
        end = date.fromisoformat(event["end"])
        start = date.fromisoformat(event["start"])
        if end >= today:
            candidates.append((start, event))

    candidates.sort(key=lambda x: x[0])
    return [e for _, e in candidates[:n]]
