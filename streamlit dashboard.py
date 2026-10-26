# ============================================================
# NIFTY 50 LIVE IMPLIED VOLATILITY ANALYSIS & FORECASTING
# UNIFIED REAL-TIME STREAMLIT APPLICATION & BACKGROUND ENGINE
# ============================================================
# Architecture:
# - Integrated persistent background daemon thread for 5-min Upstox snapshots
# - Dynamic near-ATM lag feature engineering (39 model features)
# - Real-time Random Forest implied volatility forecasting & relative valuation
# - Full 8-page dark-themed institutional dashboard with interactive BSM stress testing
# ============================================================

import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import requests
from scipy.stats import norm
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NIFTY Options | Live IV Intelligence & Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. PATH RESOLUTION & ENVIRONMENT SETUP
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
BASE = PROJECT_DIR if (PROJECT_DIR / "data").exists() else (Path.home() / "Downloads")

# Load environment credentials from project directory or Downloads fallback
load_dotenv(PROJECT_DIR / ".env")
load_dotenv(Path.home() / "Downloads" / ".env")
ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()

MODEL_DIR = BASE / "models"
PROCESSED_DIR = BASE / "data" / "processed"
LIVE_DIR = BASE / "data" / "live"
LIVE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "nifty_iv_random_forest.joblib"
FEATURE_FILE = MODEL_DIR / "nifty_iv_model_features.joblib"
MEDIAN_FILE = MODEL_DIR / "nifty_iv_feature_medians.joblib"

HISTORY_FILE = LIVE_DIR / "live_snapshot_history.csv"
LIVE_PREDICTIONS_FILE = LIVE_DIR / "live_iv_predictions.csv"
PREDICTION_LOG_FILE = LIVE_DIR / "live_prediction_log.csv"
RAW_CHAIN_FILE = LIVE_DIR / "latest_full_option_chain.csv"

# Historical research files for validation and fallback baseline
HISTORICAL_VALUATION_FILE = PROCESSED_DIR / "relative_iv_valuation_results.csv"
FEATURE_IMPORTANCE_FILE = PROCESSED_DIR / "final_feature_importance.csv"
SPOT_STRESS_FILE = PROCESSED_DIR / "stress_test_spot.csv"
IV_STRESS_FILE = PROCESSED_DIR / "stress_test_iv.csv"
COMBINED_STRESS_FILE = PROCESSED_DIR / "stress_test_combined_scenarios.csv"
EXPIRY_ROBUSTNESS_FILE = PROCESSED_DIR / "rf_19oct_timestamp_performance.csv"


# ============================================================
# 3. INSTITUTIONAL DARK THEME STYLING
# ============================================================

st.markdown(
    """
<style>
.stApp {
    background: #071426;
    color: #E7EEF8;
}
.block-container {
    padding-top: 0.75rem;
    padding-bottom: 1.2rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
    max-width: 100%;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: #09182B;
    border-right: 1px solid #1C385B;
}
.brand-title {
    font-size: 21px;
    font-weight: 750;
    color: #FFFFFF;
    letter-spacing: -0.2px;
}
.brand-subtitle {
    color: #91A7C2;
    font-size: 11.5px;
    margin-bottom: 16px;
}

/* Status Cards & Badges */
.status-box {
    margin-top: 14px;
    padding: 12px;
    border-radius: 8px;
    background: #0D213A;
    border: 1px solid #1C385B;
}
.badge-live {
    color: #35D49A;
    font-weight: 750;
    font-size: 12px;
}
.badge-warm {
    color: #F3C763;
    font-weight: 750;
    font-size: 12px;
}
.badge-closed {
    color: #8EA5C0;
    font-weight: 750;
    font-size: 12px;
}
.badge-error {
    color: #FF7180;
    font-weight: 750;
    font-size: 12px;
}
.status-desc {
    color: #8EA5C0;
    font-size: 10.5px;
    margin-top: 5px;
    line-height: 1.4;
}

/* Overview Panels */
.panel {
    background: #0C1D34;
    border: 1px solid #1D385B;
    border-radius: 9px;
    padding: 14px;
    min-height: 106px;
}
.card-label {
    color: #B3C3D7;
    font-size: 12px;
    font-weight: 600;
}
.card-value {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 750;
    margin-top: 6px;
}
.card-note {
    color: #879DB8;
    font-size: 11px;
    margin-top: 5px;
}
.green { color: #35D49A; font-weight: 600; }
.red { color: #FF7180; font-weight: 600; }
.blue { color: #6FA8FF; font-weight: 600; }
.amber { color: #F3C763; font-weight: 600; }

.section-title {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 6px;
}
.top-label {
    color: #A6B8CD;
    font-size: 11.5px;
    font-weight: 600;
}
.top-number {
    color: #FFFFFF;
    font-size: 26px;
    font-weight: 750;
}

/* Streamlit Widget Styling */
div[data-testid="stDataFrame"] {
    border: 1px solid #1C3556;
    border-radius: 7px;
}
div[data-baseweb="select"] > div {
    background-color: #0B1B30 !important;
    border-color: #27476C !important;
}
div[data-testid="metric-container"] {
    background: #0C1D34;
    border: 1px solid #1D385B;
    border-radius: 8px;
    padding: 12px;
}
[data-testid="stVerticalBlock"] { gap: 0.5rem; }
hr {
    border-color: #1B3555;
    margin-top: 0.4rem;
    margin-bottom: 0.4rem;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# 4. LOAD MODEL ASSETS & CACHES
# ============================================================

@st.cache_resource(show_spinner=False)
def load_ml_assets():
    if not MODEL_FILE.exists() or not FEATURE_FILE.exists() or not MEDIAN_FILE.exists():
        return None, [], {}
    model = joblib.load(MODEL_FILE)
    features = joblib.load(FEATURE_FILE)
    medians = joblib.load(MEDIAN_FILE)
    return model, features, medians


MODEL, MODEL_FEATURES, TRAIN_MEDIANS = load_ml_assets()

# Upstox API settings
UNDERLYING_KEY = "NSE_INDEX|Nifty 50"
OPTION_CHAIN_URL = "https://api.upstox.com/v2/option/chain"
OPTION_CONTRACT_URL = "https://api.upstox.com/v2/option/contract"
API_HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}" if ACCESS_TOKEN else "",
}


def num(value):
    try:
        return np.nan if value is None else float(value)
    except (TypeError, ValueError):
        return np.nan


@st.cache_data(ttl=300, show_spinner=False)
def get_available_expiries():
    if not ACCESS_TOKEN:
        return ["2026-10-27", "2026-11-03", "19 Oct 2026"]
    try:
        r = requests.get(
            OPTION_CONTRACT_URL,
            headers=API_HEADERS,
            params={"instrument_key": UNDERLYING_KEY},
            timeout=15,
        )
        r.raise_for_status()
        contracts = r.json().get("data", [])
        expiries = sorted({c.get("expiry") for c in contracts if c.get("expiry")})
        today = pd.Timestamp.now(tz="Asia/Kolkata").date()
        future = [e for e in expiries if pd.to_datetime(e).date() >= today]
        return future if future else expiries
    except Exception:
        return ["2026-10-27", "2026-11-03", "19 Oct 2026"]


def fetch_option_chain(expiry):
    if not ACCESS_TOKEN:
        raise ValueError("UPSTOX_ACCESS_TOKEN is missing or not configured in .env")
    r = requests.get(
        OPTION_CHAIN_URL,
        headers=API_HEADERS,
        params={"instrument_key": UNDERLYING_KEY, "expiry_date": expiry},
        timeout=18,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Upstox option-chain error: {payload}")
    return payload.get("data", [])


# ============================================================
# 5. FEATURE ENGINEERING & PREDICTION PIPELINE
# ============================================================

def parse_option_chain(chain, expiry, bucket_utc):
    rows = []
    for item in chain:
        strike = num(item.get("strike_price"))
        spot = num(item.get("underlying_spot_price"))
        for source_key, option_type in [("call_options", "CE"), ("put_options", "PE")]:
            opt = item.get(source_key) or {}
            mkt = opt.get("market_data") or {}
            grk = opt.get("option_greeks") or {}
            rows.append(
                {
                    "time_5m": bucket_utc,
                    "expiry": str(expiry),
                    "option_type": option_type,
                    "option_type_code": 0 if option_type == "CE" else 1,
                    "strike": strike,
                    "spot": spot,
                    "LTP": num(mkt.get("ltp")),
                    "Volume": num(mkt.get("volume")),
                    "OI": num(mkt.get("oi")),
                    "Bid": num(mkt.get("bid_price")),
                    "Ask": num(mkt.get("ask_price")),
                    "IV": num(grk.get("iv")),
                }
            )
    return pd.DataFrame(rows)


def add_current_features(df):
    df = df.copy()
    df["moneyness"] = df["strike"] / df["spot"]
    df["distance_from_ATM_pct"] = (df["strike"] - df["spot"]).abs() / df["spot"] * 100
    df["bid_ask_spread"] = df["Ask"] - df["Bid"]
    df["mid_price"] = (df["Ask"] + df["Bid"]) / 2.0
    df["relative_spread_pct"] = np.where(
        df["mid_price"] > 0,
        df["bid_ask_spread"] / df["mid_price"] * 100.0,
        np.nan,
    )

    put_oi = df.loc[df["option_type"] == "PE", "OI"].fillna(0).sum()
    call_oi = df.loc[df["option_type"] == "CE", "OI"].fillna(0).sum()
    df["pcr"] = put_oi / call_oi if call_oi > 0 else np.nan

    current_ist = pd.to_datetime(df["time_5m"], utc=True).dt.tz_convert("Asia/Kolkata")
    expiry_dates = pd.to_datetime(df["expiry"]).dt.date
    df["days_to_expiry"] = [
        (exp_d - cur_t.date()).days
        for exp_d, cur_t in zip(expiry_dates, current_ist)
    ]
    return df


def filter_near_atm(df):
    return df[
        (df["moneyness"] >= 0.95)
        & (df["moneyness"] <= 1.05)
        & (df["IV"] > 0)
    ].copy()


def read_history():
    if not HISTORY_FILE.exists():
        return pd.DataFrame()
    h = pd.read_csv(HISTORY_FILE)
    if not h.empty:
        h["time_5m"] = pd.to_datetime(h["time_5m"], utc=True, errors="coerce")
    return h


def append_history(snapshot):
    history = read_history()
    if history.empty:
        combined = snapshot.copy()
    else:
        combined = pd.concat([history, snapshot], ignore_index=True)

    combined = (
        combined.drop_duplicates(
            subset=["time_5m", "expiry", "strike", "option_type"], keep="last"
        )
        .sort_values("time_5m")
        .reset_index(drop=True)
    )
    combined.to_csv(HISTORY_FILE, index=False)
    return combined


def add_lag_features(history):
    history = history.copy()
    history["time_5m"] = pd.to_datetime(history["time_5m"], utc=True, errors="coerce")
    keys = ["expiry", "strike", "option_type"]
    lag_vars = ["IV", "spot", "LTP", "Volume", "OI", "bid_ask_spread"]

    lag5 = history[keys + ["time_5m"] + lag_vars].copy()
    lag5["time_5m"] = lag5["time_5m"] + pd.Timedelta(minutes=5)
    lag5 = lag5.rename(columns={v: f"{v}_lag_5m" for v in lag_vars})

    lag10 = history[keys + ["time_5m"] + lag_vars].copy()
    lag10["time_5m"] = lag10["time_5m"] + pd.Timedelta(minutes=10)
    lag10 = lag10.rename(columns={v: f"{v}_lag_10m" for v in lag_vars})

    merged = history.merge(lag5, on=keys + ["time_5m"], how="left")
    merged = merged.merge(lag10, on=keys + ["time_5m"], how="left")

    for v in lag_vars:
        merged[f"{v}_change_prev_5m"] = merged[v] - merged[f"{v}_lag_5m"]
        merged[f"{v}_change_prev_10m"] = merged[v] - merged[f"{v}_lag_10m"]

    return merged


def append_prediction_log(latest_df):
    cols = [
        "time_5m", "expiry", "strike", "option_type", "spot", "LTP", "Volume", "OI",
        "IV", "moneyness", "predicted_IV_change_5m", "predicted_future_IV",
        "relative_IV_valuation", "dashboard_signal",
    ]
    present_cols = [c for c in cols if c in latest_df.columns]
    new_rows = latest_df[present_cols].copy()

    if PREDICTION_LOG_FILE.exists():
        existing = pd.read_csv(PREDICTION_LOG_FILE)
        existing["time_5m"] = pd.to_datetime(existing["time_5m"], utc=True, errors="coerce")
        combined = pd.concat([existing, new_rows], ignore_index=True)
    else:
        combined = new_rows

    combined = (
        combined.drop_duplicates(
            subset=["time_5m", "expiry", "strike", "option_type"], keep="last"
        )
        .sort_values("time_5m")
        .reset_index(drop=True)
    )
    combined.to_csv(PREDICTION_LOG_FILE, index=False)


def make_prediction(history, expiry):
    if MODEL is None or not MODEL_FEATURES:
        return None

    lagged = add_lag_features(history)
    expiry_slice = lagged[lagged["expiry"].astype(str) == str(expiry)].copy()
    if expiry_slice.empty:
        return None

    latest_timestamp = expiry_slice["time_5m"].max()
    latest = expiry_slice[expiry_slice["time_5m"] == latest_timestamp].copy()
    latest = latest.dropna(subset=["IV_lag_5m", "IV_lag_10m"])

    if latest.empty:
        return None

    missing = [col for col in MODEL_FEATURES if col not in latest.columns]
    if missing:
        return None

    X = latest[MODEL_FEATURES].copy().replace([np.inf, -np.inf], np.nan)
    X = X.fillna(TRAIN_MEDIANS)

    latest["predicted_IV_change_5m"] = MODEL.predict(X)
    latest["predicted_future_IV"] = latest["IV"] + latest["predicted_IV_change_5m"]

    threshold = 0.10
    latest["relative_IV_valuation"] = np.where(
        latest["predicted_IV_change_5m"] > threshold,
        "RELATIVELY UNDERVALUED IV",
        np.where(
            latest["predicted_IV_change_5m"] < -threshold,
            "RELATIVELY OVERVALUED IV",
            "FAIR / NEUTRAL",
        ),
    )
    latest["dashboard_signal"] = latest["relative_IV_valuation"].replace(
        {
            "RELATIVELY UNDERVALUED IV": "LOW IV vs FORECAST",
            "RELATIVELY OVERVALUED IV": "HIGH IV vs FORECAST",
            "FAIR / NEUTRAL": "NEUTRAL",
        }
    )

    latest.to_csv(LIVE_PREDICTIONS_FILE, index=False)
    append_prediction_log(latest)
    return latest


# ============================================================
# 6. DEDICATED BACKGROUND COLLECTOR DAEMON
# ============================================================

def is_market_open(now_ist=None):
    if now_ist is None:
        now_ist = pd.Timestamp.now(tz="Asia/Kolkata")
    if now_ist.weekday() >= 5:  # Saturday or Sunday
        return False
    t = now_ist.time()
    return pd.Timestamp("09:15").time() <= t <= pd.Timestamp("15:30").time()


class LiveCollectorDaemon:
    """Persistent background daemon thread that synchronizes with the

    5-minute NSE market wall-clock and handles live Upstox ingestion.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.wake_event = threading.Event()
        self.target_expiry = None
        self.is_running = True
        self.force_flag = False

        self.status = "Initializing"
        self.message = "Background collector starting..."
        self.last_collection_time = None
        self.snapshot_count = 0
        self.error_count = 0

        self.thread = threading.Thread(
            target=self._worker_loop, daemon=True, name="UpstoxCollectorWorker"
        )
        self.thread.start()

    def set_target_expiry(self, expiry):
        if expiry and str(expiry) != str(self.target_expiry):
            with self.lock:
                self.target_expiry = str(expiry)

    def trigger_collection(self):
        self.force_flag = True
        self.wake_event.set()

    def collect_sync(self, expiry, force=True):
        with self.lock:
            self.target_expiry = str(expiry)
            return self._execute_cycle(force=force)

    def _execute_cycle(self, force=False):
        now_ist = pd.Timestamp.now(tz="Asia/Kolkata")
        if not force and not is_market_open(now_ist):
            self.status = "Closed"
            self.message = "Outside regular trading hours (09:15 - 15:30 IST)."
            return {"success": False, "status": "closed", "message": self.message}

        if not self.target_expiry:
            self.status = "Waiting"
            self.message = "No target expiry selected."
            return {"success": False, "status": "waiting", "message": self.message}

        bucket_ist = now_ist.floor("5min")
        bucket_utc = bucket_ist.tz_convert("UTC")

        try:
            chain = fetch_option_chain(self.target_expiry)
            if not chain:
                self.status = "Warning"
                self.message = f"Empty chain returned for {self.target_expiry}."
                return {"success": False, "status": "warning", "message": self.message}

            raw_df = parse_option_chain(chain, self.target_expiry, bucket_utc)
            raw_df = add_current_features(raw_df)

            # Persist full chain for the Option Chain viewer page
            raw_df.to_csv(RAW_CHAIN_FILE, index=False)

            # Near-ATM filter for the ML forecasting model
            snapshot = filter_near_atm(raw_df)
            if snapshot.empty:
                self.status = "Warning"
                self.message = "No valid near-ATM contracts (0.95 <= K/S <= 1.05) found."
                return {"success": False, "status": "warning", "message": self.message}

            history = append_history(snapshot)
            pred = make_prediction(history, self.target_expiry)

            self.last_collection_time = now_ist
            self.snapshot_count += 1
            if pred is not None:
                self.status = "Live"
                self.message = f"Live prediction generated at {now_ist.strftime('%H:%M:%S')} IST."
            else:
                self.status = "Warming"
                self.message = "Warming up: collecting exact 5m / 10m lag observations."

            return {
                "success": True,
                "status": self.status,
                "message": self.message,
                "time": now_ist,
                "rows": len(snapshot),
            }

        except Exception as e:
            self.error_count += 1
            self.status = "Error"
            self.message = f"{type(e).__name__}: {str(e)}"
            return {"success": False, "status": "error", "message": self.message}

    def _worker_loop(self):
        while self.is_running:
            now_ist = pd.Timestamp.now(tz="Asia/Kolkata")
            next_boundary = now_ist.floor("5min") + pd.Timedelta(minutes=5)
            # Add a 6-second offset into the bucket to let market ticks settle
            target_wake = next_boundary + pd.Timedelta(seconds=6)
            sleep_sec = max((target_wake - now_ist).total_seconds(), 2.0)

            # Wait until next 5m boundary OR until manual trigger event fires
            self.wake_event.wait(timeout=sleep_sec)
            self.wake_event.clear()

            is_forced = self.force_flag
            self.force_flag = False

            with self.lock:
                if self.target_expiry:
                    self._execute_cycle(force=is_forced)


@st.cache_resource(show_spinner=False)
def get_collector_daemon():
    return LiveCollectorDaemon()


COLLECTOR = get_collector_daemon()


# ============================================================
# 7. HISTORICAL RESEARCH DATA LOADER
# ============================================================

@st.cache_data(show_spinner=False)
def load_historical_datasets():
    def safe_read(p):
        return pd.read_csv(p) if p.exists() else pd.DataFrame()

    hist_val = safe_read(HISTORICAL_VALUATION_FILE)
    if not hist_val.empty:
        hist_val["time_5m"] = pd.to_datetime(hist_val["time_5m"], utc=True, errors="coerce")

    feat_df = safe_read(FEATURE_IMPORTANCE_FILE)
    spot_df = safe_read(SPOT_STRESS_FILE)
    iv_df = safe_read(IV_STRESS_FILE)
    comb_df = safe_read(COMBINED_STRESS_FILE)
    exp_df = safe_read(EXPIRY_ROBUSTNESS_FILE)

    if not exp_df.empty:
        exp_df["time_5m"] = pd.to_datetime(exp_df["time_5m"], utc=True, errors="coerce")
        exp_df["time_label"] = exp_df["time_5m"].dt.tz_convert("Asia/Kolkata").dt.strftime("%H:%M")

    return hist_val, feat_df, spot_df, iv_df, comb_df, exp_df


(
    HISTORICAL_VALUATION,
    FEATURE_IMPORTANCE,
    HIST_SPOT_STRESS,
    HIST_IV_STRESS,
    HIST_COMBINED_STRESS,
    HIST_ROBUSTNESS,
) = load_historical_datasets()


# ============================================================
# 8. BLACK-SCHOLES PRICING & GREEKS ENGINE
# ============================================================

def bs_pricing_kernel(S, K, T, r, sigma, option_type):
    """Closed-form analytical Black-Scholes-Merton option pricing and Greeks."""
    if T <= 0 or sigma <= 1e-6:
        intrinsic = max(S - K, 0.0) if option_type == "CE" else max(K - S, 0.0)
        delta = 1.0 if (option_type == "CE" and S > K) else (-1.0 if (option_type == "PE" and S < K) else 0.0)
        return intrinsic, delta, 0.0, 0.0, 0.0

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "CE":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365.0
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1.0
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365.0

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * np.sqrt(T) * norm.pdf(d1) / 100.0  # per 1 vol point change
    return max(price, 0.0), delta, gamma, vega, theta


def compute_exact_tte(expiry_str):
    now_ist = pd.Timestamp.now(tz="Asia/Kolkata")
    try:
        exp_date = pd.to_datetime(expiry_str).date()
        target_close = pd.Timestamp(f"{exp_date} 15:30:00", tz="Asia/Kolkata")
        seconds = max((target_close - now_ist).total_seconds(), 60.0)
    except Exception:
        seconds = 3600 * 24 * 3  # fallback 3 days
    years = seconds / (365.25 * 24 * 3600)
    minutes = seconds / 60.0
    return years, minutes


# ============================================================
# 9. CHART FORMATTING HELPERS
# ============================================================

PAPER_COLOR = "#0C1D34"
GRID_COLOR = "#213650"
TEXT_COLOR = "#C7D4E5"


def polish_chart(fig, height=330):
    fig.update_layout(
        template=None,
        height=height,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PAPER_COLOR,
        font=dict(color=TEXT_COLOR, size=11),
        margin=dict(l=55, r=20, t=35, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, tickfont=dict(size=10))
    fig.update_yaxes(gridcolor=GRID_COLOR, tickfont=dict(size=10))
    return fig


def format_large_number(x):
    if pd.isna(x):
        return "—"
    if x >= 1_00_00_000:
        return f"{x / 1_00_00_000:.2f} Cr"
    if x >= 1_00_000:
        return f"{x / 1_00_000:.2f} L"
    if x >= 1_000:
        return f"{x / 1_000:.1f} K"
    return f"{x:.0f}"


# ============================================================
# 10. SIDEBAR: NAVIGATION, EXPIRY & CONTROLS
# ============================================================

available_expiries = get_available_expiries()

with st.sidebar:
    st.markdown(
        '<div class="brand-title">📈 &nbsp; NIFTY Options</div>'
        '<div class="brand-subtitle">Live IV Intelligence & Forecasting</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "⛓ Option Chain",
            "📉 Volatility Smile",
            "🧠 ML Model",
            "⚖ Relative Valuation",
            "⚡ Stress Testing",
            "🧪 Robustness Test",
            "🗄 Data & Settings",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<b>Contract Settings</b>", unsafe_allow_html=True)

    selected_expiry = st.selectbox(
        "Active Expiry",
        available_expiries,
        index=0,
        help="Select the live NIFTY option expiry date to monitor and forecast.",
    )
    COLLECTOR.set_target_expiry(selected_expiry)

    # Action buttons
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("⚡ Collect Now", use_container_width=True, help="Force an immediate live snapshot & forecast"):
            with st.spinner("Fetching live Upstox snapshot..."):
                res = COLLECTOR.collect_sync(selected_expiry, force=True)
                if res.get("success"):
                    st.toast("Live snapshot collected successfully!", icon="✅")
                else:
                    st.toast(res.get("message", "Notice"), icon="⚠️")
            st.rerun()

    with c_btn2:
        if st.button("🔄 Reset", use_container_width=True, help="Reset live session data"):
            for f in [HISTORY_FILE, LIVE_PREDICTIONS_FILE, PREDICTION_LOG_FILE, RAW_CHAIN_FILE]:
                if f.exists():
                    f.unlink()
            st.toast("Live session data cleared.", icon="🧹")
            st.rerun()

    # Dynamic status box
    st.markdown("<hr>", unsafe_allow_html=True)
    last_t = COLLECTOR.last_collection_time
    time_str = last_t.strftime("%H:%M:%S") if last_t else "—"

    if COLLECTOR.status == "Live":
        badge_html = f'<div class="status-box"><div class="badge-live">● LIVE STREAMING</div><div class="status-desc">Last snapshot: {time_str} IST<br>Auto-updating every 5m wall-clock</div></div>'
    elif COLLECTOR.status == "Warming":
        badge_html = f'<div class="status-box"><div class="badge-warm">● WARMING UP</div><div class="status-desc">Snapshot saved at {time_str} IST.<br>Building 5m & 10m lag history...</div></div>'
    elif not is_market_open():
        badge_html = f'<div class="status-box"><div class="badge-closed">● MARKET CLOSED</div><div class="status-desc">NSE Hours: 09:15 - 15:30 IST.<br>Showing offline baseline dataset.</div></div>'
    elif COLLECTOR.status == "Error":
        badge_html = f'<div class="status-box"><div class="badge-error">● API NOTICE</div><div class="status-desc">{COLLECTOR.message[:90]}</div></div>'
    else:
        badge_html = '<div class="status-box"><div class="badge-warm">● WAITING FOR SNAPSHOT</div><div class="status-desc">Click \'Collect Now\' or wait for the 5m boundary.</div></div>'

    st.markdown(badge_html, unsafe_allow_html=True)


# ============================================================
# 11. DUAL-MODE DATA ROUTER (LIVE OR HISTORICAL FALLBACK)
# ============================================================

def load_active_data(target_expiry):
    """Loads live predictions and snapshots for the target expiry if available;

    falls back to the validated historical research dataset if no live data is present.
    """
    is_live_mode = False
    full_chain = pd.DataFrame()
    live_preds = pd.DataFrame()
    live_history = read_history()
    log_df = pd.DataFrame()

    if RAW_CHAIN_FILE.exists():
        raw_c = pd.read_csv(RAW_CHAIN_FILE)
        if not raw_c.empty and "expiry" in raw_c.columns:
            if str(target_expiry) in raw_c["expiry"].astype(str).values:
                full_chain = raw_c[raw_c["expiry"].astype(str) == str(target_expiry)].copy()

    if LIVE_PREDICTIONS_FILE.exists():
        p_df = pd.read_csv(LIVE_PREDICTIONS_FILE)
        if not p_df.empty and "expiry" in p_df.columns:
            p_slice = p_df[p_df["expiry"].astype(str) == str(target_expiry)].copy()
            if not p_slice.empty:
                live_preds = p_slice

    if PREDICTION_LOG_FILE.exists():
        log_df = pd.read_csv(PREDICTION_LOG_FILE)
        if not log_df.empty:
            log_df["time_5m"] = pd.to_datetime(log_df["time_5m"], utc=True, errors="coerce")
            log_df = log_df[log_df["expiry"].astype(str) == str(target_expiry)].copy()

    # Determine if we have valid live near-ATM data
    if not live_preds.empty:
        is_live_mode = True
        active_snapshot = live_preds.copy()
    elif not full_chain.empty:
        is_live_mode = True
        active_snapshot = filter_near_atm(full_chain)
    elif not live_history.empty and str(target_expiry) in live_history["expiry"].astype(str).values:
        is_live_mode = True
        h_slice = live_history[live_history["expiry"].astype(str) == str(target_expiry)].copy()
        max_t = h_slice["time_5m"].max()
        active_snapshot = h_slice[h_slice["time_5m"] == max_t].copy()
    else:
        # Graceful fallback to validated historical research dataset
        is_live_mode = False
        if not HISTORICAL_VALUATION.empty:
            max_t = HISTORICAL_VALUATION["time_5m"].max()
            active_snapshot = HISTORICAL_VALUATION[HISTORICAL_VALUATION["time_5m"] == max_t].copy()
        else:
            active_snapshot = pd.DataFrame()

    return is_live_mode, active_snapshot, full_chain, live_preds, log_df


IS_LIVE, CURRENT_SNAPSHOT, FULL_CHAIN, LIVE_PREDS, PREDICTION_LOG = load_active_data(selected_expiry)

has_snapshot = not CURRENT_SNAPSHOT.empty
has_predictions = not LIVE_PREDS.empty or (not IS_LIVE and not CURRENT_SNAPSHOT.empty and "predicted_future_IV" in CURRENT_SNAPSHOT.columns)

if has_snapshot:
    CURRENT_SNAPSHOT["atm_distance"] = (CURRENT_SNAPSHOT["moneyness"] - 1.0).abs()
    atm_row = CURRENT_SNAPSHOT.sort_values("atm_distance").iloc[0]
    spot_val = float(atm_row["spot"])
    current_iv = float(atm_row["IV"])
    snapshot_volume = CURRENT_SNAPSHOT["Volume"].fillna(0).sum()
    if has_predictions:
        pred_source = LIVE_PREDS if not LIVE_PREDS.empty else CURRENT_SNAPSHOT
        pred_source["atm_distance"] = (pred_source["moneyness"] - 1.0).abs()
        atm_pred_row = pred_source.sort_values("atm_distance").iloc[0]
        pred_iv = float(atm_pred_row["predicted_future_IV"])
        pred_delta = float(atm_pred_row["predicted_IV_change_5m"])
    else:
        pred_iv = np.nan
        pred_delta = np.nan
else:
    spot_val = 22691.0
    current_iv = 11.20
    snapshot_volume = 0
    pred_iv = np.nan
    pred_delta = np.nan


# ============================================================
# 12. TOP HEADER & DISPLAY FILTER
# ============================================================

h_col1, h_col2 = st.columns([2.5, 1.0])
with h_col1:
    mode_label = "● LIVE UPSTOX" if IS_LIVE else "● OFFLINE BASELINE"
    mode_class = "green" if IS_LIVE else "amber"
    st.markdown(
        f'<div class="top-label">NIFTY 50 INDEX • {selected_expiry} <span class="{mode_class}">({mode_label})</span></div>'
        f'<div class="top-number">{spot_val:,.2f}</div>',
        unsafe_allow_html=True,
    )

with h_col2:
    option_filter = st.selectbox(
        "Filter View",
        ["Both (Call & Put)", "Call (CE)", "Put (PE)"],
        label_visibility="collapsed",
    )

# Filter display subset
if has_snapshot:
    if "Call" in option_filter:
        display_snapshot = CURRENT_SNAPSHOT[CURRENT_SNAPSHOT["option_type"] == "CE"].copy()
    elif "Put" in option_filter:
        display_snapshot = CURRENT_SNAPSHOT[CURRENT_SNAPSHOT["option_type"] == "PE"].copy()
    else:
        display_snapshot = CURRENT_SNAPSHOT.copy()
else:
    display_snapshot = pd.DataFrame()


# ============================================================
# 13. REUSABLE PLOTLY CHARTS
# ============================================================

def chart_volatility_smile(data):
    if data.empty or "strike" not in data.columns or "IV" not in data.columns:
        fig = go.Figure()
        fig.add_annotation(text="No smile data available", showarrow=False, font=dict(color=TEXT_COLOR))
        return polish_chart(fig, 320)
    d = data[["strike", "IV", "option_type"]].dropna().sort_values("strike")
    fig = px.line(
        d,
        x="strike",
        y="IV",
        color="option_type",
        markers=True,
        color_discrete_map={"CE": "#458DFF", "PE": "#FF7F32"},
    )
    fig.update_xaxes(title="Strike Price (₹)")
    fig.update_yaxes(title="Implied Volatility (%)")
    return polish_chart(fig, 320)


def chart_moneyness_scatter(data):
    if data.empty or "moneyness" not in data.columns or "IV" not in data.columns:
        fig = go.Figure()
        fig.add_annotation(text="No moneyness data available", showarrow=False, font=dict(color=TEXT_COLOR))
        return polish_chart(fig, 320)
    d = data[["moneyness", "IV", "option_type"]].dropna()
    fig = px.scatter(
        d,
        x="moneyness",
        y="IV",
        color="option_type",
        color_discrete_map={"CE": "#458DFF", "PE": "#FF7F32"},
    )
    fig.update_xaxes(title="Moneyness (K / S)")
    fig.update_yaxes(title="Implied Volatility (%)")
    return polish_chart(fig, 320)


def chart_forecast_history(log_data):
    fig = go.Figure()
    if log_data.empty:
        # Fall back to historical prediction plot
        if not HISTORICAL_VALUATION.empty and "predicted_future_IV" in HISTORICAL_VALUATION.columns:
            tmp = (
                HISTORICAL_VALUATION.groupby("time_5m", as_index=False)[["IV", "predicted_future_IV"]]
                .mean()
                .sort_values("time_5m")
                .tail(25)
            )
            tmp["time_label"] = tmp["time_5m"].dt.tz_convert("Asia/Kolkata").dt.strftime("%H:%M")
            fig.add_trace(go.Scatter(x=tmp["time_label"], y=tmp["IV"], mode="lines+markers", name="Actual IV", line=dict(color="#458DFF", width=2)))
            fig.add_trace(go.Scatter(x=tmp["time_label"], y=tmp["predicted_future_IV"], mode="lines+markers", name="5m Forecast IV", line=dict(color="#FF8A37", width=2, dash="dash")))
        else:
            fig.add_annotation(text="Awaiting live prediction log...", showarrow=False, font=dict(color=TEXT_COLOR))
        fig.update_xaxes(title="Time (IST)")
        fig.update_yaxes(title="IV (%)")
        return polish_chart(fig, 320)

    tmp = (
        log_data.groupby("time_5m", as_index=False)[["IV", "predicted_future_IV"]]
        .mean()
        .sort_values("time_5m")
    )
    tmp["time_label"] = tmp["time_5m"].dt.tz_convert("Asia/Kolkata").dt.strftime("%H:%M")
    fig.add_trace(go.Scatter(x=tmp["time_label"], y=tmp["IV"], mode="lines+markers", name="Current Market IV", line=dict(color="#458DFF", width=2)))
    fig.add_trace(go.Scatter(x=tmp["time_label"], y=tmp["predicted_future_IV"], mode="lines+markers", name="5m Forecast IV", line=dict(color="#FF8A37", width=2, dash="dash")))
    fig.update_xaxes(title="Prediction Timestamp (IST)")
    fig.update_yaxes(title="IV (%)")
    return polish_chart(fig, 320)


# ============================================================
# 14. PAGE: 🏠 OVERVIEW
# ============================================================

if page == "🏠 Overview":
    if not IS_LIVE:
        st.info("ℹ️ **Offline Baseline Active:** Market is closed or awaiting first live snapshot. Showing historical benchmark dataset. The background collector is standing by and will ingest live Upstox ticks during market hours (09:15–15:30 IST) or on manual 'Collect Now'.")

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="panel"><div class="card-label">Current ATM IV</div><div class="card-value">{current_iv:.2f}%</div><div class="card-note">{"Latest live snapshot" if IS_LIVE else "Historical baseline"}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="panel"><div class="card-label">NIFTY Spot Price</div><div class="card-value">{spot_val:,.2f}</div><div class="card-note blue">{"Upstox index spot" if IS_LIVE else "Underlying benchmark"}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="panel"><div class="card-label">Snapshot Volume</div><div class="card-value">{format_large_number(snapshot_volume)}</div><div class="card-note">Near-ATM contracts</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        if not np.isnan(pred_iv):
            k_cls = "green" if pred_delta >= 0 else "red"
            st.markdown(
                f'<div class="panel"><div class="card-label">Model Forecast (t + 5m)</div><div class="card-value">{pred_iv:.2f}%</div><div class="card-note {k_cls}">ΔIV {pred_delta:+.3f} pts</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="panel"><div class="card-label">Model Forecast (t + 5m)</div><div class="card-value">Warming Up</div><div class="card-note amber">Collecting 5m / 10m lags</div></div>',
                unsafe_allow_html=True,
            )

    # Charts Row
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown('<div class="section-title">Volatility Smile</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_volatility_smile(display_snapshot), use_container_width=True, config={"displayModeBar": False})
    with g2:
        st.markdown('<div class="section-title">IV by Moneyness</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_moneyness_scatter(display_snapshot), use_container_width=True, config={"displayModeBar": False})
    with g3:
        st.markdown('<div class="section-title">Current IV vs 5m Forecast</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_forecast_history(PREDICTION_LOG), use_container_width=True, config={"displayModeBar": False})

    # Tables & Performance Row
    p1, p2, p3 = st.columns([1.2, 1.05, 1.1])
    with p1:
        st.markdown('<div class="section-title">Option Chain (Near ATM)</div>', unsafe_allow_html=True)
        if not display_snapshot.empty:
            oc_tbl = display_snapshot[["strike", "option_type", "LTP", "IV", "Volume", "OI", "Bid", "Ask"]].copy()
            oc_tbl.columns = ["Strike", "Type", "LTP", "IV (%)", "Volume", "OI", "Bid", "Ask"]
            st.dataframe(oc_tbl.sort_values("Strike").head(12), use_container_width=True, hide_index=True, height=295)
        else:
            st.info("No chain data available.")

    with p2:
        st.markdown('<div class="section-title">Validated Model Performance</div>', unsafe_allow_html=True)
        perf_summary = pd.DataFrame(
            {
                "Model": ["Persistence (Benchmark)", "Random Forest + Lags", "XGBoost Regressor"],
                "MAE": [0.5505, 0.5214, 0.5530],
                "RMSE": [1.3207, 1.2188, 1.2964],
            }
        )
        st.dataframe(perf_summary, use_container_width=True, hide_index=True, height=135)

        if not FEATURE_IMPORTANCE.empty:
            st.markdown('<div class="section-title">Top Feature Drivers</div>', unsafe_allow_html=True)
            top5 = FEATURE_IMPORTANCE.head(5).sort_values("Importance")
            fig_imp = px.bar(top5, x="Importance", y="Feature", orientation="h", color_discrete_sequence=["#7568FF"])
            fig_imp.update_layout(margin=dict(l=130, r=10, t=5, b=30), showlegend=False)
            fig_imp.update_yaxes(automargin=True)
            st.plotly_chart(polish_chart(fig_imp, 150), use_container_width=True, config={"displayModeBar": False})

    with p3:
        st.markdown('<div class="section-title">Relative IV Valuation</div>', unsafe_allow_html=True)
        target_v = LIVE_PREDS if not LIVE_PREDS.empty else CURRENT_SNAPSHOT
        if not target_v.empty and "predicted_future_IV" in target_v.columns:
            v_tbl = target_v[["strike", "option_type", "IV", "predicted_future_IV", "predicted_IV_change_5m", "dashboard_signal"]].copy()
            v_tbl.columns = ["Strike", "Type", "Market IV", "Model IV", "Diff.", "Signal"]
            st.dataframe(v_tbl.sort_values("Strike").head(12), use_container_width=True, hide_index=True, height=295)
        else:
            st.info("Relative IV valuation signals will appear once lag features are synchronized.")


# ============================================================
# 15. PAGE: ⛓ OPTION CHAIN
# ============================================================

elif page == "⛓ Option Chain":
    st.title("Interactive Live Option Chain")
    st.caption("Inspect live option chain quotes, bid-ask spreads, liquidity, and implied volatilities across all strikes.")

    chain_source = FULL_CHAIN if not FULL_CHAIN.empty else CURRENT_SNAPSHOT

    if chain_source.empty:
        st.info("Awaiting option chain snapshot from Upstox. Click '⚡ Collect Now' in the sidebar.")
    else:
        strikes = sorted(chain_source["strike"].dropna().unique())
        min_k, max_k = float(min(strikes)), float(max(strikes))

        c_filter1, c_filter2 = st.columns([2.5, 1.2])
        with c_filter1:
            k_range = st.slider("Strike Range (₹)", min_k, max_k, (min_k, max_k), step=50.0)
        with c_filter2:
            st.markdown(f"**Underlying Spot:** ₹{spot_val:,.2f}<br>**Strikes in View:** {len(strikes)}", unsafe_allow_html=True)

        filtered_chain = chain_source[
            (chain_source["strike"] >= k_range[0]) & (chain_source["strike"] <= k_range[1])
        ].copy()

        if "Call" in option_filter:
            filtered_chain = filtered_chain[filtered_chain["option_type"] == "CE"]
        elif "Put" in option_filter:
            filtered_chain = filtered_chain[filtered_chain["option_type"] == "PE"]

        disp_cols = ["option_type", "strike", "spot", "LTP", "IV", "Volume", "OI", "Bid", "Ask", "bid_ask_spread", "moneyness"]
        present = [c for c in disp_cols if c in filtered_chain.columns]
        st.dataframe(
            filtered_chain[present].sort_values(["strike", "option_type"]),
            use_container_width=True,
            hide_index=True,
            height=650,
        )


# ============================================================
# 16. PAGE: 📉 VOLATILITY SMILE
# ============================================================

elif page == "📉 Volatility Smile":
    st.title("Volatility Smile & Moneyness Dynamics")
    st.caption("Implied Volatility curvature across strikes and normalized moneyness ratios (K / S).")

    if display_snapshot.empty:
        st.info("Waiting for live option data.")
    else:
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("Strike Volatility Smile")
            st.plotly_chart(chart_volatility_smile(display_snapshot), use_container_width=True)
        with c_right:
            st.subheader("IV by Moneyness (K / S)")
            st.plotly_chart(chart_moneyness_scatter(display_snapshot), use_container_width=True)


# ============================================================
# 17. PAGE: 🧠 ML MODEL
# ============================================================

elif page == "🧠 ML Model":
    st.title("Machine Learning Forecasting Architecture")
    st.caption("Chronological validation metrics, autoregressive feature importances, and live model predictions.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("RF MAE", "0.5214", delta="-0.029 vs Persistence", delta_color="normal")
    m2.metric("Persistence MAE", "0.5505", help="Random walk benchmark")
    m3.metric("RF RMSE", "1.2188", delta="-0.102 vs Persistence", delta_color="normal")
    m4.metric("RF R² Score", "0.9866")

    st.subheader("Autoregressive Feature Importance Hierarchy")
    if not FEATURE_IMPORTANCE.empty:
        top15 = FEATURE_IMPORTANCE.head(15).sort_values("Importance")
        fig_feat = px.bar(top15, x="Importance", y="Feature", orientation="h", color_discrete_sequence=["#7568FF"])
        fig_feat.update_layout(margin=dict(l=190, r=30, t=25, b=50))
        fig_feat.update_yaxes(automargin=True)
        st.plotly_chart(polish_chart(fig_feat, 550), use_container_width=True)

    st.subheader("Current Live Model Inference Output")
    target_pred = LIVE_PREDS if not LIVE_PREDS.empty else CURRENT_SNAPSHOT
    if not target_pred.empty and "predicted_future_IV" in target_pred.columns:
        show_cols = ["strike", "option_type", "IV", "predicted_IV_change_5m", "predicted_future_IV", "dashboard_signal"]
        st.dataframe(
            target_pred[show_cols].sort_values("strike"),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("The model requires 3 sequential 5-minute snapshots to populate lag features (t-10m and t-5m).")


# ============================================================
# 18. PAGE: ⚖ RELATIVE VALUATION
# ============================================================

elif page == "⚖ Relative Valuation":
    st.title("Live Relative Implied Volatility Valuation")
    st.caption("Quantitative detection of mispriced options based on Random Forest 5-minute volatility velocity forecasts.")

    target_val = LIVE_PREDS if not LIVE_PREDS.empty else CURRENT_SNAPSHOT

    if target_val.empty or "dashboard_signal" not in target_val.columns:
        st.info("Valuation signals will generate once sequential snapshots allow delta predictions.")
    else:
        sig_counts = target_val["dashboard_signal"].value_counts().reset_index()
        sig_counts.columns = ["Valuation Signal", "Contract Count"]

        c_bar, c_info = st.columns([1.6, 1.0])
        with c_bar:
            fig_sig = px.bar(
                sig_counts,
                x="Valuation Signal",
                y="Contract Count",
                color="Valuation Signal",
                color_discrete_map={
                    "LOW IV vs FORECAST": "#35D49A",
                    "HIGH IV vs FORECAST": "#FF7180",
                    "NEUTRAL": "#6FA8FF",
                },
            )
            st.plotly_chart(polish_chart(fig_sig, 280), use_container_width=True)

        with c_info:
            st.markdown(
                """
            <div class="panel" style="min-height:220px">
            <b>Quantitative Signal Legend:</b><br><br>
            🟢 <b>LOW IV vs FORECAST:</b> Predicted volatility expansion (ΔIV > +0.10 pts). Market option is underpricing expected volatility velocity.<br><br>
            🔴 <b>HIGH IV vs FORECAST:</b> Predicted volatility contraction (ΔIV < -0.10 pts). Market option is overpricing expected volatility.<br><br>
            🔵 <b>NEUTRAL:</b> Absolute expected volatility velocity is within threshold (|ΔIV| ≤ 0.10 pts).
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.subheader("Valuation Screener Table")
        val_cols = ["strike", "option_type", "LTP", "IV", "predicted_future_IV", "predicted_IV_change_5m", "dashboard_signal"]
        st.dataframe(
            target_val[val_cols].sort_values("strike"),
            use_container_width=True,
            hide_index=True,
            height=480,
        )


# ============================================================
# 19. PAGE: ⚡ STRESS TESTING (INTERACTIVE LIVE BSM ENGINE)
# ============================================================

elif page == "⚡ Stress Testing":
    st.title("Interactive Live Option Scenario Stress Testing")
    st.caption("Multi-factor Black-Scholes scenario analysis under simultaneous Spot, Volatility, and Time-Decay shocks.")

    if CURRENT_SNAPSHOT.empty:
        st.info("Awaiting live option quotes for interactive pricing. Showing benchmark historical matrix below.")
    else:
        opt_types = sorted(CURRENT_SNAPSHOT["option_type"].unique())
        sc_col1, sc_col2 = st.columns(2)
        with sc_col1:
            stress_type = st.selectbox("Option Type", opt_types, index=0)
        available_opts = CURRENT_SNAPSHOT[CURRENT_SNAPSHOT["option_type"] == stress_type].sort_values("atm_distance")
        with sc_col2:
            stress_strike = st.selectbox("Strike Price (₹)", sorted(available_opts["strike"].dropna().unique()), index=0)

        selected_contract = available_opts[available_opts["strike"] == stress_strike].iloc[0]
        S_base = float(selected_contract["spot"])
        K_base = float(selected_contract["strike"])
        sigma_base = max(float(selected_contract["IV"]) / 100.0, 1e-4)
        mkt_ltp = float(selected_contract["LTP"]) if not pd.isna(selected_contract["LTP"]) else 0.0

        T_years, tte_minutes = compute_exact_tte(selected_expiry)
        r_rate = 0.065  # RBI standard risk-free rate assumption

        base_bs_price, base_delta, base_gamma, base_vega, base_theta = bs_pricing_kernel(
            S_base, K_base, T_years, r_rate, sigma_base, stress_type
        )

        st.markdown("<b>Scenario Parameter Controls</b>", unsafe_allow_html=True)
        sk_col1, sk_col2, sk_col3 = st.columns(3)
        with sk_col1:
            spot_shock_pct = st.slider("Underlying Spot Shock (%)", -5.0, 5.0, 0.0, 0.25)
        with sk_col2:
            iv_shock_pct = st.slider("Relative IV Shock (%)", -50.0, 50.0, 0.0, 5.0)
        with sk_col3:
            max_decay = int(min(max(tte_minutes, 5.0), 360.0))
            time_decay_min = st.slider("Intraday Time Decay (Minutes)", 0, max_decay, 0, 5)

        # Apply stress parameters
        stressed_S = S_base * (1.0 + spot_shock_pct / 100.0)
        stressed_sigma = max(sigma_base * (1.0 + iv_shock_pct / 100.0), 1e-6)
        stressed_minutes = max(tte_minutes - time_decay_min, 0.0)
        stressed_T = stressed_minutes / (365.25 * 24.0 * 60.0)

        stressed_price, str_delta, str_gamma, str_vega, str_theta = bs_pricing_kernel(
            stressed_S, K_base, stressed_T, r_rate, stressed_sigma, stress_type
        )

        val_change = stressed_price - base_bs_price
        pct_change = (val_change / base_bs_price * 100.0) if base_bs_price > 0 else 0.0

        # Stress Metrics Display
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        sm1, sm2, sm3, sm4 = st.columns(4)
        sm1.metric("Live Market LTP", f"₹{mkt_ltp:.2f}")
        sm2.metric("Base BSM Price", f"₹{base_bs_price:.2f}")
        sm3.metric("Stressed BSM Price", f"₹{stressed_price:.2f}")
        sm4.metric("Simulated P&L Move", f"{pct_change:+.2f}%", delta=f"₹{val_change:+.2f}")

        # Greeks Display
        gk1, gk2, gk3, gk4 = st.columns(4)
        gk1.metric("Delta (Δ)", f"{str_delta:.4f}")
        gk2.metric("Gamma (Γ)", f"{str_gamma:.5f}")
        gk3.metric("Vega (ν)", f"₹{str_vega:.2f} / pt")
        gk4.metric("Theta (Θ)", f"₹{str_theta:.2f} / day")

        # Interactive Spot Shock Sensitivity Curve
        shock_range = np.linspace(-5.0, 5.0, 41)
        sim_prices = [
            bs_pricing_kernel(S_base * (1.0 + z / 100.0), K_base, stressed_T, r_rate, stressed_sigma, stress_type)[0]
            for z in shock_range
        ]
        curve_df = pd.DataFrame({"Spot Shock (%)": shock_range, "Theoretical Option Value (₹)": sim_prices})
        fig_curve = px.line(curve_df, x="Spot Shock (%)", y="Theoretical Option Value (₹)", color_discrete_sequence=["#458DFF"])
        fig_curve.add_vline(x=spot_shock_pct, line_dash="dash", line_color="#FF8A37", annotation_text="Stressed Spot")
        st.plotly_chart(polish_chart(fig_curve, 350), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Historical Benchmark Stress Matrix")
    if not HIST_COMBINED_STRESS.empty:
        st.dataframe(HIST_COMBINED_STRESS.round(3), use_container_width=True, hide_index=True)


# ============================================================
# 20. PAGE: 🧪 ROBUSTNESS TEST
# ============================================================

elif page == "🧪 Robustness Test":
    st.title("Structural Regime Shift & Expiry-Day Robustness")
    st.caption("Empirical assessment of model generalization under the non-linear terminal expiry regime (19 Oct 2026).")

    r1, r2, r3 = st.columns(3)
    r1.metric("RF MAE on Expiry Day", "17.4247", delta="+16.90 vs Holdout", delta_color="inverse")
    r2.metric("Persistence MAE", "14.4715", help="Persistence outperformed RF on terminal day")
    r3.metric("Directional Accuracy", "19.09%", help="Severe regime breakdown")

    st.warning("⚠️ **Regime Breakdown Diagnosis:** During the final 2 hours of option expiration, rapid theta decay and pin risk induce extreme volatility velocity spikes. The standard autoregressive Random Forest trained on non-expiry trading regimes experiences severe error expansion, validating the structural necessity for dedicated expiry-regime models.")

    if not HIST_ROBUSTNESS.empty:
        fig_rob = go.Figure()
        fig_rob.add_trace(go.Scatter(x=HIST_ROBUSTNESS["time_label"], y=HIST_ROBUSTNESS["Actual_Mean_Abs_Delta"], mode="lines+markers", name="Actual Mean |ΔIV|", line=dict(color="#67B7FF", width=2)))
        fig_rob.add_trace(go.Scatter(x=HIST_ROBUSTNESS["time_label"], y=HIST_ROBUSTNESS["RF_MAE"], mode="lines+markers", name="Random Forest MAE", line=dict(color="#FF8A37", width=2)))
        fig_rob.update_xaxes(title="Time (IST)")
        fig_rob.update_yaxes(title="IV Points")
        st.plotly_chart(polish_chart(fig_rob, 480), use_container_width=True)


# ============================================================
# 21. PAGE: 🗄 DATA & SETTINGS
# ============================================================

elif page == "🗄 Data & Settings":
    st.title("Pipeline Diagnostics & Session Data Export")
    st.caption("Active configuration, internal worker status, and persistent file management.")

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.subheader("Operational Diagnostics")
        st.write("**Base Workspace:**", str(BASE))
        st.write("**Target Active Expiry:**", selected_expiry)
        st.write("**Collector Worker Status:**", COLLECTOR.status)
        st.write("**Last Collector Message:**", COLLECTOR.message)
        st.write("**Model Features Loaded:**", len(MODEL_FEATURES))
        st.write("**Execution Mode:**", "Live Streaming" if IS_LIVE else "Offline Baseline")

    with d_col2:
        st.subheader("Storage Persistence")
        h_df = read_history()
        st.write("**History File:**", str(HISTORY_FILE))
        st.write("**Total Timestamps in History:**", h_df["time_5m"].nunique() if not h_df.empty else 0)
        st.write("**Prediction Log File:**", str(PREDICTION_LOG_FILE))
        st.write("**Full Chain File:**", str(RAW_CHAIN_FILE))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Download Live Session CSVs")

    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        if LIVE_PREDICTIONS_FILE.exists():
            st.download_button(
                "📥 Download Live Predictions CSV",
                data=LIVE_PREDICTIONS_FILE.read_bytes(),
                file_name="live_iv_predictions.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with exp_col2:
        if HISTORY_FILE.exists():
            st.download_button(
                "📥 Download Snapshot History CSV",
                data=HISTORY_FILE.read_bytes(),
                file_name="live_snapshot_history.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with exp_col3:
        if PREDICTION_LOG_FILE.exists():
            st.download_button(
                "📥 Download Prediction Log CSV",
                data=PREDICTION_LOG_FILE.read_bytes(),
                file_name="live_prediction_log.csv",
                mime="text/csv",
                use_container_width=True,
            )
