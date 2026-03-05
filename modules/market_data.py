# modules/market_data.py
# ─────────────────────────────────────────────────────────────────────────────
# MARKET DATA LAYER
# Fetches near-real-time Indian market data via yfinance.
# ⚠ PROTOTYPE ONLY — yfinance is unofficial; not suitable for production trading.
# Future: Replace with NSE/BSE official data APIs or Bloomberg/Refinitiv feeds.
# ─────────────────────────────────────────────────────────────────────────────

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

# ── Symbol Registry ───────────────────────────────────────────────────────────
INDICES = {
    "NIFTY 50":  "^NSEI",
    "SENSEX":    "^BSESN",
}

SECTOR_STOCKS = {
    "Defense": {
        "HAL":  "HAL.NS",
        "BEL":  "BEL.NS",
    },
    "Energy": {
        "ONGC":     "ONGC.NS",
        "Reliance": "RELIANCE.NS",
    },
    "IT": {
        "Infosys": "INFY.NS",
        "TCS":     "TCS.NS",
    },
}

ALL_SYMBOLS = (
    list(INDICES.values())
    + [sym for sector in SECTOR_STOCKS.values() for sym in sector.values()]
)

# ── Data fetch helpers ────────────────────────────────────────────────────────

@st.cache_data(ttl=900, show_spinner=False)  # 15-min cache
def fetch_quote_data(symbols: list[str], period: str = "5d", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches OHLCV data for a list of symbols.
    Returns multi-level DataFrame (yfinance default).
    PLACEHOLDER: Wire to official data provider for production.
    """
    try:
        raw = yf.download(
            tickers=symbols,
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        return raw
    except Exception as e:
        st.warning(f"⚠ Market data fetch error: {e}. Showing cached / demo data.")
        return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_ticker_info(symbol: str) -> dict:
    """
    Fetches metadata / fundamentals for a single ticker.
    Returns dict with keys like previousClose, marketCap, sector, etc.
    """
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
        return info
    except Exception:
        return {}


@st.cache_data(ttl=900, show_spinner=False)
def fetch_history(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch price history for a single ticker. Returns OHLCV DataFrame."""
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period=period, interval=interval, auto_adjust=True)
        return hist
    except Exception:
        return pd.DataFrame()


# ── Derived metrics ───────────────────────────────────────────────────────────

def compute_daily_change(df_close: pd.DataFrame) -> dict[str, dict]:
    """
    Given a DataFrame of close prices (columns = symbols),
    returns dict: {symbol: {price, prev_close, change_abs, change_pct}}
    """
    result = {}
    if df_close is None or df_close.empty:
        return result

    for col in df_close.columns:
        series = df_close[col].dropna()
        if len(series) < 2:
            continue
        price      = float(series.iloc[-1])
        prev_close = float(series.iloc[-2])
        change_abs = price - prev_close
        change_pct = (change_abs / prev_close) * 100 if prev_close else 0.0
        result[col] = {
            "price":      price,
            "prev_close": prev_close,
            "change_abs": change_abs,
            "change_pct": change_pct,
        }
    return result


def get_all_market_summary() -> dict:
    """
    Master function: fetches and returns structured market summary.
    Returns: {
        "indices":       {display_name: metrics_dict},
        "sectors":       {sector_name: {stock_display_name: metrics_dict}},
        "raw_history":   {symbol: pd.DataFrame},
        "last_updated":  datetime string,
        "data_ok":       bool,
    }
    """
    summary = {
        "indices":      {},
        "sectors":      {},
        "raw_history":  {},
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M IST"),
        "data_ok":      False,
    }

    # Fetch bulk OHLCV
    raw = fetch_quote_data(ALL_SYMBOLS, period="5d", interval="1d")
    if raw.empty:
        return summary

    # Extract close prices (handle single vs multi-ticker columns)
    try:
        if isinstance(raw.columns, pd.MultiIndex):
            close_df = raw["Close"]
        else:
            close_df = raw[["Close"]].rename(columns={"Close": ALL_SYMBOLS[0]})
    except KeyError:
        return summary

    changes = compute_daily_change(close_df)

    # ── Indices ───────────────────────────────────────────────────────────────
    for display_name, sym in INDICES.items():
        if sym in changes:
            summary["indices"][display_name] = {**changes[sym], "symbol": sym}

    # ── Sectors ──────────────────────────────────────────────────────────────
    for sector, stocks in SECTOR_STOCKS.items():
        summary["sectors"][sector] = {}
        for display_name, sym in stocks.items():
            if sym in changes:
                summary["sectors"][sector][display_name] = {
                    **changes[sym], "symbol": sym
                }

    # ── Individual histories (for charting) ──────────────────────────────────
    for sym in list(INDICES.values()) + [s for sec in SECTOR_STOCKS.values() for s in sec.values()]:
        hist = fetch_history(sym, period="1mo")
        if not hist.empty:
            summary["raw_history"][sym] = hist

    summary["data_ok"] = True
    return summary


def get_nifty_sensex_comparison() -> pd.DataFrame:
    """
    Returns aligned close price DataFrame for NIFTY and SENSEX (1 month).
    Normalised to 100 for relative comparison.
    """
    nifty_hist  = fetch_history("^NSEI",  period="1mo")
    sensex_hist = fetch_history("^BSESN", period="1mo")

    if nifty_hist.empty or sensex_hist.empty:
        return pd.DataFrame()

    df = pd.DataFrame({
        "NIFTY 50": nifty_hist["Close"],
        "SENSEX":   sensex_hist["Close"],
    }).dropna()

    # Normalise to 100
    base = df.iloc[0]
    df_norm = (df / base) * 100
    return df_norm
