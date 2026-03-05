# modules/visualizations.py
# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZATION LAYER — All Plotly charts
# Functions return plotly.graph_objects.Figure objects for rendering in Streamlit.
# ─────────────────────────────────────────────────────────────────────────────

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from modules.alpha_engine import get_sentiment_color, get_sector_color

# ── Theme constants ────────────────────────────────────────────────────────────
BG_COLOR      = "#0D1117"
SURFACE_COLOR = "#161B22"
GRID_COLOR    = "#21262D"
TEXT_COLOR    = "#E6EDF3"
MUTED_COLOR   = "#8B949E"
ACCENT_GREEN  = "#00C076"
ACCENT_RED    = "#FF3355"
ACCENT_BLUE   = "#388BFD"
ACCENT_AMBER  = "#FFB800"

BASE_LAYOUT = dict(
    paper_bgcolor=BG_COLOR,
    plot_bgcolor=SURFACE_COLOR,
    font=dict(family="JetBrains Mono, Courier New, monospace", color=TEXT_COLOR, size=11),
    margin=dict(l=50, r=30, t=50, b=40),
    legend=dict(
        bgcolor="rgba(22,27,34,0.8)",
        bordercolor=GRID_COLOR,
        borderwidth=1,
    ),
)

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor=GRID_COLOR,
    zeroline=False,
    tickfont=dict(color=MUTED_COLOR, size=10),
    titlefont=dict(color=MUTED_COLOR, size=11),
)

# ── 1. Geopolitical Risk Matrix (3×3: Probability vs Impact) ──────────────────

def build_risk_matrix(risk_data: list[dict]) -> go.Figure:
    """
    3×3 Geopolitical Risk Matrix (Probability × Impact).
    Zones: Low/Medium/High coloured background bands.
    Points coloured by sentiment; hover shows full context.
    """
    fig = go.Figure()

    # ── Background zone rectangles ────────────────────────────────────────────
    zones = [
        # (x0, x1, y0, y1, fillcolor, label)
        (0.0, 0.33, 0.0, 0.33, "rgba(0,192,118,0.06)",  "LOW RISK"),
        (0.0, 0.33, 0.33, 0.66, "rgba(255,184,0,0.05)",  ""),
        (0.0, 0.33, 0.66, 1.0,  "rgba(255,51,85,0.05)",  ""),
        (0.33, 0.66, 0.0, 0.33, "rgba(255,184,0,0.05)",  ""),
        (0.33, 0.66, 0.33, 0.66, "rgba(255,184,0,0.08)", "MEDIUM RISK"),
        (0.33, 0.66, 0.66, 1.0,  "rgba(255,51,85,0.07)", ""),
        (0.66, 1.0, 0.0, 0.33,  "rgba(255,184,0,0.05)",  ""),
        (0.66, 1.0, 0.33, 0.66, "rgba(255,51,85,0.07)",  ""),
        (0.66, 1.0, 0.66, 1.0,  "rgba(255,51,85,0.12)",  "HIGH RISK"),
    ]
    zone_labels = {
        (0.0, 0.33, 0.0, 0.33):    ("LOW",    ACCENT_GREEN),
        (0.33, 0.66, 0.33, 0.66):  ("MEDIUM", ACCENT_AMBER),
        (0.66, 1.0, 0.66, 1.0):    ("HIGH",   ACCENT_RED),
    }
    for x0, x1, y0, y1, fill, label in zones:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                      fillcolor=fill, line=dict(width=0), layer="below")

    for (x0, x1, y0, y1), (lbl, col) in zone_labels.items():
        fig.add_annotation(
            x=(x0+x1)/2, y=(y0+y1)/2,
            text=f"<b>{lbl}</b>", showarrow=False,
            font=dict(color=col, size=13, family="JetBrains Mono, monospace"),
            opacity=0.3,
        )

    # ── Grid dividers ─────────────────────────────────────────────────────────
    for v in [0.33, 0.66]:
        fig.add_shape(type="line", x0=v, x1=v, y0=0, y1=1,
                      line=dict(color=GRID_COLOR, width=1, dash="dot"))
        fig.add_shape(type="line", x0=0, x1=1, y0=v, y1=v,
                      line=dict(color=GRID_COLOR, width=1, dash="dot"))

    # ── Scatter points ────────────────────────────────────────────────────────
    for sent, label in [("positive", "Positive"), ("negative", "Negative"), ("neutral", "Neutral")]:
        subset = [r for r in risk_data if r["sentiment"] == sent]
        if not subset:
            continue
        color = get_sentiment_color(sent)
        fig.add_trace(go.Scatter(
            x=[r["probability"] for r in subset],
            y=[r["impact"]      for r in subset],
            mode="markers+text",
            name=f"{label} Sentiment",
            marker=dict(
                color=color,
                size=14,
                line=dict(color=BG_COLOR, width=1.5),
                symbol="circle",
                opacity=0.85,
            ),
            text=[r["id"] for r in subset],
            textposition="top center",
            textfont=dict(size=8, color=MUTED_COLOR),
            customdata=[
                [r["label"], r["region"], r["category"], r["probability"], r["impact"]]
                for r in subset
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Region: %{customdata[1]}<br>"
                "Category: %{customdata[2]}<br>"
                "Probability: %{customdata[3]:.0%}<br>"
                "Impact: %{customdata[4]:.0%}<extra></extra>"
            ),
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="GEOPOLITICAL RISK MATRIX — PROBABILITY × IMPACT", x=0.01,
                   font=dict(size=12, color=MUTED_COLOR)),
        xaxis=dict(**AXIS_STYLE, title="PROBABILITY SCORE →",
                   range=[-0.02, 1.05], tickformat=".0%"),
        yaxis=dict(**AXIS_STYLE, title="IMPACT SCORE →",
                   range=[-0.02, 1.05], tickformat=".0%"),
        height=480,
    )
    return fig


# ── 2. Sectoral Heatmap (% change + sentiment overlay) ───────────────────────

def build_sectoral_heatmap(market_summary: dict, engine_output: dict) -> go.Figure:
    """
    Heatmap: rows = sectors, columns = stocks.
    Cell value = daily % change.
    Border/annotation colour overlay from Alpha Sentiment Engine signal.
    """
    sectors  = list(market_summary["sectors"].keys())
    if not sectors:
        return go.Figure()

    # Build matrix
    all_stocks, all_sectors, z_vals, hover_text, signal_colors = [], [], [], [], []
    sector_summary = engine_output.get("sector_summary", {})

    for sector in sectors:
        stocks_data = market_summary["sectors"].get(sector, {})
        sig_data    = sector_summary.get(sector, {})
        sig         = sig_data.get("dominant_signal", "NEUTRAL")
        sig_col     = get_sector_color(sig)

        for stock_name, metrics in stocks_data.items():
            pct = metrics.get("change_pct", 0.0)
            all_stocks.append(stock_name)
            all_sectors.append(sector)
            z_vals.append(pct)
            hover_text.append(
                f"<b>{stock_name}</b> [{sector}]<br>"
                f"Price: ₹{metrics.get('price', 0):,.2f}<br>"
                f"Change: {pct:+.2f}%<br>"
                f"Geo Signal: <b>{sig}</b> ({sig_data.get('confidence', 0):.0%} conf)"
            )
            signal_colors.append(sig_col)

    # Pivot to 2D for heatmap
    unique_sectors = sectors
    unique_stocks  = list(dict.fromkeys(all_stocks))

    z_matrix    = []
    hover_matrix = []
    for sec in unique_sectors:
        row_z, row_h = [], []
        for stk in unique_stocks:
            idx = next((i for i, (s, st) in enumerate(zip(all_sectors, all_stocks))
                        if s == sec and st == stk), None)
            if idx is not None:
                row_z.append(z_vals[idx])
                row_h.append(hover_text[idx])
            else:
                row_z.append(None)
                row_h.append("")
        z_matrix.append(row_z)
        hover_matrix.append(row_h)

    fig = go.Figure(go.Heatmap(
        z=z_matrix,
        x=unique_stocks,
        y=unique_sectors,
        text=[[f"{v:+.2f}%" if v is not None else "" for v in row] for row in z_matrix],
        texttemplate="%{text}",
        textfont=dict(size=12, color="white"),
        hovertext=hover_matrix,
        hovertemplate="%{hovertext}<extra></extra>",
        colorscale=[
            [0.0,  ACCENT_RED],
            [0.45, "#1C2526"],
            [0.55, "#1C2526"],
            [1.0,  ACCENT_GREEN],
        ],
        zmid=0,
        zmin=-5, zmax=5,
        colorbar=dict(
            title="Daily %",
            ticksuffix="%",
            tickfont=dict(color=MUTED_COLOR, size=10),
            titlefont=dict(color=MUTED_COLOR, size=10),
            len=0.8,
        ),
    ))

    # Overlay sentiment annotations per sector
    for i, sec in enumerate(unique_sectors):
        sig_data = sector_summary.get(sec, {})
        sig      = sig_data.get("dominant_signal", "NEUTRAL")
        fig.add_annotation(
            x=len(unique_stocks) - 0.3, y=sec,
            text=f" {sig}",
            showarrow=False,
            font=dict(color=get_sector_color(sig), size=9),
            xanchor="right",
        )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="SECTORAL HEATMAP — DAILY % CHANGE + GEO SIGNAL OVERLAY", x=0.01,
                   font=dict(size=12, color=MUTED_COLOR)),
        xaxis=dict(**AXIS_STYLE, title=""),
        yaxis=dict(**AXIS_STYLE, title=""),
        height=300,
    )
    return fig


# ── 3. NIFTY vs SENSEX Normalised Comparison ─────────────────────────────────

def build_index_comparison(df_norm: pd.DataFrame) -> go.Figure:
    """
    Line chart: NIFTY 50 vs SENSEX normalised to 100.
    Fills area under NIFTY, shows divergence band.
    """
    if df_norm.empty:
        return go.Figure()

    fig = go.Figure()

    colors = {"NIFTY 50": ACCENT_GREEN, "SENSEX": ACCENT_BLUE}
    for col in df_norm.columns:
        col_color = colors.get(col, ACCENT_BLUE)
        fig.add_trace(go.Scatter(
            x=df_norm.index,
            y=df_norm[col],
            name=col,
            line=dict(color=col_color, width=2),
            fill="tozeroy" if col == "NIFTY 50" else "none",
            fillcolor=f"rgba({_hex_to_rgb(col_color)}, 0.06)",
            hovertemplate=f"<b>{col}</b><br>%{{x|%b %d}}: %{{y:.2f}}<extra></extra>",
        ))

    # Divergence annotation
    if len(df_norm) > 1:
        latest = df_norm.iloc[-1]
        divergence = abs(latest.iloc[0] - latest.iloc[1]) if len(latest) >= 2 else 0
        fig.add_annotation(
            x=df_norm.index[-1], y=df_norm.iloc[-1].max() + 0.5,
            text=f"Δ {divergence:.2f} pts",
            showarrow=False,
            font=dict(color=ACCENT_AMBER, size=10),
        )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="NIFTY 50 vs SENSEX — NORMALISED TO 100 (1-MONTH)", x=0.01,
                   font=dict(size=12, color=MUTED_COLOR)),
        xaxis=dict(**AXIS_STYLE, title="", tickformat="%b %d"),
        yaxis=dict(**AXIS_STYLE, title="Indexed (Base=100)"),
        height=380,
        hovermode="x unified",
    )
    return fig


# ── 4. Individual Stock Trend Chart ──────────────────────────────────────────

def build_stock_trend(hist_df: pd.DataFrame, symbol: str, display_name: str) -> go.Figure:
    """
    Candlestick + volume chart for a single stock.
    """
    if hist_df.empty:
        return go.Figure()

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=hist_df.index,
        open=hist_df["Open"],
        high=hist_df["High"],
        low=hist_df["Low"],
        close=hist_df["Close"],
        name=display_name,
        increasing=dict(line=dict(color=ACCENT_GREEN), fillcolor=f"rgba({_hex_to_rgb(ACCENT_GREEN)}, 0.5)"),
        decreasing=dict(line=dict(color=ACCENT_RED),   fillcolor=f"rgba({_hex_to_rgb(ACCENT_RED)}, 0.5)"),
    ))

    # 5-day MA
    if len(hist_df) >= 5:
        ma5 = hist_df["Close"].rolling(5).mean()
        fig.add_trace(go.Scatter(
            x=hist_df.index, y=ma5,
            name="MA5", line=dict(color=ACCENT_AMBER, width=1, dash="dash"),
            hovertemplate="MA5: ₹%{y:,.2f}<extra></extra>",
        ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"{display_name} ({symbol}) — 1 MONTH CANDLES", x=0.01,
                   font=dict(size=12, color=MUTED_COLOR)),
        xaxis=dict(**AXIS_STYLE, title="", tickformat="%b %d", rangeslider=dict(visible=False)),
        yaxis=dict(**AXIS_STYLE, title="Price (₹)"),
        height=380,
    )
    return fig


# ── 5. Risk Category Bar Chart ────────────────────────────────────────────────

def build_category_risk_bars(news_feed: list[dict]) -> go.Figure:
    """
    Horizontal bar chart: avg composite risk score (prob × impact) per category.
    """
    from collections import defaultdict
    cat_scores: dict[str, list[float]] = defaultdict(list)
    for n in news_feed:
        score = n["probability"] * n["impact"]
        cat_scores[n["category"]].append(score)

    cats   = list(cat_scores.keys())
    avgs   = [np.mean(v) for v in cat_scores.values()]
    colors = [
        ACCENT_RED if a > 0.55 else ACCENT_AMBER if a > 0.35 else ACCENT_GREEN
        for a in avgs
    ]

    fig = go.Figure(go.Bar(
        x=avgs, y=cats,
        orientation="h",
        marker=dict(color=colors, line=dict(color=BG_COLOR, width=1)),
        text=[f"{a:.2f}" for a in avgs],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="Category: <b>%{y}</b><br>Avg Risk Score: %{x:.2f}<extra></extra>",
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="AVG COMPOSITE RISK SCORE BY CATEGORY (Prob × Impact)", x=0.01,
                   font=dict(size=12, color=MUTED_COLOR)),
        xaxis=dict(**AXIS_STYLE, title="Score", range=[0, 1]),
        yaxis=dict(**AXIS_STYLE, title=""),
        height=350,
    )
    return fig


# ── Utility ───────────────────────────────────────────────────────────────────

def _hex_to_rgb(hex_color: str) -> str:
    """Convert #RRGGBB to 'R,G,B' string for rgba()."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"
