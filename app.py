# app.py
# ═════════════════════════════════════════════════════════════════════════════
# BHARAT GEOPOLITIC-ALPHA DASHBOARD (MVP VERSION)
# Senior Full-Stack Developer + Financial Data Scientist Implementation
# ─────────────────────────────────────────────────────────────────────────────
# ⚠  INFORMATIONAL & RESEARCH USE ONLY — NOT INVESTMENT ADVICE
# ⚠  Market data via yfinance (prototype) — not suitable for trading decisions
# ⚠  Geopolitical feed is placeholder JSON — not live news intelligence
# ═════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ── Internal modules ──────────────────────────────────────────────────────────
from modules.market_data     import get_all_market_summary, get_nifty_sensex_comparison
from modules.geo_data         import get_news_feed, get_risk_matrix_data
from modules.alpha_engine     import run_sentiment_engine, get_sector_color, get_signal_emoji
from modules.visualizations   import (
    build_risk_matrix,
    build_sectoral_heatmap,
    build_index_comparison,
    build_stock_trend,
    build_category_risk_bars,
)
from modules.executive_brief  import generate_executive_brief

# ═════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & GLOBAL STYLES
# ═════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Bharat Geopolitic-Alpha Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Import fonts ── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* ── Base theme overrides ── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #0D1117;
    color: #E6EDF3;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #161B22;
    border-right: 1px solid #21262D;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 8px;
    padding: 1rem;
}

/* ── Dividers ── */
hr { border-color: #21262D; }

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Custom scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D1117; }
::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }

/* ── Tag / badge styles ── */
.geo-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 1px;
    font-weight: 500;
    text-transform: uppercase;
}
.tag-positive { background: rgba(0,192,118,0.15); color: #00C076; border: 1px solid rgba(0,192,118,0.3); }
.tag-negative { background: rgba(255,51,85,0.15);  color: #FF3355; border: 1px solid rgba(255,51,85,0.3); }
.tag-neutral  { background: rgba(255,184,0,0.12);  color: #FFB800; border: 1px solid rgba(255,184,0,0.3); }

/* ── Brief sections ── */
.brief-box {
    background: #161B22;
    border: 1px solid #21262D;
    border-left: 3px solid #388BFD;
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    margin: 0.75rem 0;
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1.7;
}
.brief-bluf {
    border-left-color: #FFB800;
    font-size: 0.95rem;
}
.signal-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.pill-bullish { background: rgba(0,192,118,0.2);  color: #00C076; }
.pill-bearish { background: rgba(255,51,85,0.2);   color: #FF3355; }
.pill-watch   { background: rgba(255,184,0,0.2);   color: #FFB800; }
.pill-neutral { background: rgba(107,114,128,0.2); color: #9CA3AF; }

/* ── Prototype banner ── */
.proto-banner {
    background: rgba(255,184,0,0.1);
    border: 1px solid rgba(255,184,0,0.4);
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #FFB800;
    text-align: center;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}

/* ── Section headers ── */
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 4px;
    color: #8B949E;
    text-transform: uppercase;
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #21262D;
}

/* ── Footer ── */
.footer-disclaimer {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 6px;
    padding: 1rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #6B7280;
    line-height: 1.6;
    text-align: center;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# DATA LOADING (cached)
# ═════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=900, show_spinner=False)
def load_all_data():
    """Master data loader — cached for 15 minutes."""
    market_summary = get_all_market_summary()
    news_feed      = get_news_feed()
    engine_output  = run_sentiment_engine(news_feed)
    risk_data      = get_risk_matrix_data()
    return market_summary, news_feed, engine_output, risk_data


def get_tag_html(sentiment: str) -> str:
    return f'<span class="geo-tag tag-{sentiment}">{sentiment}</span>'


def get_pill_html(signal: str) -> str:
    css = {
        "BULLISH": "pill-bullish",
        "BEARISH": "pill-bearish",
        "WATCH":   "pill-watch",
        "NEUTRAL": "pill-neutral",
    }.get(signal, "pill-neutral")
    return f'<span class="signal-pill {css}">{signal}</span>'


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem;">
        <div style="font-size:2rem;">🇮🇳</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    letter-spacing:3px; color:#8B949E; margin-top:0.25rem;">
            BHARAT GEOPOLITIC-ALPHA
        </div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.1rem;
                    font-weight:600; color:#E6EDF3; margin-top:0.1rem;">
            MVP Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        options=[
            "📊  Market Overview",
            "🌐  Geopolitical Intelligence",
            "⚡  Risk Matrix",
            "📋  Executive Brief",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # ── Quick market status ────────────────────────────────────────────────
    st.markdown('<div class="section-header">LIVE STATUS</div>', unsafe_allow_html=True)
    now = datetime.now()
    ist_hour = (now.hour + 5) % 24 + (1 if (now.minute + 30) >= 60 else 0)
    market_open = 9 <= ist_hour < 16
    status_color = "#00C076" if market_open else "#FF3355"
    status_text  = "MARKET OPEN" if market_open else "MARKET CLOSED"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-top:0.25rem;">
        <div style="width:8px;height:8px;border-radius:50%;background:{status_color};
                    box-shadow:0 0 8px {status_color}"></div>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                     color:{status_color};letter-spacing:1px">{status_text}</span>
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                color:#6B7280;margin-top:0.25rem;">IST {ist_hour:02d}:{now.minute:02d}</div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Controls ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">CONTROLS</div>', unsafe_allow_html=True)
    if st.button("↻ Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # ── Architecture note ─────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                color:#6B7280;line-height:1.8;">
        <div style="color:#8B949E;margin-bottom:0.5rem;letter-spacing:2px;">ARCHITECTURE</div>
        ✓ yfinance (prototype)<br>
        ✓ Rule-based Sentiment Engine<br>
        ✓ Placeholder Geo-Intel Feed<br>
        ○ ML Classifier (future)<br>
        ○ Live News API (future)<br>
        ○ PostgreSQL / TimescaleDB (future)<br>
        ○ Bloomberg / Refinitiv (future)
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ═════════════════════════════════════════════════════════════════════════════

with st.spinner("Loading market + intelligence data…"):
    market_summary, news_feed, engine_output, risk_data = load_all_data()

sector_summary = engine_output.get("sector_summary", {})

# ── Prototype banner (always visible) ─────────────────────────────────────────
st.markdown("""
<div class="proto-banner">
    ⚠ PROTOTYPE — DATA VIA YFINANCE (UNOFFICIAL) · FOR INFORMATIONAL & RESEARCH USE ONLY · NOT INVESTMENT ADVICE
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: MARKET OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────

if "Market Overview" in page:

    st.markdown("## 📊 Market Overview")
    st.markdown(f"*Last updated: {market_summary.get('last_updated', 'N/A')}*")

    if not market_summary.get("data_ok"):
        st.warning("⚠ Market data unavailable. Check connectivity or yfinance status.")

    # ── Index metrics ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">BENCHMARK INDICES</div>', unsafe_allow_html=True)
    idx_cols = st.columns(len(market_summary.get("indices", {})) or 1)
    for col, (name, metrics) in zip(idx_cols, market_summary.get("indices", {}).items()):
        pct   = metrics.get("change_pct", 0)
        price = metrics.get("price", 0)
        col.metric(
            label=f"🇮🇳 {name}",
            value=f"₹{price:,.2f}",
            delta=f"{pct:+.2f}%",
            delta_color="normal",
        )

    st.markdown("---")

    # ── NIFTY vs SENSEX chart ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">INDEX COMPARISON</div>', unsafe_allow_html=True)
    df_norm = get_nifty_sensex_comparison()
    if not df_norm.empty:
        st.plotly_chart(build_index_comparison(df_norm), use_container_width=True)
    else:
        st.info("Index comparison chart unavailable — data loading issue.")

    st.markdown("---")

    # ── Sector stocks ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">SECTORAL STOCKS</div>', unsafe_allow_html=True)

    for sector, stocks in market_summary.get("sectors", {}).items():
        sig_data = sector_summary.get(sector, {})
        sig      = sig_data.get("dominant_signal", "NEUTRAL")
        emoji    = get_signal_emoji(sig)
        conf     = sig_data.get("confidence", 0)
        color    = get_sector_color(sig)

        with st.expander(
            f"{emoji} {sector} — Geo Signal: {sig} ({conf:.0%} confidence)",
            expanded=True,
        ):
            stock_cols = st.columns(len(stocks))
            for col, (stock_name, metrics) in zip(stock_cols, stocks.items()):
                pct   = metrics.get("change_pct", 0)
                price = metrics.get("price", 0)
                sym   = metrics.get("symbol", "")
                col.metric(
                    label=f"{stock_name} ({sym})",
                    value=f"₹{price:,.2f}",
                    delta=f"{pct:+.2f}%",
                )

            # Drill-down chart
            st.markdown("**Stock Trend (1 Month)**")
            drill_cols = st.columns(len(stocks))
            for col, (stock_name, metrics) in zip(drill_cols, stocks.items()):
                sym  = metrics.get("symbol", "")
                hist = market_summary.get("raw_history", {}).get(sym, pd.DataFrame())
                if not hist.empty:
                    with col:
                        st.plotly_chart(
                            build_stock_trend(hist, sym, stock_name),
                            use_container_width=True,
                        )

    st.markdown("---")

    # ── Sectoral heatmap ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">SECTORAL HEATMAP</div>', unsafe_allow_html=True)
    heatmap_fig = build_sectoral_heatmap(market_summary, engine_output)
    st.plotly_chart(heatmap_fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GEOPOLITICAL INTELLIGENCE
# ─────────────────────────────────────────────────────────────────────────────

elif "Geopolitical Intelligence" in page:

    st.markdown("## 🌐 Geopolitical Intelligence Feed")
    st.markdown("*Structured placeholder intelligence feed — India-centric themes*")

    # ── Filter controls ───────────────────────────────────────────────────────
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        categories = ["All"] + sorted(set(n["category"] for n in news_feed))
        sel_cat = st.selectbox("Filter by Category", categories)
    with filter_col2:
        sentiments = ["All", "positive", "negative", "neutral"]
        sel_sent = st.selectbox("Filter by Sentiment", sentiments)
    with filter_col3:
        min_risk = st.slider("Min Risk Score (Prob×Impact)", 0.0, 1.0, 0.0, 0.05)

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered_news = [
        n for n in news_feed
        if (sel_cat  == "All" or n["category"]  == sel_cat)
        and (sel_sent == "All" or n["sentiment"] == sel_sent)
        and (n["probability"] * n["impact"] >= min_risk)
    ]

    st.markdown(f"*Showing {len(filtered_news)} of {len(news_feed)} intelligence items*")
    st.markdown("---")

    # ── News cards ────────────────────────────────────────────────────────────
    for n in filtered_news:
        risk_score = n["probability"] * n["impact"]
        risk_color = "#FF3355" if risk_score > 0.55 else "#FFB800" if risk_score > 0.35 else "#00C076"
        tag_html   = get_tag_html(n["sentiment"])

        with st.container():
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                st.markdown(f"""
                <div style="border:1px solid #21262D;border-left:3px solid {risk_color};
                            border-radius:6px;padding:1rem 1.2rem;margin-bottom:0.75rem;
                            background:#161B22;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.5rem;">
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                     color:#8B949E;">{n['id']}</span>
                        {tag_html}
                        <span class="geo-tag" style="background:rgba(56,139,253,0.1);
                              color:#388BFD;border:1px solid rgba(56,139,253,0.3);">
                            {n['category'].upper()}
                        </span>
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                     color:#6B7280;">📍 {n['region']}</span>
                    </div>
                    <div style="font-weight:600;font-size:0.95rem;margin-bottom:0.5rem;
                                color:#E6EDF3;">{n['title']}</div>
                    <div style="font-size:0.82rem;color:#8B949E;line-height:1.6;">
                        {n['summary']}
                    </div>
                    <div style="display:flex;gap:1.5rem;margin-top:0.75rem;
                                font-family:'JetBrains Mono',monospace;font-size:0.7rem;">
                        <span style="color:#6B7280;">PROB: <span style="color:{risk_color};">
                            {n['probability']:.0%}</span></span>
                        <span style="color:#6B7280;">IMPACT: <span style="color:{risk_color};">
                            {n['impact']:.0%}</span></span>
                        <span style="color:#6B7280;">RISK SCORE: <span style="color:{risk_color};">
                            {risk_score:.2f}</span></span>
                        <span style="color:#6B7280;">DATE: {n['date']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Category risk chart ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">RISK SCORE BY CATEGORY</div>', unsafe_allow_html=True)
    st.plotly_chart(build_category_risk_bars(filtered_news), use_container_width=True)

    # ── Alpha engine signal summary ───────────────────────────────────────────
    st.markdown('<div class="section-header">ALPHA ENGINE — SECTOR SIGNALS</div>', unsafe_allow_html=True)
    sig_cols = st.columns(3)
    for col, sector in zip(sig_cols, ["Defense", "Energy", "IT"]):
        sig_data = sector_summary.get(sector, {})
        sig      = sig_data.get("dominant_signal", "NEUTRAL")
        conf     = sig_data.get("confidence", 0)
        color    = get_sector_color(sig)
        emoji    = get_signal_emoji(sig)
        pill     = get_pill_html(sig)
        col.markdown(f"""
        <div style="background:#161B22;border:1px solid #21262D;border-top:2px solid {color};
                    border-radius:6px;padding:1rem;text-align:center;">
            <div style="font-size:1.5rem;margin-bottom:0.3rem;">{emoji}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                        color:#8B949E;letter-spacing:2px;">{sector.upper()}</div>
            <div style="margin:0.5rem 0;">{pill}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;
                        color:{color};">{conf:.0%} conf</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                        color:#6B7280;margin-top:0.25rem;">
                {sig_data.get('item_count', 0)} signals
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RISK MATRIX
# ─────────────────────────────────────────────────────────────────────────────

elif "Risk Matrix" in page:

    st.markdown("## ⚡ Geopolitical Risk Matrix")
    st.markdown("*Probability × Impact positioning of all tracked intelligence items*")

    # ── Main risk matrix ──────────────────────────────────────────────────────
    st.plotly_chart(build_risk_matrix(risk_data), use_container_width=True)

    st.markdown("---")

    # ── Legend & interpretation ───────────────────────────────────────────────
    st.markdown('<div class="section-header">MATRIX LEGEND</div>', unsafe_allow_html=True)
    leg_cols = st.columns(3)
    for col, (zone, color, desc) in zip(leg_cols, [
        ("LOW RISK",    "#00C076", "Prob < 0.33 OR Impact < 0.33 — Monitor routine"),
        ("MEDIUM RISK", "#FFB800", "Prob 0.33–0.66 × Impact 0.33–0.66 — Active Watch"),
        ("HIGH RISK",   "#FF3355", "Prob > 0.66 AND Impact > 0.66 — Immediate Attention"),
    ]):
        col.markdown(f"""
        <div style="background:#161B22;border:1px solid #21262D;border-left:3px solid {color};
                    border-radius:6px;padding:0.75rem 1rem;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                        color:{color};font-weight:600;margin-bottom:0.3rem;">{zone}</div>
            <div style="font-size:0.8rem;color:#8B949E;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── High-risk items table ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">HIGH-RISK ITEMS (Score > 0.55)</div>', unsafe_allow_html=True)
    high_risk = [
        n for n in news_feed
        if n["probability"] * n["impact"] > 0.55
    ]
    high_risk.sort(key=lambda x: x["probability"] * x["impact"], reverse=True)

    if high_risk:
        df_risk = pd.DataFrame([{
            "ID":        n["id"],
            "Title":     n["title"][:70] + "…" if len(n["title"]) > 70 else n["title"],
            "Category":  n["category"].upper(),
            "Region":    n["region"],
            "Prob":      f"{n['probability']:.0%}",
            "Impact":    f"{n['impact']:.0%}",
            "Score":     f"{n['probability'] * n['impact']:.2f}",
            "Sentiment": n["sentiment"].upper(),
        } for n in high_risk])
        st.dataframe(
            df_risk,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("✅ No high-risk items currently in the intelligence feed.")

    st.markdown("---")

    # ── Signal distribution ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">ENGINE SIGNAL DISTRIBUTION</div>', unsafe_allow_html=True)
    all_signals = engine_output.get("all_signals", [])
    if all_signals:
        from collections import Counter
        sig_counts = Counter(s["signal"] for s in all_signals)
        dist_cols  = st.columns(4)
        for col, (sig, count) in zip(dist_cols, sig_counts.items()):
            color = get_sector_color(sig)
            emoji = get_signal_emoji(sig)
            col.markdown(f"""
            <div style="background:#161B22;border:1px solid {color}33;
                        border-radius:6px;padding:1rem;text-align:center;">
                <div style="font-size:1.5rem;">{emoji}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;
                            color:{color};font-weight:600;">{count}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                            color:#8B949E;letter-spacing:2px;">{sig}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: EXECUTIVE BRIEF
# ─────────────────────────────────────────────────────────────────────────────

elif "Executive Brief" in page:

    st.markdown("## 📋 Executive Brief Generator")
    st.markdown("*Template-based BLUF intelligence summary — not ML-generated, not investment advice*")

    # ── Generate button ───────────────────────────────────────────────────────
    col_btn, col_info = st.columns([0.25, 0.75])
    with col_btn:
        generate = st.button("🚀 Generate Executive Brief", use_container_width=True, type="primary")
    with col_info:
        st.markdown("""
        <div style="padding:0.6rem;font-size:0.8rem;color:#8B949E;">
            Generates a structured BLUF-style brief from geopolitical signals and market data.
            Uses deterministic template logic — no LLM, no ML model.
        </div>
        """, unsafe_allow_html=True)

    if generate or st.session_state.get("brief_generated"):
        st.session_state["brief_generated"] = True

        with st.spinner("Generating executive brief…"):
            brief = generate_executive_brief(market_summary, engine_output, news_feed)

        meta = brief["metadata"]
        risk = brief["risk_level"]
        risk_colors = {"ELEVATED": "#FF3355", "MODERATE": "#FFB800", "CONTAINED": "#00C076"}
        risk_color  = risk_colors.get(risk, "#8B949E")

        # ── Header ─────────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:#161B22;border:1px solid #21262D;border-radius:8px;
                    padding:1.5rem;margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                color:#8B949E;letter-spacing:3px;margin-bottom:0.3rem;">
                        BHARAT GEOPOLITIC-ALPHA · EXECUTIVE INTELLIGENCE BRIEF
                    </div>
                    <div style="font-size:1.2rem;font-weight:700;color:#E6EDF3;">
                        India Geopolitical Risk Assessment
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                                color:#6B7280;margin-top:0.3rem;">
                        Generated: {meta['generated_at']} · {meta['news_count']} intelligence items ·
                        {meta['signal_count']} sector signals
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                color:#8B949E;letter-spacing:2px;margin-bottom:0.3rem;">RISK LEVEL</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.3rem;
                                font-weight:700;color:{risk_color};">{risk}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                                color:#6B7280;">Score: {meta['avg_risk_score']:.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Market snapshot ─────────────────────────────────────────────────────
        snap_cols = st.columns(len(brief["market_snapshot"]) or 1)
        for col, snap in zip(snap_cols, brief["market_snapshot"]):
            pct   = snap["change_pct"]
            color = "#00C076" if pct >= 0 else "#FF3355"
            col.markdown(f"""
            <div style="background:#0D1117;border:1px solid #21262D;border-radius:6px;
                        padding:0.75rem;text-align:center;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                            color:#8B949E;">{snap['name']}</div>
                <div style="font-size:1.1rem;font-weight:600;color:#E6EDF3;margin:0.2rem 0;">
                    ₹{snap['price']:,.2f}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;
                            color:{color};">{pct:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # ── BLUF ───────────────────────────────────────────────────────────────
        st.markdown('<div class="section-header">BLUF — BOTTOM LINE UP FRONT</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="brief-box brief-bluf">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                        color:#FFB800;letter-spacing:2px;margin-bottom:0.5rem;">ASSESSMENT</div>
            {brief['bluf']}
        </div>
        """, unsafe_allow_html=True)

        # ── Key Drivers ─────────────────────────────────────────────────────────
        st.markdown('<div class="section-header">KEY DRIVERS</div>', unsafe_allow_html=True)
        for i, driver in enumerate(brief["key_drivers"], 1):
            dir_color = {"↑": "#00C076", "↓": "#FF3355", "→": "#FFB800"}.get(driver["direction"], "#8B949E")
            tag_html  = get_tag_html(driver["sentiment"])
            st.markdown(f"""
            <div style="display:flex;gap:1rem;align-items:flex-start;
                        padding:0.75rem 0;border-bottom:1px solid #21262D;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;
                            color:{dir_color};min-width:20px;">{driver['direction']}</div>
                <div style="flex:1;">
                    <div style="font-size:0.9rem;font-weight:500;color:#E6EDF3;margin-bottom:0.25rem;">
                        {driver['title']}</div>
                    <div style="display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap;">
                        {tag_html}
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                     color:#6B7280;">📍 {driver['region']}</span>
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                     color:#6B7280;">RISK: {driver['risk_score']:.2f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Sectoral Impact ─────────────────────────────────────────────────────
        st.markdown('<div class="section-header">SECTORAL IMPACT</div>', unsafe_allow_html=True)
        for impact in brief["sectoral_impact"]:
            color = get_sector_color(impact["signal"])
            pill  = get_pill_html(impact["signal"])
            st.markdown(f"""
            <div class="brief-box" style="border-left-color:{color};">
                <div style="display:flex;justify-content:space-between;align-items:center;
                            margin-bottom:0.5rem;">
                    <div style="font-weight:600;font-size:0.9rem;">
                        {impact['emoji']} {impact['sector']}
                    </div>
                    <div style="display:flex;align-items:center;gap:0.75rem;">
                        {pill}
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                     color:#6B7280;">{impact['confidence']:.0%} conf</span>
                    </div>
                </div>
                <div style="font-size:0.82rem;color:#8B949E;line-height:1.6;">
                    {impact['rationale']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Investor Signals ────────────────────────────────────────────────────
        st.markdown('<div class="section-header">INVESTOR SIGNAL SUMMARY</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(255,184,0,0.08);border:1px solid rgba(255,184,0,0.3);
                    border-radius:6px;padding:0.6rem 1rem;margin-bottom:1rem;
                    font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#FFB800;">
            ⚠ The following signals are for informational & research use only.
            They do NOT constitute investment recommendations or financial advice.
        </div>
        """, unsafe_allow_html=True)

        inv_cols = st.columns(3)
        for col, inv in zip(inv_cols, brief["investor_signals"]):
            color = get_sector_color(inv["signal"])
            pill  = get_pill_html(inv["signal"])
            col.markdown(f"""
            <div style="background:#161B22;border:1px solid #21262D;border-top:2px solid {color};
                        border-radius:6px;padding:1rem;height:100%;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                    <div style="font-weight:600;font-size:0.9rem;">{inv['emoji']} {inv['sector']}</div>
                    {pill}
                </div>
                <div style="font-size:0.8rem;color:#8B949E;line-height:1.6;">{inv['message']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Metadata footer ─────────────────────────────────────────────────────
        st.markdown("---")
        with st.expander("Brief Metadata & Data Provenance"):
            st.json(meta)


# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL FOOTER
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="footer-disclaimer">
    <div style="color:#8B949E;font-weight:500;margin-bottom:0.4rem;letter-spacing:2px;">
        ⚠ DISCLAIMER
    </div>
    This dashboard is for <strong>informational and research purposes only</strong>.
    It does not constitute financial, investment, legal, or strategic advice.
    Market data is sourced via yfinance (unofficial, prototype-grade) and may be
    delayed or inaccurate. Geopolitical intelligence items are placeholder data —
    not live news intelligence. Sector signals are generated by deterministic
    rule-based logic; they do not predict future market movements.
    Past geopolitical patterns are not indicative of future outcomes.
    Always consult qualified financial and strategic advisors before making decisions.
    <br><br>
    <span style="color:#6B7280;">
        Bharat Geopolitic-Alpha Dashboard · MVP Version · Built with Streamlit + yfinance + Plotly
        · Not affiliated with NSE, BSE, SEBI, or any government body
    </span>
</div>
""", unsafe_allow_html=True)
