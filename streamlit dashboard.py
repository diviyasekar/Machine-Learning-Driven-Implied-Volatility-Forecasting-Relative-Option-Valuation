# ============================================================
# NIFTY 50 IV ANALYSIS & FORECASTING DASHBOARD
# MULTI-PAGE SIDEBAR + PROFESSIONAL OVERVIEW
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NIFTY Options | IV Analysis & Forecasting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #071426;
        color: #E7EEF8;
    }

    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 1rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
        max-width: 100%;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ---------------- SIDEBAR ---------------- */

    section[data-testid="stSidebar"] {
        background: #09182B;
        border-right: 1px solid #203450;
    }

    .brand {
        font-size: 21px;
        font-weight: 750;
        color: white;
    }

    .subtitle {
        color: #91A7C2;
        font-size: 12px;
        margin-bottom: 18px;
    }

    .status-box {
        margin-top: 25px;
        padding: 12px;
        border-radius: 8px;
        background: #0D213A;
        border: 1px solid #1C385B;
    }

    .status-title {
        color: #F3C763;
        font-weight: 700;
        font-size: 12px;
    }

    .status-small {
        color: #8EA5C0;
        font-size: 10px;
        margin-top: 5px;
    }

    /* ---------------- CARDS ---------------- */

    .panel {
        background: #0C1D34;
        border: 1px solid #1D385B;
        border-radius: 9px;
        padding: 14px;
        min-height: 105px;
    }

    .card-label {
        color: #B3C3D7;
        font-size: 12px;
        font-weight: 600;
    }

    .card-value {
        color: white;
        font-size: 25px;
        font-weight: 750;
        margin-top: 7px;
    }

    .card-note {
        color: #879DB8;
        font-size: 10px;
        margin-top: 6px;
    }

    .green {
        color: #35D49A;
    }

    .red {
        color: #FF7180;
    }

    .blue {
        color: #6FA8FF;
    }

    .section-title {
        color: white;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .top-label {
        color: #A6B8CD;
        font-size: 11px;
        font-weight: 600;
    }

    .top-number {
        color: white;
        font-size: 25px;
        font-weight: 750;
    }

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

    [data-testid="stVerticalBlock"] {
        gap: 0.55rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
BASE = PROJECT_DIR if (PROJECT_DIR / "data").exists() else (Path.home() / "Downloads")

PROCESSED = (
    BASE
    / "data"
    / "processed"
)

VALUATION_FILE = (
    PROCESSED
    / "relative_iv_valuation_results.csv"
)

FEATURE_FILE = (
    PROCESSED
    / "final_feature_importance.csv"
)

SPOT_FILE = (
    PROCESSED
    / "stress_test_spot.csv"
)

IV_FILE = (
    PROCESSED
    / "stress_test_iv.csv"
)

COMBINED_FILE = (
    PROCESSED
    / "stress_test_combined_scenarios.csv"
)

EXPIRY_FILE = (
    PROCESSED
    / "rf_19oct_timestamp_performance.csv"
)


# ============================================================
# 4. LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        VALUATION_FILE
    )

    df["time_5m"] = pd.to_datetime(
        df["time_5m"],
        utc=True,
        errors="coerce"
    )

    feature_df = pd.read_csv(
        FEATURE_FILE
    )

    spot_df = pd.read_csv(
        SPOT_FILE
    )

    iv_df = pd.read_csv(
        IV_FILE
    )

    combined_df = pd.read_csv(
        COMBINED_FILE
    )

    expiry_df = pd.read_csv(
        EXPIRY_FILE
    )

    expiry_df["time_5m"] = pd.to_datetime(
        expiry_df["time_5m"],
        utc=True,
        errors="coerce"
    )

    expiry_df["time_IST"] = (
        expiry_df["time_5m"]
        .dt.tz_convert("Asia/Kolkata")
    )

    expiry_df["time_label"] = (
        expiry_df["time_IST"]
        .dt.strftime("%H:%M")
    )

    return (
        df,
        feature_df,
        spot_df,
        iv_df,
        combined_df,
        expiry_df
    )


(
    df,
    feature_df,
    spot_stress,
    iv_stress,
    combined_stress,
    expiry_df
) = load_data()


# ============================================================
# 5. SIDEBAR — ACTUAL NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """<div class="brand">📈 &nbsp; NIFTY Options</div>
<div class="subtitle">IV Analysis & Forecasting</div>""",
        unsafe_allow_html=True
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
            "🗄 Data & Settings"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown(
        """<div class="status-box">
<div class="status-title">● Historical Demo</div>
<div class="status-small">
Live Upstox data will replace the historical backend in Step 25.
</div>
</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# 6. HELPERS
# ============================================================

def format_large_number(x):

    if x >= 1_00_00_000:
        return f"{x / 1_00_00_000:.2f} Cr"

    elif x >= 1_00_000:
        return f"{x / 1_00_000:.2f} L"

    elif x >= 1_000:
        return f"{x / 1_000:.1f} K"

    return f"{x:.0f}"


PAPER = "#0C1D34"
GRID = "#213650"
TEXT = "#C7D4E5"


def polish(fig, height=320):

    fig.update_layout(
        template=None,
        height=height,

        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,

        font=dict(
            color=TEXT,
            size=11
        ),

        margin=dict(
            l=55,
            r=20,
            t=40,
            b=50
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(
        gridcolor=GRID,
        tickfont=dict(
            size=10
        )
    )

    fig.update_yaxes(
        gridcolor=GRID,
        tickfont=dict(
            size=10
        )
    )

    return fig


# ============================================================
# 7. LATEST SNAPSHOT
# ============================================================

latest_time = df["time_5m"].max()

latest_snapshot = (
    df[
        df["time_5m"] == latest_time
    ]
    .copy()
)

latest_snapshot["atm_distance"] = (
    latest_snapshot["moneyness"]
    - 1
).abs()

atm_row = (
    latest_snapshot
    .sort_values("atm_distance")
    .iloc[0]
)

spot = float(
    atm_row["spot"]
)

current_iv = float(
    atm_row["IV"]
)

pred_iv = float(
    atm_row["predicted_future_IV"]
)

pred_delta = float(
    atm_row["predicted_IV_change_5m"]
)

snapshot_volume = (
    latest_snapshot["Volume"]
    .fillna(0)
    .sum()
)


# ============================================================
# 8. COMMON HEADER
# ============================================================

h1, h2, h3 = st.columns(
    [2.2, 1, 1]
)

with h1:

    st.markdown(
        f"""<div class="top-label">NIFTY 50</div>
<div class="top-number">{spot:,.2f}</div>""",
        unsafe_allow_html=True
    )


# Historical data has only one expiry.
# Live Upstox data will populate more values automatically.

with h2:

    expiry_choice = st.selectbox(
        "Expiry",
        [
            "19 Oct 2026"
        ],
        label_visibility="collapsed",
        help=(
            "Only one expiry exists in this historical dataset. "
            "The live version will list available expiries."
        )
    )


with h3:

    option_filter = st.selectbox(
        "Option Type",
        [
            "Both (Call & Put)",
            "Call",
            "Put"
        ],
        label_visibility="collapsed"
    )


# ============================================================
# 9. OPTION FILTER
# ============================================================

if option_filter == "Call":

    display_snapshot = (
        latest_snapshot[
            latest_snapshot["option_type"]
            == "CE"
        ]
        .copy()
    )

elif option_filter == "Put":

    display_snapshot = (
        latest_snapshot[
            latest_snapshot["option_type"]
            == "PE"
        ]
        .copy()
    )

else:

    display_snapshot = latest_snapshot.copy()


# ============================================================
# REUSABLE CHART FUNCTIONS
# ============================================================

def volatility_smile_chart(data):

    smile = (
        data[
            [
                "strike",
                "IV",
                "option_type"
            ]
        ]
        .dropna()
        .sort_values("strike")
    )

    fig = px.line(
        smile,
        x="strike",
        y="IV",
        color="option_type",
        markers=True,
        color_discrete_map={
            "CE": "#458DFF",
            "PE": "#FF7F32"
        }
    )

    fig.update_xaxes(
        title="Strike Price"
    )

    fig.update_yaxes(
        title="Implied Volatility (%)"
    )

    return polish(
        fig,
        height=330
    )


def moneyness_chart(data):

    money = (
        data[
            [
                "moneyness",
                "IV",
                "option_type"
            ]
        ]
        .dropna()
    )

    fig = px.scatter(
        money,
        x="moneyness",
        y="IV",
        color="option_type",
        color_discrete_map={
            "CE": "#458DFF",
            "PE": "#FF7F32"
        }
    )

    fig.update_xaxes(
        title="Moneyness"
    )

    fig.update_yaxes(
        title="IV (%)"
    )

    return polish(
        fig,
        height=330
    )


def prediction_chart():

    chart = (
        df.groupby(
            "time_5m",
            as_index=False
        )[
            [
                "IV_t_plus_5",
                "predicted_future_IV"
            ]
        ]
        .mean()
        .sort_values("time_5m")
    )

    chart["Observation"] = np.arange(
        len(chart)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart["Observation"],
            y=chart["IV_t_plus_5"],
            mode="lines+markers",
            name="Actual IV",
            line=dict(
                color="#458DFF",
                width=2
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart["Observation"],
            y=chart["predicted_future_IV"],
            mode="lines",
            name="Predicted IV",
            line=dict(
                color="#FF8A37",
                width=2,
                dash="dash"
            )
        )
    )

    fig.update_xaxes(
        title="Observation Index"
    )

    fig.update_yaxes(
        title="IV (%)"
    )

    return polish(
        fig,
        height=330
    )


# ============================================================
# PAGE: OVERVIEW
# ============================================================

if page == "🏠 Overview":

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(
            f"""<div class="panel">
<div class="card-label">Current IV (ATM)</div>
<div class="card-value">{current_iv:.2f}%</div>
<div class="card-note">Latest historical snapshot</div>
</div>""",
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""<div class="panel">
<div class="card-label">NIFTY Spot Price</div>
<div class="card-value">{spot:,.2f}</div>
<div class="card-note blue">Underlying index level</div>
</div>""",
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""<div class="panel">
<div class="card-label">Snapshot Volume</div>
<div class="card-value">{format_large_number(snapshot_volume)}</div>
<div class="card-note">Available option volume</div>
</div>""",
            unsafe_allow_html=True
        )

    with c4:

        direction_class = (
            "green"
            if pred_delta >= 0
            else "red"
        )

        st.markdown(
            f"""<div class="panel">
<div class="card-label">Model Prediction (Next 5 min)</div>
<div class="card-value">{pred_iv:.2f}%</div>
<div class="card-note {direction_class}">ΔIV {pred_delta:+.3f}</div>
</div>""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # THREE CHARTS
    # --------------------------------------------------------

    g1, g2, g3 = st.columns(3)

    with g1:

        st.markdown(
            '<div class="section-title">Volatility Smile</div>',
            unsafe_allow_html=True
        )

        st.plotly_chart(
            volatility_smile_chart(
                display_snapshot
            ),
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    with g2:

        st.markdown(
            '<div class="section-title">IV by Moneyness</div>',
            unsafe_allow_html=True
        )

        st.plotly_chart(
            moneyness_chart(
                display_snapshot
            ),
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    with g3:

        st.markdown(
            '<div class="section-title">IV Prediction vs Actual</div>',
            unsafe_allow_html=True
        )

        st.plotly_chart(
            prediction_chart(),
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    # --------------------------------------------------------
    # SECOND ROW
    # --------------------------------------------------------

    p1, p2, p3 = st.columns(
        [1.2, 1.05, 1.1]
    )


    with p1:

        st.markdown(
            '<div class="section-title">Option Chain (Near ATM)</div>',
            unsafe_allow_html=True
        )

        near_atm = (
            display_snapshot[
                (
                    display_snapshot[
                        "moneyness"
                    ]
                    >= 0.97
                )
                &
                (
                    display_snapshot[
                        "moneyness"
                    ]
                    <= 1.03
                )
            ]
            .sort_values("strike")
            .copy()
        )

        option_table = (
            near_atm[
                [
                    "strike",
                    "option_type",
                    "LTP",
                    "IV",
                    "Volume",
                    "OI"
                ]
            ]
            .copy()
        )

        option_table.columns = [
            "Strike",
            "Type",
            "LTP",
            "IV (%)",
            "Volume",
            "OI"
        ]

        st.dataframe(
            option_table.head(10),
            use_container_width=True,
            hide_index=True,
            height=300
        )


    with p2:

        st.markdown(
            '<div class="section-title">ML Model Performance</div>',
            unsafe_allow_html=True
        )

        performance = pd.DataFrame(
            {
                "Model": [
                    "Persistence",
                    "Random Forest",
                    "XGBoost"
                ],

                "MAE": [
                    0.5505,
                    0.5214,
                    0.5530
                ],

                "RMSE": [
                    1.3207,
                    1.2188,
                    1.2964
                ]
            }
        )

        st.dataframe(
            performance,
            use_container_width=True,
            hide_index=True,
            height=150
        )

        st.markdown(
            '<div class="section-title">Feature Importance</div>',
            unsafe_allow_html=True
        )

        top5 = (
            feature_df
            .head(5)
            .sort_values("Importance")
        )

        fig = px.bar(
            top5,
            x="Importance",
            y="Feature",
            orientation="h",
            color_discrete_sequence=[
                "#7568FF"
            ]
        )

        # This fixes the cramped / blurry labels

        fig.update_layout(
            height=220,
            showlegend=False,
            margin=dict(
                l=125,
                r=10,
                t=5,
                b=40
            )
        )

        fig.update_yaxes(
            tickfont=dict(
                size=11
            ),
            automargin=True
        )

        polish(
            fig,
            height=220
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    with p3:

        st.markdown(
            '<div class="section-title">Relative Valuation</div>',
            unsafe_allow_html=True
        )

        valuation = (
            display_snapshot[
                [
                    "strike",
                    "option_type",
                    "IV",
                    "predicted_future_IV",
                    "predicted_IV_change_5m",
                    "relative_IV_valuation"
                ]
            ]
            .copy()
            .sort_values("strike")
        )

        valuation.columns = [
            "Strike",
            "Type",
            "Market IV",
            "Model IV",
            "Diff.",
            "Signal"
        ]

        valuation["Signal"] = (
            valuation["Signal"]
            .replace(
                {
                    "RELATIVELY UNDERVALUED IV":
                        "Low IV",

                    "RELATIVELY OVERVALUED IV":
                        "High IV",

                    "FAIR / NEUTRAL":
                        "Neutral"
                }
            )
        )

        st.dataframe(
            valuation.head(10),
            use_container_width=True,
            hide_index=True,
            height=300
        )


    # --------------------------------------------------------
    # STRESS SUMMARY ON OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Stress Testing</div>',
        unsafe_allow_html=True
    )

    stress_summary = (
        combined_stress[
            [
                "Scenario",
                "Spot",
                "IV_%",
                "Option_Value",
                "Value_Change_%"
            ]
        ]
        .copy()
    )

    stress_summary.columns = [
        "Scenario",
        "Spot Price",
        "IV (%)",
        "Option Value",
        "Price Move (%)"
    ]

    st.dataframe(
        stress_summary.round(2),
        use_container_width=True,
        hide_index=True,
        height=220
    )


# ============================================================
# PAGE: OPTION CHAIN
# ============================================================

elif page == "⛓ Option Chain":

    st.title(
        "Option Chain"
    )

    st.caption(
        "Near-ATM and full option-chain observations."
    )

    chain = (
        display_snapshot
        .sort_values(
            [
                "strike",
                "option_type"
            ]
        )
    )

    st.dataframe(
        chain[
            [
                "option_type",
                "strike",
                "spot",
                "LTP",
                "IV",
                "Volume",
                "OI",
                "Bid",
                "Ask",
                "moneyness"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=650
    )


# ============================================================
# PAGE: VOLATILITY SMILE
# ============================================================

elif page == "📉 Volatility Smile":

    st.title(
        "Volatility Smile Analysis"
    )

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            volatility_smile_chart(
                display_snapshot
            ),
            use_container_width=True
        )

    with right:

        st.plotly_chart(
            moneyness_chart(
                display_snapshot
            ),
            use_container_width=True
        )


# ============================================================
# PAGE: ML MODEL
# ============================================================

elif page == "🧠 ML Model":

    st.title(
        "Machine Learning Model"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "RF MAE",
        "0.5214"
    )

    c2.metric(
        "RF RMSE",
        "1.2188"
    )

    c3.metric(
        "RF R²",
        "0.9866"
    )


    st.subheader(
        "Model Comparison"
    )

    model_comparison = pd.DataFrame(
        {
            "Model": [
                "Persistence",
                "Random Forest + Lag",
                "XGBoost + Lag"
            ],

            "MAE": [
                0.550478,
                0.521398,
                0.552956
            ],

            "RMSE": [
                1.320669,
                1.218771,
                1.296449
            ]
        }
    )

    st.dataframe(
        model_comparison,
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Top 15 Feature Importances"
    )

    top15 = (
        feature_df
        .head(15)
        .sort_values("Importance")
    )

    fig = px.bar(
        top15,
        x="Importance",
        y="Feature",
        orientation="h",
        color_discrete_sequence=[
            "#7568FF"
        ]
    )

    fig.update_layout(
        margin=dict(
            l=180,
            r=30,
            t=25,
            b=50
        )
    )

    fig.update_yaxes(
        automargin=True,
        tickfont=dict(
            size=12
        )
    )

    polish(
        fig,
        height=620
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE: RELATIVE VALUATION
# ============================================================

elif page == "⚖ Relative Valuation":

    st.title(
        "Relative IV Valuation"
    )

    valuation = (
        display_snapshot[
            [
                "strike",
                "option_type",
                "LTP",
                "IV",
                "predicted_future_IV",
                "predicted_IV_change_5m",
                "relative_IV_valuation"
            ]
        ]
        .copy()
    )

    valuation.columns = [
        "Strike",
        "Type",
        "LTP",
        "Market IV",
        "Forecast IV",
        "Forecast Gap",
        "Signal"
    ]

    st.dataframe(
        valuation,
        use_container_width=True,
        hide_index=True,
        height=520
    )

    counts = (
        df[
            "relative_IV_valuation"
        ]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "Status",
        "Count"
    ]

    fig = px.bar(
        counts,
        x="Status",
        y="Count",
        color_discrete_sequence=[
            "#458DFF"
        ]
    )

    polish(
        fig,
        height=360
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE: STRESS TESTING
# ============================================================

elif page == "⚡ Stress Testing":

    st.title(
        "Option Stress Testing"
    )

    left, right = st.columns(2)


    with left:

        st.subheader(
            "Spot Shock"
        )

        fig = px.line(
            spot_stress,
            x="Spot_Shock_%",
            y="Option_Value",
            markers=True,
            color_discrete_sequence=[
                "#458DFF"
            ]
        )

        polish(
            fig,
            height=380
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with right:

        st.subheader(
            "IV Shock"
        )

        fig = px.line(
            iv_stress,
            x="Stressed_IV_%",
            y="Option_Value",
            markers=True,
            color_discrete_sequence=[
                "#FF7F32"
            ]
        )

        polish(
            fig,
            height=380
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader(
        "Combined Scenarios"
    )

    st.dataframe(
        combined_stress.round(3),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PAGE: ROBUSTNESS
# ============================================================

elif page == "🧪 Robustness Test":

    st.title(
        "Expiry-Day Robustness Test"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "RF MAE",
        "17.4247"
    )

    c2.metric(
        "Persistence MAE",
        "14.4715"
    )

    c3.metric(
        "Direction Accuracy",
        "19.09%"
    )


    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=expiry_df["time_label"],
            y=expiry_df[
                "Actual_Mean_Abs_Delta"
            ],
            mode="lines+markers",
            name="Actual Mean |ΔIV|",
            line=dict(
                color="#67B7FF"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=expiry_df["time_label"],
            y=expiry_df["RF_MAE"],
            mode="lines+markers",
            name="RF MAE",
            line=dict(
                color="#FF8A37"
            )
        )
    )

    fig.update_xaxes(
        title="Time (IST)"
    )

    fig.update_yaxes(
        title="IV Points"
    )

    polish(
        fig,
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGE: DATA & SETTINGS
# ============================================================

elif page == "🗄 Data & Settings":

    st.title(
        "Data & Settings"
    )

    st.write(
        "Current mode: Historical demonstration"
    )

    st.write(
        "Development rows:",
        len(df)
    )

    st.write(
        "Latest historical timestamp:",
        latest_time
    )

    st.write(
        "Available option types:",
        sorted(
            df["option_type"]
            .dropna()
            .unique()
        )
    )

    st.info(
        """
        Only one expiry is available in the current historical
        valuation dataset.

        After live Upstox integration, this page will show
        available market expiries and live refresh information.
        """
    )