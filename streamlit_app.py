import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="WAVES Intelligence™ — Institutional Wave Console",
    layout="wide",
)

# ---------------------------------------------------------
# Dark theme + WAVES styling
# ---------------------------------------------------------
DARK_BG = "#020617"   # almost black
CARD_BG = "#020818"
TEXT_MAIN = "#E5E7EB"
TEXT_MUTED = "#9CA3AF"
ACCENT = "#22C55E"
ACCENT_SOFT = "#38BDF8"
BORDER = "#1F2937"

CUSTOM_CSS = f"""
<style>
    .stApp {{
        background-color: {DARK_BG} !important;
    }}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {TEXT_MAIN} !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}
    .metric-card {{
        background: radial-gradient(circle at top left, #0F172A, #020617);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        border: 1px solid {BORDER};
        box-shadow: 0 18px 40px rgba(0,0,0,0.60);
    }}
    .metric-label {{
        font-size: 0.72rem;
        letter-spacing: .16em;
        text-transform: uppercase;
        color: {TEXT_MUTED};
    }}
    .metric-value {{
        font-size: 1.6rem;
        font-weight: 600;
        margin-top: 2px;
    }}
    .metric-sub {{
        font-size: 0.72rem;
        color: {TEXT_MUTED};
    }}
    .section-card {{
        background: {CARD_BG};
        border-radius: 14px;
        padding: 1rem 1.25rem 1.1rem 1.25rem;
        border: 1px solid {BORDER};
    }}
    .section-title {{
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }}
    .section-caption {{
        font-size: 0.75rem;
        color: {TEXT_MUTED};
        margin-bottom: 0.6rem;
    }}
    .sidebar-title {{
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Wave definitions (15 Waves)
# ---------------------------------------------------------
WAVES = {
    "sp500": {
        "label": "S&P 500 Wave (LIVE Demo)",
        "benchmark": "S&P 500 Index",
        "csv_hint": "SP500_PORTFOLIO_FINAL.csv export",
        "wave_type": "AI-Managed Wave",
    },
    # Add other waves as before...
}

# ---------------------------------------------------------
# Sidebar: wave selector + CSV upload
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<div style='font-size:1.1rem;font-weight:600;margin-bottom:0.25rem;'>"
        "🌊 WAVES Intelligence™</div>",
        unsafe_allow_html=True,
    )
    st.caption("Institutional Wave Console (alpha demo)")

    wave_label_to_key = {cfg["label"]: key for key, cfg in WAVES.items()}
    chosen_label = st.selectbox(
        "Select Wave",
        options=list(wave_label_to_key.keys()),
        index=0,
    )
    wave_key = wave_label_to_key[chosen_label]
    wave_cfg = WAVES[wave_key]

    st.markdown(
        f"<div class='sidebar-title'>Wave type:</div>"
        f"<span style='font-size:0.8rem;color:{TEXT_MUTED};'>{wave_cfg['wave_type']} • "
        f"Benchmark: {wave_cfg['benchmark']}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("<div class='sidebar-title'>Upload latest Wave snapshot (.csv)</div>", unsafe_allow_html=True)
    st.caption(
        f"Expected columns (any order): **Ticker, Price, Dollar_Alloc** "
        f"(optional: Weight_pct, Index_Weight).<br>"
        f"Suggested export: `{{wave_cfg['csv_hint']}}`",
        unsafe_allow_html=True,
    )

    portfolio_file = st.file_uploader(
        "Upload Wave CSV",
        type=["csv"],
        label_visibility="collapsed",
        key="wave_csv",
    )

# ---------------------------------------------------------
# Validate uploaded CSV
# ---------------------------------------------------------
if portfolio_file is None:
    st.info("Upload the latest Wave snapshot CSV in the sidebar to continue.")
    st.stop()

try:
    raw_df = pd.read_csv(portfolio_file)
    raw_df.columns = [c.strip().replace(" ", "_") for c in raw_df.columns]  # Normalize column names
except Exception as e:
    st.error(f"Error reading your CSV file: {e}")
    st.stop()

# Required columns
REQUIRED_COLUMNS = ["Ticker", "Price", "Dollar_Alloc"]
missing_columns = [col for col in REQUIRED_COLUMNS if col not in raw_df.columns]

if missing_columns:
    st.error(f"Your CSV is missing the following required columns: {', '.join(missing_columns)}.")
    st.stop()

# Ensure numeric columns
for num_col in ["Price", "Dollar_Alloc"]:
    raw_df[num_col] = pd.to_numeric(raw_df[num_col], errors="coerce")

if raw_df.isnull().any(axis=None):
    st.warning("Some numeric values in your CSV file could not be interpreted.")

# Normalize weights
total_nav = raw_df["Dollar_Alloc"].sum()
raw_df["Weight_pct"] = raw_df["Dollar_Alloc"] / total_nav * 100.0
...

# ---------------------------------------------------------
# TODO: Add visualization and metric updates from your code!
# ---------------------------------------------------------
