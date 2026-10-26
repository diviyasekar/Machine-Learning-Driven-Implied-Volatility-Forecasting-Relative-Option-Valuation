# ============================================================
# STEP 25B
# AUTOMATIC 5-MINUTE LIVE IV PREDICTION ENGINE
# ============================================================

import os
import time
import joblib
import requests
import pandas as pd
import numpy as np

from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
BASE = PROJECT_DIR if (PROJECT_DIR / "data").exists() else (Path.home() / "Downloads")

MODEL_FOLDER = BASE / "models"
LIVE_FOLDER = BASE / "data" / "live"

LIVE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_FILE = (
    MODEL_FOLDER /
    "nifty_iv_random_forest.joblib"
)

FEATURE_FILE = (
    MODEL_FOLDER /
    "nifty_iv_model_features.joblib"
)

MEDIAN_FILE = (
    MODEL_FOLDER /
    "nifty_iv_feature_medians.joblib"
)

SNAPSHOT_HISTORY_FILE = (
    LIVE_FOLDER /
    "live_snapshot_history.csv"
)

LIVE_OUTPUT_FILE = (
    LIVE_FOLDER /
    "live_iv_predictions.csv"
)


# ============================================================
# 2. LOAD TOKEN
# ============================================================

load_dotenv(
    BASE / ".env"
)

ACCESS_TOKEN = os.getenv(
    "UPSTOX_ACCESS_TOKEN"
)

if not ACCESS_TOKEN:
    raise ValueError(
        "UPSTOX_ACCESS_TOKEN was not found in .env"
    )


# ============================================================
# 3. LOAD MODEL
# ============================================================

model = joblib.load(
    MODEL_FILE
)

model_features = joblib.load(
    FEATURE_FILE
)

training_medians = joblib.load(
    MEDIAN_FILE
)


print("=" * 80)
print("LIVE MODEL LOADED")
print("=" * 80)

print(
    "Model:",
    type(model)
)

print(
    "Number of features:",
    len(model_features)
)


# ============================================================
# 4. UPSTOX SETTINGS
# ============================================================

UNDERLYING_KEY = (
    "NSE_INDEX|Nifty 50"
)

OPTION_CHAIN_URL = (
    "https://api.upstox.com/v2/option/chain"
)

OPTION_CONTRACT_URL = (
    "https://api.upstox.com/v2/option/contract"
)

HEADERS = {
    "Accept":
        "application/json",

    "Authorization":
        f"Bearer {ACCESS_TOKEN}"
}


# ============================================================
# 5. SAFE NUMBER FUNCTION
# ============================================================

def num(value):

    try:
        if value is None:
            return np.nan

        return float(value)

    except:
        return np.nan


# ============================================================
# 6. GET EXPIRIES
# ============================================================

def get_available_expiries():

    params = {
        "instrument_key":
            UNDERLYING_KEY
    }

    response = requests.get(
        OPTION_CONTRACT_URL,
        headers=HEADERS,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json().get(
        "data",
        []
    )

    expiries = sorted({

        item.get("expiry")

        for item in data

        if item.get("expiry")
    })

    return expiries


# ============================================================
# 7. CHOOSE NEAREST EXPIRY
# ============================================================

def choose_nearest_expiry():

    expiries = get_available_expiries()

    if not expiries:
        raise ValueError(
            "No NIFTY expiries returned."
        )

    today = pd.Timestamp.now(
        tz="Asia/Kolkata"
    ).date()

    future_expiries = [

        expiry

        for expiry in expiries

        if pd.to_datetime(
            expiry
        ).date() >= today
    ]

    if not future_expiries:
        raise ValueError(
            "No current/future expiry available."
        )

    return future_expiries[0]


# ============================================================
# 8. FETCH OPTION CHAIN
# ============================================================

def fetch_option_chain(expiry):

    params = {

        "instrument_key":
            UNDERLYING_KEY,

        "expiry_date":
            expiry
    }

    response = requests.get(
        OPTION_CHAIN_URL,
        headers=HEADERS,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    result = response.json()

    if result.get("status") != "success":
        raise ValueError(
            f"Upstox response not successful: {result}"
        )

    return result.get(
        "data",
        []
    )


# ============================================================
# 9. PARSE CHAIN
# ============================================================

def parse_option_chain(
    chain,
    expiry
):

    timestamp = (
        pd.Timestamp.now(
            tz="UTC"
        )
        .round("min")
    )

    rows = []

    for item in chain:

        strike = num(
            item.get(
                "strike_price"
            )
        )

        spot = num(
            item.get(
                "underlying_spot_price"
            )
        )

        for source_key, option_type in [

            (
                "call_options",
                "CE"
            ),

            (
                "put_options",
                "PE"
            )
        ]:

            option = (
                item.get(
                    source_key
                )
                or {}
            )

            market = (
                option.get(
                    "market_data"
                )
                or {}
            )

            greeks = (
                option.get(
                    "option_greeks"
                )
                or {}
            )

            rows.append({

                "time_5m":
                    timestamp,

                "expiry":
                    expiry,

                "option_type":
                    option_type,

                "option_type_code":
                    (
                        0
                        if option_type == "CE"
                        else 1
                    ),

                "strike":
                    strike,

                "spot":
                    spot,

                "LTP":
                    num(
                        market.get(
                            "ltp"
                        )
                    ),

                "Volume":
                    num(
                        market.get(
                            "volume"
                        )
                    ),

                "OI":
                    num(
                        market.get(
                            "oi"
                        )
                    ),

                "Bid":
                    num(
                        market.get(
                            "bid_price"
                        )
                    ),

                "Ask":
                    num(
                        market.get(
                            "ask_price"
                        )
                    ),

                "IV":
                    num(
                        greeks.get(
                            "iv"
                        )
                    )
            })

    return pd.DataFrame(
        rows
    )


# ============================================================
# 10. CURRENT FEATURES
# ============================================================

def add_current_features(df):

    df = df.copy()

    df["moneyness"] = (
        df["strike"]
        /
        df["spot"]
    )

    df["distance_from_ATM_pct"] = (
        abs(
            df["strike"]
            -
            df["spot"]
        )
        /
        df["spot"]
        * 100
    )

    df["bid_ask_spread"] = (
        df["Ask"]
        -
        df["Bid"]
    )

    df["mid_price"] = (
        df["Ask"]
        +
        df["Bid"]
    ) / 2

    df["relative_spread_pct"] = np.where(

        df["mid_price"] > 0,

        (
            df["bid_ask_spread"]
            /
            df["mid_price"]
            * 100
        ),

        np.nan
    )


    # ========================================================
    # PCR
    # ========================================================

    total_put_oi = (
        df.loc[
            df["option_type"] == "PE",
            "OI"
        ]
        .fillna(0)
        .sum()
    )

    total_call_oi = (
        df.loc[
            df["option_type"] == "CE",
            "OI"
        ]
        .fillna(0)
        .sum()
    )

    if total_call_oi > 0:

        pcr = (
            total_put_oi
            /
            total_call_oi
        )

    else:

        pcr = np.nan

    df["pcr"] = pcr


    # ========================================================
    # DAYS TO EXPIRY
    # ========================================================

    current_ist = (
        df["time_5m"]
        .dt.tz_convert(
            "Asia/Kolkata"
        )
    )

    expiry_dates = pd.to_datetime(
        df["expiry"]
    ).dt.date

    df["days_to_expiry"] = [

        (
            expiry_date
            -
            current_time.date()
        ).days

        for expiry_date, current_time
        in zip(
            expiry_dates,
            current_ist
        )
    ]

    return df


# ============================================================
# 11. NEAR-ATM FILTER
# ============================================================

def filter_near_atm(df):

    return (
        df[
            (df["moneyness"] >= 0.95)
            &
            (df["moneyness"] <= 1.05)
            &
            (df["IV"] > 0)
        ]
        .copy()
    )


# ============================================================
# 12. APPEND SNAPSHOT HISTORY
# ============================================================

def append_history(snapshot):

    if SNAPSHOT_HISTORY_FILE.exists():

        history = pd.read_csv(
            SNAPSHOT_HISTORY_FILE
        )

        history["time_5m"] = pd.to_datetime(
            history["time_5m"],
            utc=True,
            errors="coerce"
        )

        history = pd.concat(
            [
                history,
                snapshot
            ],
            ignore_index=True
        )

    else:

        history = snapshot.copy()


    history = (
        history

        .drop_duplicates(
            subset=[
                "time_5m",
                "expiry",
                "strike",
                "option_type"
            ],
            keep="last"
        )

        .sort_values(
            "time_5m"
        )
    )

    history.to_csv(
        SNAPSHOT_HISTORY_FILE,
        index=False
    )

    return history


# ============================================================
# 13. LAG FEATURES
# ============================================================

def add_lag_features(history):

    history = history.copy()

    history["time_5m"] = pd.to_datetime(
        history["time_5m"],
        utc=True,
        errors="coerce"
    )

    keys = [
        "expiry",
        "strike",
        "option_type"
    ]

    lag_variables = [
        "IV",
        "spot",
        "LTP",
        "Volume",
        "OI",
        "bid_ask_spread"
    ]


    # ========================================================
    # 5 MINUTE LAG
    # ========================================================

    lag5 = history[
        keys
        +
        ["time_5m"]
        +
        lag_variables
    ].copy()

    lag5["time_5m"] = (
        lag5["time_5m"]
        +
        pd.Timedelta(
            minutes=5
        )
    )

    lag5 = lag5.rename(
        columns={
            var:
                f"{var}_lag_5m"

            for var in lag_variables
        }
    )


    # ========================================================
    # 10 MINUTE LAG
    # ========================================================

    lag10 = history[
        keys
        +
        ["time_5m"]
        +
        lag_variables
    ].copy()

    lag10["time_5m"] = (
        lag10["time_5m"]
        +
        pd.Timedelta(
            minutes=10
        )
    )

    lag10 = lag10.rename(
        columns={
            var:
                f"{var}_lag_10m"

            for var in lag_variables
        }
    )


    result = history.merge(
        lag5,
        on=keys + ["time_5m"],
        how="left"
    )

    result = result.merge(
        lag10,
        on=keys + ["time_5m"],
        how="left"
    )


    # ========================================================
    # MOMENTUM FEATURES
    # ========================================================

    for var in lag_variables:

        result[
            f"{var}_change_prev_5m"
        ] = (
            result[var]
            -
            result[
                f"{var}_lag_5m"
            ]
        )

        result[
            f"{var}_change_prev_10m"
        ] = (
            result[var]
            -
            result[
                f"{var}_lag_10m"
            ]
        )

    return result


# ============================================================
# 14. MAKE PREDICTION
# ============================================================

def make_prediction(history):

    lagged = add_lag_features(
        history
    )

    latest_timestamp = (
        lagged["time_5m"]
        .max()
    )

    latest = lagged[
        lagged["time_5m"]
        ==
        latest_timestamp
    ].copy()


    latest = latest.dropna(
        subset=[
            "IV_lag_5m",
            "IV_lag_10m"
        ]
    )


    if latest.empty:

        print(
            "\nNot enough lag history yet."
        )

        print(
            "Need current + exact 5-minute + exact 10-minute snapshots."
        )

        return None


    X_live = (
        latest[
            model_features
        ]
        .copy()
    )

    X_live = X_live.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )

    X_live = X_live.fillna(
        training_medians
    )


    latest[
        "predicted_IV_change_5m"
    ] = model.predict(
        X_live
    )


    latest[
        "predicted_future_IV"
    ] = (
        latest["IV"]
        +
        latest[
            "predicted_IV_change_5m"
        ]
    )


    threshold = 0.10


    latest[
        "relative_IV_valuation"
    ] = np.where(

        latest[
            "predicted_IV_change_5m"
        ] > threshold,

        "RELATIVELY UNDERVALUED IV",

        np.where(

            latest[
                "predicted_IV_change_5m"
            ] < -threshold,

            "RELATIVELY OVERVALUED IV",

            "FAIR / NEUTRAL"
        )
    )


    latest[
        "dashboard_signal"
    ] = latest[
        "relative_IV_valuation"
    ].replace({

        "RELATIVELY UNDERVALUED IV":
            "LOW IV vs FORECAST",

        "RELATIVELY OVERVALUED IV":
            "HIGH IV vs FORECAST",

        "FAIR / NEUTRAL":
            "NEUTRAL"
    })


    latest.to_csv(
        LIVE_OUTPUT_FILE,
        index=False
    )


    print("\n" + "=" * 80)
    print("LIVE PREDICTION CREATED")
    print("=" * 80)

    print(
        "Prediction timestamp:",
        latest_timestamp
    )

    print(
        "Rows predicted:",
        len(latest)
    )

    print(
        "\nSaved:"
    )

    print(
        LIVE_OUTPUT_FILE
    )


    print(
        "\nSample predictions:"
    )

    print(

        latest[
            [
                "strike",
                "option_type",
                "spot",
                "IV",
                "predicted_IV_change_5m",
                "predicted_future_IV",
                "dashboard_signal"
            ]
        ]

        .head(10)

        .round(4)

        .to_string(
            index=False
        )
    )


    return latest


# ============================================================
# 15. ONE DATA-COLLECTION CYCLE
# ============================================================

def run_cycle():

    print("\n" + "=" * 80)

    print(
        "FETCHING LIVE SNAPSHOT"
    )

    print(
        "Local time:",
        pd.Timestamp.now(
            tz="Asia/Kolkata"
        )
    )

    print("=" * 80)


    expiry = choose_nearest_expiry()


    print(
        "Nearest expiry:",
        expiry
    )


    chain = fetch_option_chain(
        expiry
    )


    print(
        "Strikes received:",
        len(chain)
    )


    snapshot = parse_option_chain(
        chain,
        expiry
    )


    snapshot = add_current_features(
        snapshot
    )


    snapshot = filter_near_atm(
        snapshot
    )


    print(
        "Near-ATM valid rows:",
        len(snapshot)
    )


    history = append_history(
        snapshot
    )


    print(
        "Stored unique timestamps:",
        history["time_5m"].nunique()
    )


    make_prediction(
        history
    )


# ============================================================
# 16. CALCULATE WAIT TO NEXT 5-MINUTE BOUNDARY
# ============================================================

def seconds_until_next_5min():

    now = pd.Timestamp.now(
        tz="Asia/Kolkata"
    )

    next_time = (
        now.ceil("5min")
    )

    seconds = (
        next_time
        -
        now
    ).total_seconds()


    # avoid an immediate zero-second loop
    if seconds < 2:
        seconds = 300


    return int(
        seconds
    )


# ============================================================
# 17. CONTINUOUS LOOP
# ============================================================

def run_continuously():

    print("\n" + "=" * 80)
    print("AUTOMATIC 5-MINUTE MODE STARTED")
    print("=" * 80)

    print(
        "Press Ctrl + C to stop."
    )


    while True:

        try:

            run_cycle()

        except requests.exceptions.ReadTimeout:

            print(
                "\nRead timeout. "
                "Skipping this cycle."
            )

        except requests.exceptions.ConnectTimeout:

            print(
                "\nConnection timeout. "
                "Skipping this cycle."
            )

        except requests.exceptions.ConnectionError as e:

            print(
                "\nConnection error:"
            )

            print(e)

        except KeyboardInterrupt:

            print(
                "\nLive pipeline stopped by user."
            )

            break

        except Exception as e:

            print(
                "\nERROR:"
            )

            print(
                type(e).__name__,
                str(e)
            )


        wait_seconds = (
            seconds_until_next_5min()
        )


        print(
            f"\nNext snapshot in approximately "
            f"{wait_seconds} seconds."
        )


        try:

            time.sleep(
                wait_seconds
            )

        except KeyboardInterrupt:

            print(
                "\nLive pipeline stopped by user."
            )

            break


# ============================================================
# 18. START PROGRAM
# ============================================================

if __name__ == "__main__":

    run_continuously()