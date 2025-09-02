# pattern_detector.py
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from typing import Dict, Any, Optional, Tuple

def _local_extrema(series: pd.Series, order: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """Return indices of local minima and maxima."""
    arr = series.values
    maxima = argrelextrema(arr, np.greater, order=order)[0]
    minima = argrelextrema(arr, np.less, order=order)[0]
    return minima, maxima

def detect_double_bottom(
    df: pd.DataFrame,
    lookback: int = 200,
    order: int = 3,
    price_tolerance: float = 0.03,
    require_breakout: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Double bottom (W):
      - two local minima within tolerance
      - a middle peak (neckline) between them
      - optional: last close > neckline (breakout)
    """
    if df is None or df.empty or "close" not in df.columns:
        return None

    close = df["close"].dropna()
    if len(close) < max(20, order * 3):
        return None

    window = close[-lookback:]
    minima, maxima = _local_extrema(window, order=order)
    if len(minima) < 2:
        return None

    vals = window.values
    idxs = window.index

    for i in range(len(minima) - 1):
        i1, i2 = minima[i], minima[i+1]
        if i2 - i1 < order + 1:
            continue
        low1, low2 = vals[i1], vals[i2]
        if abs(low2 - low1) / max(low1, low2) > price_tolerance:
            continue

        # Find neckline = highest point between the two lows
        mid_slice = vals[i1:i2+1]
        mid_rel = int(np.argmax(mid_slice))
        mid_idx = i1 + mid_rel
        neckline = float(vals[mid_idx])

        recent_close = float(vals[-1])
        if require_breakout and not (recent_close > neckline):
            continue

        return {
            "pattern": "double_bottom",
            "t1": idxs[i1],
            "t2": idxs[i2],
            "low1": float(low1),
            "low2": float(low2),
            "neckline_time": idxs[mid_idx],
            "neckline": neckline,
            "confirmed": bool(recent_close > neckline),
            "detected_at": idxs[-1],
        }
    return None

def detect_double_top(
    df: pd.DataFrame,
    lookback: int = 200,
    order: int = 3,
    price_tolerance: float = 0.03,
    require_breakout: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Double top (N):
      - two local maxima within tolerance
      - a middle trough between them
      - optional: last close < neckline (breakdown)
    """
    if df is None or df.empty or "close" not in df.columns:
        return None

    close = df["close"].dropna()
    if len(close) < max(20, order * 3):
        return None

    window = close[-lookback:]
    minima, maxima = _local_extrema(window, order=order)
    if len(maxima) < 2:
        return None

    vals = window.values
    idxs = window.index

    for i in range(len(maxima) - 1):
        i1, i2 = maxima[i], maxima[i+1]
        if i2 - i1 < order + 1:
            continue
        high1, high2 = vals[i1], vals[i2]
        if abs(high2 - high1) / max(high1, high2) > price_tolerance:
            continue

        # Neckline = lowest point between the two highs
        mid_slice = vals[i1:i2+1]
        mid_rel = int(np.argmin(mid_slice))
        mid_idx = i1 + mid_rel
        neckline = float(vals[mid_idx])

        recent_close = float(vals[-1])
        if require_breakout and not (recent_close < neckline):
            continue

        return {
            "pattern": "double_top",
            "t1": idxs[i1],
            "t2": idxs[i2],
            "high1": float(high1),
            "high2": float(high2),
            "neckline_time": idxs[mid_idx],
            "neckline": neckline,
            "confirmed": bool(recent_close < neckline),
            "detected_at": idxs[-1],
        }
    return None
def detect_patterns(df: pd.DataFrame):
    """
    Run all pattern detections and return a list of results.
    """
    results = []

    db = detect_double_bottom(df)
    if db:
        results.append(db)

    dt = detect_double_top(df)
    if dt:
        results.append(dt)

    return results