# data_fetcher.py  (REPLACE your existing file with this)
import yfinance as yf
import pandas as pd
from typing import Optional, Union
from datetime import datetime


def _normalize(raw: Union[pd.DataFrame, tuple, list]) -> pd.DataFrame:
    """
    Normalize yfinance output into a DataFrame with columns:
      ['open','high','low','close','volume'] when available.

    Handles:
      - raw being a DataFrame
      - raw being a tuple/list where the first element is a DataFrame
      - MultiIndex columns (tuples)
      - 'Adj Close' fallback for 'close'
    """
    # sometimes yf.download returns a tuple/list (older/newer combos) -> take first df if so
    if isinstance(raw, (tuple, list)):
        if len(raw) > 0 and isinstance(raw[0], pd.DataFrame):
            df = raw[0]
        else:
            return pd.DataFrame()
    elif isinstance(raw, pd.DataFrame):
        df = raw
    else:
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    # Build mapping from standard names to actual columns
    cols = list(df.columns)
    found = {}  # maps words like 'open' -> actual column object

    for col in cols:
        # build a lowercase searchable string for the column
        if isinstance(col, tuple):
            key = " ".join([str(x) for x in col if x is not None]).lower()
        else:
            key = str(col).lower()

        # prefer the first occurrence for each measurement
        if 'open' in key and 'open' not in found:
            found['open'] = col
        if 'high' in key and 'high' not in found:
            found['high'] = col
        if 'low' in key and 'low' not in found:
            found['low'] = col
        # prefer plain 'close' over 'adj close'
        if 'close' in key and 'adj' not in key and 'close' not in found:
            found['close'] = col
        if 'adj close' in key and 'adj close' not in found:
            found['adj close'] = col
        if 'volume' in key and 'volume' not in found:
            found['volume'] = col

    # Prepare final mapping, prefer 'close' then 'adj close'
    mapping = {}
    if 'open' in found: mapping['open'] = found['open']
    if 'high' in found: mapping['high'] = found['high']
    if 'low' in found: mapping['low'] = found['low']
    if 'close' in found:
        mapping['close'] = found['close']
    elif 'adj close' in found:
        mapping['close'] = found['adj close']
    if 'volume' in found:
        mapping['volume'] = found['volume']

    # If we didn't find anything sensible, try a safe fallback: lowercase string columns
    if not mapping:
        # attempt to coerce columns to single-level lowercase names and select known columns
        try:
            df2 = df.copy()
            new_cols = []
            for c in df2.columns:
                if isinstance(c, tuple):
                    new_cols.append("_".join([str(x) for x in c if x is not None]).lower())
                else:
                    new_cols.append(str(c).lower())
            df2.columns = new_cols
            out_cols = [c for c in ["open","high","low","close","volume"] if c in df2.columns]
            return df2[out_cols].copy()
        except Exception:
            # last resort: return empty DataFrame so caller can handle it
            return pd.DataFrame()

    # Build standardized DataFrame
    out = pd.DataFrame(index=df.index)
    for std_name, real_col in mapping.items():
        out[std_name] = df[real_col]

    # Ensure datetime index and typical dtypes
    out.index = pd.to_datetime(out.index)
    # ensure numeric dtype where possible
    out = out.apply(pd.to_numeric, errors='coerce')

    return out

def fetch_intraday(ticker: str, interval: str = "15m", period: str = "60d") -> pd.DataFrame:
    """
    Fetch intraday data using yfinance.
    Note: yfinance intraday data is limited in history (usually ~60 days).
    """
    # explicit auto_adjust to avoid FutureWarning and keep raw OHLCV
    raw = yf.download(tickers=ticker, period=period, interval=interval,
                      progress=False, threads=True, auto_adjust=False)
    return _normalize(raw)

def fetch_daily(ticker: str, period: str = "5y", start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch daily OHLCV.
    Use either period or start/end.
    """
    kwargs = {"period": period} if start is None else {"start": start, "end": end}
    raw = yf.download(tickers=ticker, progress=False, threads=True, auto_adjust=False, **kwargs)
    return _normalize(raw)
def store_detection(pattern_name, ticker):
    detection = {
        "pattern": pattern_name,
        "ticker": ticker,
        # always save as UTC tz-aware
        "detected_at": pd.Timestamp.utcnow().tz_localize("UTC")
    }
    if "detections" not in st.session_state:
        st.session_state["detections"] = []
    st.session_state["detections"].append(detection)
