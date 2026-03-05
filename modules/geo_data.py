# modules/geo_data.py
# ─────────────────────────────────────────────────────────────────────────────
# GEOPOLITICAL INTELLIGENCE DATA LAYER
# Placeholder JSON feed — structured for future replacement with live News APIs
# (e.g., NewsAPI, GDELT, MEA Press Releases, Bloomberg Feeds)
# Fields: title, region, category, probability (0-1), impact (0-1), sentiment
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime

# ── Sentiment constants ───────────────────────────────────────────────────────
SENTIMENT_POSITIVE = "positive"
SENTIMENT_NEGATIVE = "negative"
SENTIMENT_NEUTRAL  = "neutral"

# ── Category → Sector mapping (used by Alpha Sentiment Engine) ────────────────
CATEGORY_SECTOR_MAP = {
    "defense":      ["defense"],
    "energy":       ["energy"],
    "technology":   ["it"],
    "trade":        ["it", "energy"],
    "diplomacy":    ["defense", "energy"],
    "border":       ["defense"],
    "multilateral": ["energy", "it"],
    "crude_oil":    ["energy", "aviation", "paints"],
}

# ── Master news feed (placeholder — extendable via DB or API) ─────────────────
def get_news_feed() -> list[dict]:
    """
    Returns structured geopolitical news feed.
    PLACEHOLDER: Replace body with live API call (NewsAPI / GDELT / MEA RSS).
    Each item: {title, region, category, probability, impact, sentiment, date, summary}
    """
    return [
        # ── IMEC Corridor ─────────────────────────────────────────────────────
        {
            "id": "GEO-001",
            "title": "IMEC Corridor: India-UAE Rail-Sea Link Advances to Phase 2 MoU",
            "region": "Middle East / South Asia",
            "category": "trade",
            "probability": 0.72,
            "impact": 0.85,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-01",
            "summary": (
                "India-Middle East-Europe Economic Corridor enters binding MoU phase. "
                "Port Mundra and JNPT designated as primary Indian nodes. "
                "Positive for logistics, infrastructure, and export-linked IT services."
            ),
            "tags": ["IMEC", "trade", "infrastructure", "connectivity"],
        },
        {
            "id": "GEO-002",
            "title": "Saudi Arabia Delays IMEC Rail Segment — Regional Tensions Cited",
            "region": "Middle East",
            "category": "trade",
            "probability": 0.45,
            "impact": 0.60,
            "sentiment": SENTIMENT_NEGATIVE,
            "date": "2025-02",
            "summary": (
                "Saudi stakeholders signal 12-18 month delay in Riyadh-Haifa rail spur "
                "due to Israel-Palestine spillover risks. May dampen short-term IMEC momentum."
            ),
            "tags": ["IMEC", "delay", "Saudi Arabia", "geopolitical risk"],
        },

        # ── LAC Border Status ─────────────────────────────────────────────────
        {
            "id": "GEO-003",
            "title": "India-China Agree on Depsang Buffer Zone Patrol Protocol",
            "region": "Himalayan / LAC",
            "category": "border",
            "probability": 0.68,
            "impact": 0.78,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-01",
            "summary": (
                "Structured patrol protocol at Depsang Plains reduces friction. "
                "Positive signal for border stability; defense capex trajectory maintained. "
                "HAL, BEL order books remain robust per Ministry of Defence statements."
            ),
            "tags": ["LAC", "border", "China", "Depsang", "defense"],
        },
        {
            "id": "GEO-004",
            "title": "PLA Infrastructure Build-Up Near Arunachal — Satellite Data",
            "region": "Eastern LAC / Arunachal",
            "category": "border",
            "probability": 0.80,
            "impact": 0.90,
            "sentiment": SENTIMENT_NEGATIVE,
            "date": "2025-02",
            "summary": (
                "Commercial satellite imagery reveals accelerated village/road construction "
                "within 20km of LAC in Arunachal sector. Elevates threat perception; "
                "supports case for sustained defense acquisition budgets."
            ),
            "tags": ["LAC", "PLA", "Arunachal", "threat", "defense"],
        },

        # ── iCET Technology Cooperation ───────────────────────────────────────
        {
            "id": "GEO-005",
            "title": "US-India iCET: GE F414 Engine ToT Agreement Signed",
            "region": "USA / India",
            "category": "technology",
            "probability": 0.88,
            "impact": 0.92,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-01",
            "summary": (
                "GE Aerospace signs Transfer of Technology agreement for F414 jet engine "
                "under iCET framework. HAL Koraput to co-produce. Major milestone for "
                "Make-in-India defense and dual-use tech ecosystem."
            ),
            "tags": ["iCET", "defense", "technology", "HAL", "GE"],
        },
        {
            "id": "GEO-006",
            "title": "iCET Semiconductor MoU: India Fab Feasibility Study Launched",
            "region": "USA / India",
            "category": "technology",
            "probability": 0.60,
            "impact": 0.80,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-02",
            "summary": (
                "Micron, Applied Materials join India fab feasibility study under iCET. "
                "Positive for domestic chip ecosystem; long-term tailwind for Indian IT "
                "services and EMS companies."
            ),
            "tags": ["iCET", "semiconductor", "technology", "IT"],
        },

        # ── Crude Oil Risks ───────────────────────────────────────────────────
        {
            "id": "GEO-007",
            "title": "Houthi Red Sea Disruption Spikes Brent — India Crude Import Cost Rises",
            "region": "Red Sea / Gulf of Aden",
            "category": "crude_oil",
            "probability": 0.75,
            "impact": 0.85,
            "sentiment": SENTIMENT_NEGATIVE,
            "date": "2025-01",
            "summary": (
                "Sustained Houthi attacks force rerouting via Cape of Good Hope, adding "
                "$3-5/bbl freight premium. India's oil import bill pressured. Aviation, "
                "paints, and petrochemical downstream face margin compression."
            ),
            "tags": ["crude", "Red Sea", "Houthi", "energy", "aviation", "inflation"],
        },
        {
            "id": "GEO-008",
            "title": "India-Russia Rupee-Rouble Oil Deal Extended — Discount Maintained",
            "region": "Russia / India",
            "category": "energy",
            "probability": 0.82,
            "impact": 0.70,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-01",
            "summary": (
                "India-Russia bilateral extends Ural crude discount at ~$4/bbl below Brent. "
                "ONGC's upstream segment benefits from favorable input costs for refining JVs. "
                "Geopolitical dependency risk remains; US secondary sanction risk a tail risk."
            ),
            "tags": ["crude", "Russia", "ONGC", "energy", "sanctions"],
        },

        # ── BRICS Developments ────────────────────────────────────────────────
        {
            "id": "GEO-009",
            "title": "BRICS+ De-Dollarisation Push: India Signals Cautious Stance",
            "region": "Multilateral / Global",
            "category": "multilateral",
            "probability": 0.55,
            "impact": 0.75,
            "sentiment": SENTIMENT_NEUTRAL,
            "date": "2025-02",
            "summary": (
                "India reiterates non-alignment on dollar replacement rhetoric within BRICS+. "
                "Prioritises bilateral settlement mechanisms over structural reserve currency shift. "
                "Neutral short-term market impact; long-term FPI flows monitoring warranted."
            ),
            "tags": ["BRICS", "de-dollarisation", "currency", "multilateral"],
        },
        {
            "id": "GEO-010",
            "title": "BRICS Energy Compact: India Pushes for Clean Energy Technology Transfer",
            "region": "Multilateral / Global",
            "category": "multilateral",
            "probability": 0.63,
            "impact": 0.68,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-02",
            "summary": (
                "India tables clean energy tech transfer agenda at BRICS energy ministers meet. "
                "Positive signal for domestic renewable and green hydrogen ecosystem. "
                "ONGC's green energy pivot may receive multilateral financing support."
            ),
            "tags": ["BRICS", "energy", "green", "ONGC", "multilateral"],
        },

        # ── Additional Diplomacy ──────────────────────────────────────────────
        {
            "id": "GEO-011",
            "title": "Quad Strengthens Maritime Domain Awareness — ISRO Satellite Data Shared",
            "region": "Indo-Pacific",
            "category": "diplomacy",
            "probability": 0.78,
            "impact": 0.72,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-01",
            "summary": (
                "Quad nations formalise real-time satellite AIS data sharing for IOR maritime "
                "surveillance. ISRO's NavIC role elevated. Positive for dual-use space and "
                "defense electronics sectors."
            ),
            "tags": ["Quad", "Indo-Pacific", "maritime", "ISRO", "defense"],
        },
        {
            "id": "GEO-012",
            "title": "India-EU FTA Talks Accelerate — IT Services Mobility Chapter Key",
            "region": "Europe / India",
            "category": "trade",
            "probability": 0.50,
            "impact": 0.80,
            "sentiment": SENTIMENT_POSITIVE,
            "date": "2025-02",
            "summary": (
                "India-EU Free Trade Agreement negotiations show progress on professional mobility "
                "chapter — critical for Indian IT services visa facilitation. "
                "TCS, Infosys, and Wipro among key beneficiaries if visa caps eased."
            ),
            "tags": ["FTA", "EU", "IT", "TCS", "Infosys", "trade"],
        },
    ]


def get_news_by_category(category: str) -> list[dict]:
    """Filter news feed by category."""
    return [n for n in get_news_feed() if n["category"] == category]


def get_news_by_sentiment(sentiment: str) -> list[dict]:
    """Filter news feed by sentiment tag."""
    return [n for n in get_news_feed() if n["sentiment"] == sentiment]


def get_risk_matrix_data() -> list[dict]:
    """Return flattened list suitable for Risk Matrix scatter plot."""
    return [
        {
            "id":          n["id"],
            "label":       n["title"][:55] + "…" if len(n["title"]) > 55 else n["title"],
            "probability": n["probability"],
            "impact":      n["impact"],
            "sentiment":   n["sentiment"],
            "category":    n["category"],
            "region":      n["region"],
        }
        for n in get_news_feed()
    ]
