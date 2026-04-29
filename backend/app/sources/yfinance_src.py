"""yfinance wrapper for prices, fundamentals, and technical indicators."""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def _rsi(series: pd.Series, period: int = 14) -> Optional[float]:
    if len(series) < period + 1:
        return None
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-9)
    rsi = 100 - 100 / (1 + rs)
    val = rsi.iloc[-1]
    return float(val) if pd.notna(val) else None


def _sma(series: pd.Series, period: int) -> Optional[float]:
    if len(series) < period:
        return None
    val = series.rolling(period).mean().iloc[-1]
    return float(val) if pd.notna(val) else None


def fetch_snapshot(symbol: str) -> Optional[dict]:
    """Latest price + key fundamentals + technical indicators."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y", auto_adjust=True)
        if hist.empty:
            return None
        close = hist["Close"]
        last = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if len(close) > 1 else last
        change_pct = ((last - prev) / prev * 100) if prev else 0.0

        info = {}
        try:
            info = ticker.info or {}
        except Exception:  # noqa: BLE001
            info = {}

        return {
            "symbol": symbol,
            "price": last,
            "change_pct": change_pct,
            "volume": int(hist["Volume"].iloc[-1]) if "Volume" in hist else 0,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "rsi_14": _rsi(close, 14),
            "sma_20": _sma(close, 20),
            "sma_50": _sma(close, 50),
            "sma_200": _sma(close, 200),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("yfinance snapshot failed for %s: %s", symbol, exc)
        return None


def fetch_history(symbol: str, period: str = "6mo") -> list[dict]:
    """Daily OHLCV history for charting."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, auto_adjust=True)
        if hist.empty:
            return []
        return [
            {
                "date": idx.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
            }
            for idx, row in hist.iterrows()
        ]
    except Exception as exc:  # noqa: BLE001
        logger.warning("yfinance history failed for %s: %s", symbol, exc)
        return []


def fetch_company_profile(symbol: str) -> dict:
    try:
        info = yf.Ticker(symbol).info or {}
        return {
            "symbol": symbol,
            "name": info.get("longName") or info.get("shortName") or symbol,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "summary": info.get("longBusinessSummary", "")[:1000],
            "website": info.get("website"),
            "employees": info.get("fullTimeEmployees"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("yfinance profile failed for %s: %s", symbol, exc)
        return {"symbol": symbol, "name": symbol}


def fetch_earnings_dates(symbol: str) -> list[dict]:
    """Recent earnings dates with EPS estimate vs actual."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.get_earnings_dates(limit=8)
        if df is None or df.empty:
            return []
        rows = []
        for idx, row in df.iterrows():
            rows.append(
                {
                    "symbol": symbol,
                    "report_date": idx.to_pydatetime().replace(tzinfo=None),
                    "eps_estimate": float(row["EPS Estimate"]) if pd.notna(row.get("EPS Estimate")) else None,
                    "eps_actual": float(row["Reported EPS"]) if pd.notna(row.get("Reported EPS")) else None,
                }
            )
        return rows
    except Exception as exc:  # noqa: BLE001
        logger.warning("yfinance earnings dates failed for %s: %s", symbol, exc)
        return []
