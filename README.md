# Stock & Forex Pattern Screener

A **Streamlit-based stock and forex screener** built with **Python, yFinance, and Plotly** that detects common chart patterns such as **M (double top)** and **W (double bottom)** formations.  

It helps traders and analysts quickly visualise potential market reversals or breakout opportunities with both **stocks** and **forex pairs**.

---

## Features

- **Multi-Asset Support** -- Screen both **stocks** and **forex pairs**

- **Candlestick Visualization** -- Interactive charts using **Plotly**

- **Pattern Detection Engine** -- Detects M/W breakouts (double top/bottom)
- **Early Alerts** -- Identifies early breakout signals

- *(Optional)* Email alerts for pattern detection (configurable in code)

- **Detection History** -- Stores previously detected patterns in the session

---

##  Tech Stack

| Component | Purpose |

|------------|----------|

| **Python** | Core logic and backend |

| **Streamlit** | Web UI for interactive screening |

| **yFinance** | Fetching real-time market data |

| **Plotly** | Interactive candlestick charts |

| **NumPy / SciPy** | Pattern recognition via local extrema |

| **Pandas** | Data manipulation & session storage |

---

##  Project Structure

stock-pattern-screener

├── app.py # Main Streamlit application

├── data_fetcher.py # Handles data fetching and normalization

├── pattern_detector.py # Core pattern detection logic (M/W break)

├── requirements.txt # Python dependencies

└── README.md # Project documentation

---

## ⚙️ Installation & Setup

### Clone the Repository

```

git clone https://github.com/<your-username>/stock-pattern-screener.git

cd stock-pattern-screener
```

## Create a Virtual Environment (Optional but Recommended)

```
python -m venv venv
```
```
source venv/bin/activate  # On Mac/Linux

venv\Scripts\activate     # On Windows
```
## Install Dependencies

```

pip install -r requirements.txt
```
## Run the Application

```

streamlit run app.py
```
Then open the local URL shown in the terminal, usually:

👉 http://localhost:8501
---

## How It Works

### Data Fetching:

The app uses yfinance to download intraday or daily OHLC data for the selected stock or forex symbol.

### Visualization:

plotly renders a candlestick chart for quick technical inspection.

### Pattern Detection:

The pattern_detector.py module identifies:

- Double Bottom (W pattern) -- Potential bullish reversal

- Double Top (M pattern) -- Potential bearish reversal

- Detection can be configured for early alerts or confirmed breakouts.
### History Tracking:

Detected patterns are stored in session state and displayed in a tabular format.

#### Example Usage

- Stocks

- Enter stock tickers (e.g., TCS, RELIANCE, AAPL)

- Choose the period (e.g., 6mo) and interval (e.g., 1d)

- Click Fetch Stock Data

#### Forex

- Enter forex pairs (e.g., USDINR, EURUSD)

- Use Yahoo-compatible format (e.g., USDINR=X)

- Click Fetch Forex Data

---
# ScreenShots
---
<img width="3647" height="1506" alt="image" src="https://github.com/user-attachments/assets/aa9683e0-f6ef-4a69-b184-d0be9e3590f2" />

<img width="3840" height="5180" alt="screencapture-localhost-8501-2025-10-25-14_41_43" src="https://github.com/user-attachments/assets/5c047a1b-04bc-4a93-b78e-219d96253276" />

