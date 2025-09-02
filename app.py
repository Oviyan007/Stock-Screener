# import streamlit as st
# import yfinance as yf
# import pandas as pd
# import plotly.graph_objects as go
# from pattern_detector import detect_patterns  # keep your existing function

# st.set_page_config(page_title="Stock Pattern Monitor", layout="wide")
# st.title("📈 Stock Pattern Monitor")

# # Sidebar input
# ticker = st.sidebar.text_input("Enter Ticker (e.g. AAPL, INFY, TCS):", "AAPL")
# period = st.sidebar.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"])
# interval = st.sidebar.selectbox("Interval", ["15m", "1d"])

# # Initialize history storage
# if "detections" not in st.session_state:
#     st.session_state["detections"] = []

# # Fetch + Process Data when Add button clicked
# if st.sidebar.button("Add"):
#     try:
#         df = yf.download(ticker, period=period, interval=interval)

#         if df.empty:
#             st.error(f"❌ No data found for ticker '{ticker}'. Please check symbol.")
#         else:
#             # Normalize columns
#             df.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in df.columns]

#             st.success(f"✅ Data loaded for {ticker}")

#             # --- Detect patterns ---
#             with st.spinner("Scanning for patterns..."):
#                 patterns = detect_patterns(df)
#                 if patterns:
#                     for p in patterns:
#                         st.session_state["detections"].append({
#                             "pattern": p,
#                             "ticker": ticker,
#                             "interval": interval,
#                             "detected_at": pd.Timestamp.utcnow().tz_convert("UTC")
#                         })

#             # --- Show Candlestick Chart ---
#             fig = go.Figure(data=[go.Candlestick(
#                 x=df.index,
#                 open=df["open"],
#                 high=df["high"],
#                 low=df["low"],
#                 close=df["close"]
#             )])
#             fig.update_layout(title=f"{ticker} Stock Chart", xaxis_rangeslider_visible=False)
#             st.plotly_chart(fig, use_container_width=True)

#     except Exception as e:
#         st.error(f"⚠️ Error fetching data: {str(e)}")

# # --- Detection History ---
# st.subheader("Pattern Detection History")
# if st.session_state["detections"]:
#     hist_df = pd.DataFrame(st.session_state["detections"])
#     hist_df["detected_at"] = pd.to_datetime(hist_df["detected_at"], utc=True)
#     hist_df = hist_df.sort_values("detected_at", ascending=False)
#     st.dataframe(hist_df, use_container_width=True)
# else:
#     st.info("No patterns detected yet.")

## new version with yahoo ticker find 
# import streamlit as st
# import yfinance as yf
# import pandas as pd
# import plotly.graph_objects as go
# import requests
# from datetime import datetime

# st.title("📈 Stock Pattern Detector")

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
# # Sidebar: Search + Selection
# # -------------------------------
# company_query = st.sidebar.text_input("🔎 Search Company", "MobiKwik")

# ticker = None
# if company_query:
#     suggestions = search_ticker(company_query)
#     if suggestions:
#         ticker = st.sidebar.selectbox("Select Ticker", suggestions)
#     else:
#         st.sidebar.warning("No ticker found. Try another company name.")

# # -------------------------------
# # Period & Interval selection
# # -------------------------------
# period = st.sidebar.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"])
# interval = st.sidebar.selectbox("Interval", ["15m", "1d"])

# # -------------------------------
# # Initialize detection history
# # -------------------------------
# if "detections" not in st.session_state:
#     st.session_state["detections"] = []

# # -------------------------------
# # Fetch + Plot
# # -------------------------------
# if ticker and st.sidebar.button("Load Data"):
#     try:
#         df = yf.download(ticker, period=period, interval=interval)

#         if df.empty:
#             st.error(f"❌ No data found for ticker '{ticker}'. Please check symbol.")
#         else:
#             # Clean columns
#             df.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in df.columns]

#             st.success(f"✅ Data loaded for {ticker}")

#             # Candlestick chart
#             fig = go.Figure(data=[go.Candlestick(
#                 x=df.index,
#                 open=df["open"],
#                 high=df["high"],
#                 low=df["low"],
#                 close=df["close"]
#             )])
#             fig.update_layout(title=f"{ticker} Stock Chart", xaxis_rangeslider_visible=False)
#             st.plotly_chart(fig, use_container_width=True)

#             # Save to history
#             st.session_state["detections"].append({
#                 "ticker": ticker,
#                 "interval": interval,
#                 "period": period,
#                 "last_refreshed": datetime.utcnow()
#             })

#     except Exception as e:
#         st.error(f"⚠️ Error fetching data: {str(e)}")

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
#features with alert and multiple stock options

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------------------
# EMAIL CONFIG (Hardcoded)
# -------------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use App Password for Gmail
RECEIVER_EMAIL = "receiver_email@gmail.com"

# -------------------------------
# Send email function
# -------------------------------
def send_email_alert(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"⚠️ Email failed: {e}")

# -------------------------------
# Function: Search ticker by company name
# -------------------------------
def search_ticker(query):
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            data = r.json()
            return [item["symbol"] for item in data.get("quotes", [])]
    except Exception as e:
        st.error(f"⚠️ Search error: {e}")
    return []

# -------------------------------
# Dummy Pattern Detector
# -------------------------------
def detect_patterns(df):
    patterns = []
    if len(df) > 2:
        if df["close"].iloc[-1] > df["open"].iloc[-1]:  # bullish candle
            patterns.append("Bullish Candle")
        if df["close"].iloc[-1] < df["open"].iloc[-1]:  # bearish candle
            patterns.append("Bearish Candle")
    return patterns if patterns else ["None"]

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📈 Stock Pattern Detector with Alerts")

# Multiple company names input
company_query = st.sidebar.text_input(
    "🔎 Enter Company Names (comma separated)", 
    "MobiKwik, Infosys, TCS"
)

# Period & Interval
period = st.sidebar.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"])
interval = st.sidebar.selectbox("Interval", ["15m", "1d"])

# Initialize detection history
if "detections" not in st.session_state:
    st.session_state["detections"] = []

# Fetch + Process
if st.sidebar.button("Load Data"):
    companies = [q.strip() for q in company_query.split(",") if q.strip()]

    for company in companies:
        suggestions = search_ticker(company)
        if not suggestions:
            st.warning(f"No ticker found for {company}")
            continue

        ticker = suggestions[0]  # pick first match
        try:
            df = yf.download(ticker, period=period, interval=interval)

            if df.empty:
                st.error(f"❌ No data found for '{ticker}' ({company}).")
            else:
                # Clean columns
                df.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in df.columns]

                st.success(f"✅ Data loaded for {company} ({ticker})")

                # Candlestick chart
                fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"]
                )])
                fig.update_layout(title=f"{company} ({ticker}) Stock Chart", xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

                # Detect patterns
                patterns = detect_patterns(df)

                # Save detection history
                detection = {
                    "company": company,
                    "ticker": ticker,
                    "interval": interval,
                    "period": period,
                    "patterns": ", ".join(patterns),
                    "last_refreshed": datetime.utcnow()
                }
                st.session_state["detections"].append(detection)

                # Show detected patterns
                st.info(f"📊 Patterns in {company} ({ticker}): {detection['patterns']}")

                # Send email only if a pattern (not "None")
                if detection["patterns"] != "None":
                    subject = f"📊 Pattern Alert: {company} ({ticker})"
                    body = f"""
                    Company: {company}
                    Ticker: {ticker}
                    Interval: {interval}
                    Period: {period}
                    Patterns: {detection['patterns']}
                    Last Refreshed: {detection['last_refreshed']}
                    """
                    # send_email_alert(subject, body)

        except Exception as e:
            st.error(f"⚠️ Error fetching data for {company}: {str(e)}")

# Show Detection History
st.subheader("📋 Detection History")
if st.session_state["detections"]:
    hist_df = pd.DataFrame(st.session_state["detections"])
    hist_df["last_refreshed"] = pd.to_datetime(hist_df["last_refreshed"], utc=True)
    hist_df = hist_df.sort_values("last_refreshed", ascending=False)
    st.dataframe(hist_df, use_container_width=True)
else:
    st.info("No tickers loaded yet.")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 