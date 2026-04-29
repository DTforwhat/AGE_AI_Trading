"""Technical trend analysis derived from stock snapshots."""

from __future__ import annotations

from typing import Optional


def trend_signal(snapshot: dict) -> dict[str, Optional[str | float]]:
    """Build a simple trend reading from indicators on a snapshot."""
    price = snapshot.get("price")
    sma20 = snapshot.get("sma_20")
    sma50 = snapshot.get("sma_50")
    sma200 = snapshot.get("sma_200")
    rsi = snapshot.get("rsi_14")
    high = snapshot.get("fifty_two_week_high")
    low = snapshot.get("fifty_two_week_low")

    # Trend by SMA stack
    trend = "neutral"
    if sma20 and sma50 and sma200 and price:
        if price > sma20 > sma50 > sma200:
            trend = "strong_uptrend"
        elif price > sma50 > sma200:
            trend = "uptrend"
        elif price < sma20 < sma50 < sma200:
            trend = "strong_downtrend"
        elif price < sma50 < sma200:
            trend = "downtrend"

    # RSI bucket
    rsi_state = None
    if rsi is not None:
        if rsi >= 70:
            rsi_state = "overbought"
        elif rsi <= 30:
            rsi_state = "oversold"
        else:
            rsi_state = "neutral"

    # Position in 52w range (0..1)
    range_pos = None
    if price and high and low and high > low:
        range_pos = (price - low) / (high - low)

    return {
        "trend": trend,
        "rsi_state": rsi_state,
        "range_pos": range_pos,
        "rsi": rsi,
    }
