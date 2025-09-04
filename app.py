# # app.py
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
# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from data_fetcher import fetch_intraday, fetch_daily
from pattern_detector import detect_patterns

# -------------------------------
# EMAIL CONFIG (Hardcoded for now)
# -------------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Gmail App Password
RECEIVER_EMAIL = "receiver_email@gmail.com"

def send_email_alert(subject, body):
    """Send email alert for detected patterns"""
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
# Candle requirements
# -------------------------------
CANDLE_REQUIREMENTS = {
    "1d": 40,     # Daily
    "4h": 150,    # 4 Hour
    "1h": 100,    # 1 Hour
    "15m": 200    # 15 Minute
}

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="📈 Stock Pattern Detector", layout="wide")
st.title("📈 Stock Pattern Detector with Alerts")

# Sidebar inputs
company_query = st.sidebar.text_input(
    "🔎 Enter Company Names (comma separated)",
    "MobiKwik, Infosys, TCS"
)

period = st.sidebar.selectbox("Period", ["5d", "1mo", "3mo", "6mo", "1y"])
interval = st.sidebar.selectbox("Interval", ["15m", "1h", "4h", "1d"])

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

        ticker = suggestions[0]  # pick first suggestion
        try:
            # Fetch data
            if interval in ["15m", "1h", "4h"]:
                df = fetch_intraday(ticker, interval=interval, period=period)
            else:
                df = fetch_daily(ticker, period=period)

            if df.empty:
                st.error(f"❌ No data found for '{ticker}' ({company}).")
                continue

            # --- Candle requirement check ---
            min_candles = CANDLE_REQUIREMENTS.get(interval, 0)
            if len(df) < min_candles:
                st.warning(f"⚠️ Not enough candles for {company} ({ticker}). "
                           f"Need at least {min_candles}, got {len(df)}.")
                continue

            st.success(f"✅ Data loaded for {company} ({ticker}) [{interval}]")

            # --- Candlestick Chart ---
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"]
            )])
            fig.update_layout(title=f"{company} ({ticker}) Stock Chart [{interval}]",
                              xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # --- Pattern Detection (with early alert) ---
            patterns = detect_patterns(df, early_alert=True)
            pattern_names = ", ".join([p["pattern"] for p in patterns]) if patterns else "None"

            detection = {
                "company": company,
                "ticker": ticker,
                "interval": interval,
                "period": period,
                "patterns": pattern_names,
                "last_refreshed": datetime.utcnow()
            }
            st.session_state["detections"].append(detection)

            st.info(f"📊 Patterns in {company} ({ticker}) [{interval}]: {pattern_names}")

            # --- Send Email if pattern detected ---
            if patterns:
                subject = f"📊 Pattern Alert: {company} ({ticker}) [{interval}]"
                body = f"""
                Company: {company}
                Ticker: {ticker}
                Interval: {interval}
                Period: {period}
                Patterns: {pattern_names}
                Last Refreshed: {detection['last_refreshed']}
                """
                # send_email_alert(subject, body)   # Uncomment to enable email

        except Exception as e:
            st.error(f"⚠️ Error fetching data for {company}: {str(e)}")

# -------------------------------
# Show Detection History
# -------------------------------
st.subheader("📋 Detection History")
if st.session_state["detections"]:
    hist_df = pd.DataFrame(st.session_state["detections"])
    hist_df["last_refreshed"] = pd.to_datetime(hist_df["last_refreshed"], utc=True)
    hist_df = hist_df.sort_values("last_refreshed", ascending=False)
    st.dataframe(hist_df, use_container_width=True)
else:
    st.info("No tickers loaded yet.")

# Hide Streamlit Menu
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
