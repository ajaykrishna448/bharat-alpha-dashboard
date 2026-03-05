# modules/executive_brief.py
# ─────────────────────────────────────────────────────────────────────────────
# EXECUTIVE BRIEF GENERATOR — TEMPLATE-BASED
# Produces BLUF-style structured intelligence summary.
# ⚠ TEMPLATE LOGIC ONLY — no LLM, no ML, no investment advice.
# Future: Wire to LLM (Claude API) for dynamic narrative generation.
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime
from modules.alpha_engine import (
    SIGNAL_BULLISH, SIGNAL_BEARISH, SIGNAL_WATCH, SIGNAL_NEUTRAL,
    get_signal_emoji,
)
from modules.geo_data import SENTIMENT_POSITIVE, SENTIMENT_NEGATIVE


# ── BLUF Templates ────────────────────────────────────────────────────────────

BLUF_TEMPLATES = {
    "risk_elevated": (
        "India's geopolitical risk landscape is ELEVATED this period. "
        "Multiple high-impact vectors — particularly {top_risk_categories} — "
        "are intersecting with active market sensitivity. "
        "Selective sectoral caution is warranted; {bullish_sectors} present "
        "constructive positioning against a backdrop of {bearish_sectors} headwinds."
    ),
    "risk_moderate": (
        "India's geopolitical environment remains MODERATELY COMPLEX. "
        "Key catalysts centred on {top_risk_categories} present mixed vectors. "
        "Sectoral divergence is expected: {bullish_sectors} are supported by "
        "structural tailwinds while {bearish_sectors} face near-term pressure."
    ),
    "risk_contained": (
        "India's geopolitical risk profile is BROADLY CONTAINED. "
        "Constructive developments in {top_risk_categories} support stable "
        "market conditions. {bullish_sectors} exhibit positive momentum; "
        "near-term risk factors remain manageable."
    ),
}

INVESTOR_SIGNAL_MAP = {
    "Defense": {
        SIGNAL_BULLISH: "Defense sector: Monitor HAL and BEL for order book updates. Sustained procurement pipeline positive.",
        SIGNAL_BEARISH: "Defense sector: Short-term sentiment drag; monitor quarterly results for execution signals.",
        SIGNAL_WATCH:   "Defense sector: Heightened monitoring warranted. Volatility possible around event resolution.",
        SIGNAL_NEUTRAL: "Defense sector: No material near-term catalyst. Maintain existing positioning.",
    },
    "Energy": {
        SIGNAL_BULLISH: "Energy sector: ONGC upstream realisations supported. Reliance integrated model buffers volatility.",
        SIGNAL_BEARISH: "Energy sector: Margin pressure likely. Monitor crude benchmarks and forex closely.",
        SIGNAL_WATCH:   "Energy sector: Risk-reward asymmetric. Crude spike scenario warrants partial hedge.",
        SIGNAL_NEUTRAL: "Energy sector: Balanced risk. No immediate catalyst; await policy direction.",
    },
    "IT": {
        SIGNAL_BULLISH: "IT sector: Deal pipeline tailwinds via iCET/FTA progress. TCS and Infosys well-positioned.",
        SIGNAL_BEARISH: "IT sector: Macro/visa headwinds possible. Monitor guidance revisions.",
        SIGNAL_WATCH:   "IT sector: Monitor discretionary spending trends amid global uncertainty.",
        SIGNAL_NEUTRAL: "IT sector: Stable. No near-term geopolitical catalyst; fundamentals drive.",
    },
}


# ── Brief Generator ───────────────────────────────────────────────────────────

def generate_executive_brief(
    market_summary: dict,
    engine_output: dict,
    news_feed: list[dict],
) -> dict:
    """
    Generates structured BLUF executive brief.
    Returns: {bluf, key_drivers, sectoral_impact, investor_signals, metadata}
    """
    sector_summary = engine_output.get("sector_summary", {})
    all_signals    = engine_output.get("all_signals", [])

    # ── Determine overall risk level ──────────────────────────────────────────
    avg_risk = (
        sum(n["probability"] * n["impact"] for n in news_feed) / len(news_feed)
        if news_feed else 0.5
    )
    if avg_risk >= 0.55:
        risk_level = "risk_elevated"
        risk_label = "ELEVATED"
    elif avg_risk >= 0.40:
        risk_level = "risk_moderate"
        risk_label = "MODERATE"
    else:
        risk_level = "risk_contained"
        risk_label = "CONTAINED"

    # ── Identify key categories ───────────────────────────────────────────────
    from collections import Counter
    cat_counts = Counter(n["category"] for n in news_feed)
    top_categories = [c.upper() for c, _ in cat_counts.most_common(3)]

    bullish_sectors = [
        s for s, d in sector_summary.items()
        if d.get("dominant_signal") == SIGNAL_BULLISH
    ]
    bearish_sectors = [
        s for s, d in sector_summary.items()
        if d.get("dominant_signal") == SIGNAL_BEARISH
    ]
    watch_sectors = [
        s for s, d in sector_summary.items()
        if d.get("dominant_signal") == SIGNAL_WATCH
    ]

    # ── BLUF paragraph ────────────────────────────────────────────────────────
    bluf = BLUF_TEMPLATES[risk_level].format(
        top_risk_categories=", ".join(top_categories) or "TRADE, BORDER, ENERGY",
        bullish_sectors=", ".join(bullish_sectors) or "no clear bullish sector",
        bearish_sectors=", ".join(bearish_sectors) or "no clear bearish sector",
    )

    # ── Key Drivers (top 5 by composite score) ─────────────────────────────────
    scored_news = sorted(
        news_feed,
        key=lambda n: n["probability"] * n["impact"],
        reverse=True,
    )[:5]

    key_drivers = []
    for n in scored_news:
        direction = {
            SENTIMENT_POSITIVE: "↑",
            SENTIMENT_NEGATIVE: "↓",
        }.get(n["sentiment"], "→")
        key_drivers.append({
            "id":         n["id"],
            "direction":  direction,
            "title":      n["title"],
            "category":   n["category"].upper(),
            "region":     n["region"],
            "risk_score": round(n["probability"] * n["impact"], 2),
            "sentiment":  n["sentiment"],
        })

    # ── Sectoral Impact Table ─────────────────────────────────────────────────
    sectoral_impact = []
    for sector, sig_data in sector_summary.items():
        sig        = sig_data.get("dominant_signal", SIGNAL_NEUTRAL)
        confidence = sig_data.get("confidence", 0)
        emoji      = get_signal_emoji(sig)

        # Get relevant news for this sector
        relevant = [
            s["news_title"] for s in all_signals
            if s["sector"] == sector
        ][:2]

        sectoral_impact.append({
            "sector":      sector,
            "signal":      sig,
            "emoji":       emoji,
            "confidence":  confidence,
            "rationale":   "; ".join(relevant[:1]) if relevant else "No direct signal.",
            "item_count":  sig_data.get("item_count", 0),
        })

    # ── Investor Signals ──────────────────────────────────────────────────────
    investor_signals = []
    tracked_sectors = ["Defense", "Energy", "IT"]
    for sector in tracked_sectors:
        sig_data = sector_summary.get(sector, {})
        sig      = sig_data.get("dominant_signal", SIGNAL_NEUTRAL)
        template = INVESTOR_SIGNAL_MAP.get(sector, {}).get(sig, "No signal template available.")
        investor_signals.append({
            "sector":  sector,
            "signal":  sig,
            "emoji":   get_signal_emoji(sig),
            "message": template,
        })

    # ── Market Snapshot ───────────────────────────────────────────────────────
    market_snapshot = []
    for idx_name, metrics in market_summary.get("indices", {}).items():
        market_snapshot.append({
            "name":       idx_name,
            "price":      metrics.get("price", 0),
            "change_pct": metrics.get("change_pct", 0),
        })

    # ── Metadata ──────────────────────────────────────────────────────────────
    metadata = {
        "generated_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        "risk_level":    risk_label,
        "avg_risk_score": round(avg_risk, 2),
        "news_count":    len(news_feed),
        "signal_count":  len(all_signals),
        "data_source":   "Yahoo Finance (prototype) + Placeholder Geo-Intelligence Feed",
        "disclaimer":    (
            "This brief is generated by template-based rule logic for informational "
            "and research purposes only. It does not constitute financial, investment, "
            "or strategic advice. Past geopolitical patterns are not indicative of "
            "future market outcomes."
        ),
    }

    return {
        "bluf":            bluf,
        "risk_level":      risk_label,
        "key_drivers":     key_drivers,
        "sectoral_impact": sectoral_impact,
        "investor_signals": investor_signals,
        "market_snapshot": market_snapshot,
        "metadata":        metadata,
    }
