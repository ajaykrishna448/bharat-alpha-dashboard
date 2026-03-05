# modules/alpha_engine.py
# ─────────────────────────────────────────────────────────────────────────────
# ALPHA SENTIMENT ENGINE — RULE-BASED
# Maps geopolitical news categories + sentiment → sector impact signals.
# ⚠ RULE-BASED ONLY — no ML, no investment recommendations.
# Future: Replace rules with trained NLP classifier + signal scoring model.
# ─────────────────────────────────────────────────────────────────────────────

from modules.geo_data import (
    get_news_feed,
    SENTIMENT_POSITIVE,
    SENTIMENT_NEGATIVE,
    SENTIMENT_NEUTRAL,
)

# ── Signal constants ──────────────────────────────────────────────────────────
SIGNAL_BULLISH  = "BULLISH"
SIGNAL_BEARISH  = "BEARISH"
SIGNAL_NEUTRAL  = "NEUTRAL"
SIGNAL_WATCH    = "WATCH"   # elevated monitoring — not directional

# ── Rule Table: (category, sentiment) → {sector: signal, rationale} ──────────
# Each rule is a tuple key mapping to a list of sector-signal records.
# Extend this table to add new rules without touching engine logic.

RULE_TABLE: dict[tuple, list[dict]] = {

    # ── Defense ──────────────────────────────────────────────────────────────
    ("defense", SENTIMENT_POSITIVE): [
        {"sector": "Defense", "signal": SIGNAL_BULLISH,
         "rationale": "Positive defense news signals sustained capex; HAL/BEL order flows supported."},
    ],
    ("defense", SENTIMENT_NEGATIVE): [
        {"sector": "Defense", "signal": SIGNAL_WATCH,
         "rationale": "Negative defense development warrants monitoring; short-term sentiment drag possible."},
    ],
    ("border", SENTIMENT_POSITIVE): [
        {"sector": "Defense", "signal": SIGNAL_BULLISH,
         "rationale": "Easing border tensions: no procurement reduction expected; sentiment positive."},
    ],
    ("border", SENTIMENT_NEGATIVE): [
        {"sector": "Defense", "signal": SIGNAL_BULLISH,
         "rationale": "Heightened border tensions typically accelerate defense procurement. HAL/BEL positive."},
    ],

    # ── Energy ───────────────────────────────────────────────────────────────
    ("energy", SENTIMENT_POSITIVE): [
        {"sector": "Energy", "signal": SIGNAL_BULLISH,
         "rationale": "Favourable energy geo-event supports ONGC/Reliance upstream margins."},
    ],
    ("energy", SENTIMENT_NEGATIVE): [
        {"sector": "Energy",   "signal": SIGNAL_BEARISH,
         "rationale": "Negative energy development pressures upstream realisation."},
        {"sector": "IT",       "signal": SIGNAL_NEUTRAL,
         "rationale": "Indirect inflationary pressure on IT discretionary spending — monitor."},
    ],
    ("crude_oil", SENTIMENT_NEGATIVE): [
        {"sector": "Energy",   "signal": SIGNAL_WATCH,
         "rationale": "Crude spike risk: ONGC gains on upstream, Reliance refining margins mixed."},
        {"sector": "Aviation", "signal": SIGNAL_BEARISH,
         "rationale": "ATF cost spike pressure on aviation sector (IndiGo, Air India — not tracked here)."},
        {"sector": "Paints",   "signal": SIGNAL_BEARISH,
         "rationale": "Crude-linked feedstock cost pressure on paints (Asian Paints etc. — not tracked here)."},
    ],
    ("crude_oil", SENTIMENT_POSITIVE): [
        {"sector": "Energy",   "signal": SIGNAL_NEUTRAL,
         "rationale": "Crude decline mixed for ONGC (lower realisations) but positive for downstream."},
    ],

    # ── Technology / IT ──────────────────────────────────────────────────────
    ("technology", SENTIMENT_POSITIVE): [
        {"sector": "IT", "signal": SIGNAL_BULLISH,
         "rationale": "Tech cooperation positive: iCET/FTA tailwinds for TCS/Infosys deal pipeline."},
    ],
    ("technology", SENTIMENT_NEGATIVE): [
        {"sector": "IT", "signal": SIGNAL_BEARISH,
         "rationale": "Tech friction risk: export controls or visa tightening may pressure IT earnings."},
    ],

    # ── Trade ────────────────────────────────────────────────────────────────
    ("trade", SENTIMENT_POSITIVE): [
        {"sector": "IT",     "signal": SIGNAL_BULLISH,
         "rationale": "Trade corridor positive: IT services export revenue supported."},
        {"sector": "Energy", "signal": SIGNAL_BULLISH,
         "rationale": "Trade route stability supports energy supply chains."},
    ],
    ("trade", SENTIMENT_NEGATIVE): [
        {"sector": "IT",     "signal": SIGNAL_WATCH,
         "rationale": "Trade disruption risk: monitor IT deal closure timelines."},
        {"sector": "Energy", "signal": SIGNAL_BEARISH,
         "rationale": "Trade friction may elevate energy import costs."},
    ],

    # ── Diplomacy ────────────────────────────────────────────────────────────
    ("diplomacy", SENTIMENT_POSITIVE): [
        {"sector": "Defense", "signal": SIGNAL_BULLISH,
         "rationale": "Diplomatic wins often accompany defense co-production deals."},
        {"sector": "Energy",  "signal": SIGNAL_BULLISH,
         "rationale": "Improved bilateral = better energy supply terms for India."},
    ],
    ("diplomacy", SENTIMENT_NEGATIVE): [
        {"sector": "Defense", "signal": SIGNAL_WATCH,
         "rationale": "Diplomatic setback: assess impact on joint programs."},
    ],

    # ── Multilateral ─────────────────────────────────────────────────────────
    ("multilateral", SENTIMENT_POSITIVE): [
        {"sector": "Energy", "signal": SIGNAL_BULLISH,
         "rationale": "Multilateral clean energy pact: ONGC green pivot financing supported."},
        {"sector": "IT",     "signal": SIGNAL_NEUTRAL,
         "rationale": "Tech transfer clauses may benefit domestic semiconductor ecosystem long-term."},
    ],
    ("multilateral", SENTIMENT_NEUTRAL): [
        {"sector": "IT",     "signal": SIGNAL_NEUTRAL,
         "rationale": "Neutral multilateral developments: no immediate market catalyst."},
        {"sector": "Energy", "signal": SIGNAL_NEUTRAL,
         "rationale": "Monitoring BRICS+ currency developments for FPI flow implications."},
    ],
}

# ── Engine Core ───────────────────────────────────────────────────────────────

def run_sentiment_engine(news_feed: list[dict] | None = None) -> dict:
    """
    Processes news feed through rule table.
    Returns: {
        "sector_signals":  {sector_name: {signal, score, items}},
        "all_signals":     [flat list of all triggered rules],
        "sector_summary":  {sector_name: dominant_signal},
    }
    """
    if news_feed is None:
        news_feed = get_news_feed()

    sector_signals: dict[str, list[dict]] = {}
    all_signals: list[dict] = []

    for news in news_feed:
        cat  = news.get("category", "")
        sent = news.get("sentiment", "")
        prob = news.get("probability", 0.5)
        imp  = news.get("impact", 0.5)
        weight = prob * imp  # composite weight

        rules = RULE_TABLE.get((cat, sent), [])
        for rule in rules:
            sector  = rule["sector"]
            signal  = rule["signal"]
            item = {
                "news_id":   news["id"],
                "news_title": news["title"],
                "sector":    sector,
                "signal":    signal,
                "weight":    weight,
                "rationale": rule["rationale"],
                "category":  cat,
                "sentiment": sent,
            }
            all_signals.append(item)
            sector_signals.setdefault(sector, []).append(item)

    # ── Aggregate to dominant signal per sector ───────────────────────────────
    sector_summary: dict[str, dict] = {}
    for sector, items in sector_signals.items():
        score_map = {
            SIGNAL_BULLISH: 0.0,
            SIGNAL_BEARISH: 0.0,
            SIGNAL_WATCH:   0.0,
            SIGNAL_NEUTRAL: 0.0,
        }
        for item in items:
            score_map[item["signal"]] += item["weight"]

        dominant = max(score_map, key=lambda k: score_map[k])
        total    = sum(score_map.values()) or 1
        confidence = score_map[dominant] / total

        sector_summary[sector] = {
            "dominant_signal": dominant,
            "confidence":      round(confidence, 2),
            "score_map":       score_map,
            "item_count":      len(items),
        }

    return {
        "sector_signals":  sector_signals,
        "all_signals":     all_signals,
        "sector_summary":  sector_summary,
    }


def get_sector_color(signal: str) -> str:
    """Maps signal string to hex color for UI rendering."""
    return {
        SIGNAL_BULLISH: "#00C076",  # green
        SIGNAL_BEARISH: "#FF3355",  # red
        SIGNAL_WATCH:   "#FFB800",  # amber
        SIGNAL_NEUTRAL: "#6B7280",  # grey
    }.get(signal, "#6B7280")


def get_sentiment_color(sentiment: str) -> str:
    """Maps sentiment to hex color."""
    return {
        SENTIMENT_POSITIVE: "#00C076",
        SENTIMENT_NEGATIVE: "#FF3355",
        SENTIMENT_NEUTRAL:  "#FFB800",
    }.get(sentiment, "#6B7280")


def get_signal_emoji(signal: str) -> str:
    return {
        SIGNAL_BULLISH: "🟢",
        SIGNAL_BEARISH: "🔴",
        SIGNAL_WATCH:   "🟡",
        SIGNAL_NEUTRAL: "⚪",
    }.get(signal, "⚪")
