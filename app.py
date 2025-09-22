#  app.py
# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import requests
# from datetime import datetime
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# from data_fetcher import fetch_intraday, fetch_daily
# from pattern_detector import detect_patterns

# # -------------------------------
# # EMAIL CONFIG (Hardcoded for now)
# # -------------------------------
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SENDER_EMAIL = "your_email@gmail.com"
# SENDER_PASSWORD = "your_app_password"  # Use Gmail App Password
# RECEIVER_EMAIL = "receiver_email@gmail.com"

# def send_email_alert(subject, body):
#     """Send email alert for detected patterns"""
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = SENDER_EMAIL
#         msg["To"] = RECEIVER_EMAIL
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "plain"))

#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(SENDER_EMAIL, SENDER_PASSWORD)
#             server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
#         print("✅ Email sent successfully")
#     except Exception as e:
#         print(f"⚠️ Email failed: {e}")

# # -------------------------------
# # Function: Search ticker by company name
# # -------------------------------
# def search_ticker(query):
#     url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
#     try:
#         r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         if r.status_code == 200:
#             data = r.json()
#             return [item["symbol"] for item in data.get("quotes", [])]
#     except Exception as e:
#         st.error(f"⚠️ Search error: {e}")
#     return []

# # -------------------------------
# # Streamlit UI
# # -------------------------------
# st.set_page_config(page_title="📈 Stock Pattern Detector", layout="wide")
# st.title("📈 Stock Pattern Detector with Alerts")

# # Sidebar inputs
# company_query = st.sidebar.text_input(
#     "🔎 Enter Company Names (comma separated)",
#     "Infosys, Reliance, TCS"
# )

# period = st.sidebar.selectbox("Period", ["3mo", "6mo", "1y", "2y"])
# interval = st.sidebar.selectbox("Interval", ["1d", "4h"])  # only Day & 4H

# # Initialize detection history
# if "detections" not in st.session_state:
#     st.session_state["detections"] = []

# # -------------------------------
# # Fetch + Process
# # -------------------------------
# if st.sidebar.button("Load Data"):
#     companies = [q.strip() for q in company_query.split(",") if q.strip()]

#     for company in companies:
#         suggestions = search_ticker(company)
#         if not suggestions:
#             st.warning(f"No ticker found for {company}")
#             continue

#         ticker = suggestions[0]  # pick first suggestion
#         try:
#             # Use correct fetcher
#             if interval == "4h":
#                 df = fetch_intraday(ticker, interval="4h", period=period)
#                 if len(df) < 150:
#                     st.warning(f"⚠️ Skipping {company} ({ticker}) – not enough 4H candles (<150).")
#                     continue
#             else:  # daily
#                 df = fetch_daily(ticker, period=period)
#                 if len(df) < 40:
#                     st.warning(f"⚠️ Skipping {company} ({ticker}) – not enough Daily candles (<40).")
#                     continue

#             if df.empty:
#                 st.error(f"❌ No data found for '{ticker}' ({company}).")
#                 continue

#             st.success(f"✅ Data loaded for {company} ({ticker})")

#             # --- Candlestick Chart ---
#             fig = go.Figure(data=[go.Candlestick(
#                 x=df.index,
#                 open=df["open"],
#                 high=df["high"],
#                 low=df["low"],
#                 close=df["close"]
#             )])
#             fig.update_layout(title=f"{company} ({ticker}) Stock Chart",
#                               xaxis_rangeslider_visible=False)
#             st.plotly_chart(fig, use_container_width=True)

#             # --- Pattern Detection with Early Alert ---
#             patterns = detect_patterns(df, early_alert=True)
#             pattern_names = ", ".join([p["pattern"] for p in patterns]) if patterns else "None"

#             detection = {
#                 "company": company,
#                 "ticker": ticker,
#                 "interval": interval,
#                 "period": period,
#                 "patterns": pattern_names,
#                 "last_refreshed": datetime.utcnow()
#             }
#             st.session_state["detections"].append(detection)

#             st.info(f"📊 Patterns in {company} ({ticker}): {pattern_names}")

#             # --- Send Email if early pattern detected ---
#             if patterns:
#                 subject = f"📊 Pattern Alert: {company} ({ticker})"
#                 body = f"""
#                 Company: {company}
#                 Ticker: {ticker}
#                 Interval: {interval}
#                 Period: {period}
#                 Patterns: {pattern_names}
#                 Last Refreshed: {detection['last_refreshed']}
#                 """
#                 # Uncomment when ready:
#                 # send_email_alert(subject, body)

#         except Exception as e:
#             st.error(f"⚠️ Error fetching data for {company}: {str(e)}")

# # -------------------------------
# # Show Detection History
# # -------------------------------
# st.subheader("📋 Detection History")
# if st.session_state["detections"]:
#     hist_df = pd.DataFrame(st.session_state["detections"])
#     hist_df["last_refreshed"] = pd.to_datetime(hist_df["last_refreshed"], utc=True)
#     hist_df = hist_df.sort_values("last_refreshed", ascending=False)
#     st.dataframe(hist_df, use_container_width=True)
# else:
#     st.info("No tickers loaded yet.")

# # -------------------------------
# # Hide Streamlit Menu
# # -------------------------------
# hide_streamlit_style = """
#     <style>
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# # ____________________________recent working code --------------------------------
# # app.py
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# ------------------ Utils ------------------

def normalize_symbol(user_symbol: str, asset_type: str) -> str:
    """
    Normalize a user-entered symbol for yfinance.
    - Stocks: if no market suffix and not forex, try NSE by appending .NS
    - Forex: if looks like a currency pair w/o =X, append =X
    """
    sym = (user_symbol or "").strip().upper()
    if not sym:
        return sym

    if asset_type == "forex":
        # If user entered like USDINR without =X, convert to USDINR=X
        if sym.endswith("=X"):
            return sym
        if len(sym) == 6 and sym.isalpha():
            return f"{sym}=X"
        return sym

    # asset_type == "stock"
    if "." not in sym and not sym.endswith("=X"):
        # Heuristic: default to NSE suffix for common Indian equities
        return f"{sym}.NS"
    return sym

def fetch_data(ticker, period="6mo", interval="1d"):
    try:
        # Enforce single symbol; if multiple provided, use the first
        original_ticker = ticker
        if isinstance(ticker, str) and "," in ticker:
            parts = [t.strip() for t in ticker.split(",") if t.strip()]
            if parts:
                ticker = parts[0]
                st.warning(f"Multiple symbols detected. Using first: {ticker}")

        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
            group_by="ticker"
        )
        if df.empty:
            return None
        # Handle MultiIndex columns by selecting the requested ticker
        if isinstance(df.columns, pd.MultiIndex):
            level0 = list(df.columns.get_level_values(0))
            level1 = list(df.columns.get_level_values(1))

            known_fields = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}

            if ticker in level0:
                df = df[ticker].copy()
            elif ticker in level1:
                df = df.xs(ticker, level=1, axis=1).copy()
            else:
                # Try to infer ticker candidates from each level
                candidates0 = [v for v in sorted(set(level0)) if v not in known_fields]
                candidates1 = [v for v in sorted(set(level1)) if v not in known_fields]
                if candidates0:
                    chosen = candidates0[0]
                    df = df[chosen].copy()
                    st.warning(f"Downloaded multiple symbols. Showing: {chosen}")
                elif candidates1:
                    chosen = candidates1[0]
                    df = df.xs(chosen, level=1, axis=1).copy()
                    st.warning(f"Downloaded multiple symbols. Showing: {chosen}")
                else:
                    # As a last resort, flatten columns and proceed
                    df = df.copy()
                    df.columns = ["_".join(map(str, c)).strip() for c in df.columns]

        df = df.reset_index()
        return df
    except Exception as e:
        st.warning(f"⚠️ Error fetching {ticker}: {e}")
        return None

def plot_candles(df, title):
    if df is None or df.empty:
        st.warning("No data to plot.")
        return

    # Normalize columns in case of MultiIndex or casing differences
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.copy()
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        except Exception:
            pass

    # Standardize OHLC column names to title-case
    rename_map = {}
    for col in df.columns:
        try:
            col_lower = str(col).strip().lower()
        except Exception:
            continue
        if col_lower in {"open", "high", "low", "close"}:
            rename_map[col] = col_lower.title()
    if rename_map:
        df = df.rename(columns=rename_map)

    # Ensure we have required columns
    required_cols = {"Open", "High", "Low", "Close"}
    if not required_cols.issubset(set(df.columns)):
        st.error("Data missing required OHLC columns.")
        st.caption(f"Available columns: {list(df.columns)}")
        return

    df = df.reset_index(drop=True)

    # Determine x-axis column and coerce to datetime for Plotly time axis
    x_col = "Datetime" if "Datetime" in df.columns else ("Date" if "Date" in df.columns else None)
    if x_col is None:
        # Fallback: create a simple index-based x axis
        x_values = list(range(len(df)))
    else:
        # Coerce to datetime if possible; if it fails, use as-is
        try:
            x_values = pd.to_datetime(df[x_col])
        except Exception:
            x_values = df[x_col]

    fig = go.Figure(data=[go.Candlestick(
        x=x_values,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )])
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        margin=dict(l=10, r=10, t=40, b=10),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

def detect_pattern(df):
    """
    Simple placeholder pattern detection:
    Checks for double top/bottom (M / W shape).
    Early alert when C crosses B.
    """
    if df is None or len(df) < 10:
        return None

    closes = df["Close"].values

    # Example logic: last 4 pivots
    A, B, C, D = closes[-10], closes[-7], closes[-4], closes[-1]

    if C > B:  # Early alert in uptrend
        return "Possible W pattern forming (C > B)"
    elif C < B:  # Early alert in downtrend
        return "Possible M pattern forming (C < B)"
    return None

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="Stock & Forex Screener", layout="wide")

st.title("Stock & Forex Screener with Pattern Detection")

tabs = st.tabs(["Stocks", "Forex"])

# Initialize detection history in session state
if "detections" not in st.session_state:
    st.session_state["detections"] = []

# -------- STOCKS --------
with tabs[0]:
    st.header("Stocks")
    stock_symbol = st.text_input("Enter Stock Symbol(s) comma-separated (e.g., TCS, RELIANCE, AAPL):", "TCS")
    period = st.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=3)
    interval = st.selectbox("Interval", ["15m", "1h", "4h", "1d"], index=3)

    if st.button("Fetch Stock Data"):
        symbols = [s.strip() for s in stock_symbol.split(",") if s.strip()]
        if not symbols:
            st.error("Please enter at least one stock symbol.")
        for sym in symbols:
            norm = normalize_symbol(sym, asset_type="stock")
            df = fetch_data(norm, period=period, interval=interval)
            if df is not None:
                st.success(f"Showing data for {norm}")
                plot_candles(df, f"{norm} ({interval})")

                st.subheader("Tabular Data")
                st.dataframe(df.tail(50))

                pattern = detect_pattern(df)
                if pattern:
                    st.info(f"{norm}: {pattern}")
                # Append detection record
                st.session_state["detections"].append({
                    "asset_type": "stock",
                    "symbol": norm,
                    "period": period,
                    "interval": interval,
                    "pattern": pattern or "None",
                    "last_refreshed": datetime.utcnow()
                })
            else:
                st.error(f"No data for {sym}")

# -------- FOREX --------
with tabs[1]:
    st.header("Forex")
    st.write("You can enter raw pairs (USDINR) or Yahoo format (USDINR=X), comma-separated.")

    forex_symbol = st.text_input("Enter Forex Symbol(s):", "USDINR, EURUSD")
    forex_period = st.selectbox("Forex Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)
    forex_interval = st.selectbox("Forex Interval", ["15m", "1h", "4h", "1d"], index=3)

    if st.button("Fetch Forex Data"):
        symbols = [s.strip() for s in forex_symbol.split(",") if s.strip()]
        if not symbols:
            st.error("Please enter at least one forex symbol.")
        for sym in symbols:
            norm = normalize_symbol(sym, asset_type="forex")
            df_fx = fetch_data(norm, period=forex_period, interval=forex_interval)
            if df_fx is not None:
                st.success(f"Showing Forex data for {norm}")
                plot_candles(df_fx, f"{norm} ({forex_interval})")

                st.subheader("Tabular Data")
                st.dataframe(df_fx.tail(50))

                pattern = detect_pattern(df_fx)
                if pattern:
                    st.info(f"{norm}: {pattern}")
                # Append detection record
                st.session_state["detections"].append({
                    "asset_type": "forex",
                    "symbol": norm,
                    "period": forex_period,
                    "interval": forex_interval,
                    "pattern": pattern or "None",
                    "last_refreshed": datetime.utcnow()
                })
            else:
                st.error(f"No data for {norm}")

# -------- Detection History --------
st.subheader(" Detection History")
if st.session_state["detections"]:
    hist_df = pd.DataFrame(st.session_state["detections"])  # columns: asset_type, symbol, period, interval, pattern, last_refreshed
    try:
        hist_df["last_refreshed"] = pd.to_datetime(hist_df["last_refreshed"], utc=True)
    except Exception:
        pass
    hist_df = hist_df.sort_values("last_refreshed", ascending=False)
    st.dataframe(hist_df, use_container_width=True)
else:
    st.info("No detections yet. Fetch data to populate history.")
