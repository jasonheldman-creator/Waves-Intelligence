import streamlit as st
import pandas as pd
import numpy as np

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
    "us_growth": {
        "label": "US Growth Wave",
        "benchmark": "Russell 1000 Growth",
        "csv_hint": "US_GROWTH_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "us_value": {
        "label": "US Value Wave",
        "benchmark": "Russell 1000 Value",
        "csv_hint": "US_VALUE_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "smcap_growth": {
        "label": "Small Cap Growth Wave",
        "benchmark": "Russell 2000 Growth",
        "csv_hint": "SMALL_CAP_GROWTH_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "sm_mid_growth": {
        "label": "Small-Mid Cap Growth Wave",
        "benchmark": "SMID Growth Composite",
        "csv_hint": "SMID_GROWTH_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "income": {
        "label": "Equity Income Wave",
        "benchmark": "US Dividend Composite",
        "csv_hint": "EQUITY_INCOME_WAVE.csv",
        "wave_type": "Income Wave",
    },
    "future_power": {
        "label": "Future Power & Energy Wave",
        "benchmark": "Clean Energy / Infrastructure",
        "csv_hint": "FUTURE_POWER_WAVE.csv",
        "wave_type": "Thematic Wave",
    },
    "tech_leaders": {
        "label": "Tech Leaders Wave",
        "benchmark": "NASDAQ 100",
        "csv_hint": "TECH_LEADERS_WAVE.csv",
        "wave_type": "AI-Managed Wave",
    },
    "ai_wave": {
        "label": "AI & Automation Wave",
        "benchmark": "AI / Robotics Composite",
        "csv_hint": "AI_WAVE.csv",
        "wave_type": "Thematic Wave",
    },
    "quality_core": {
        "label": "Quality Core Wave",
        "benchmark": "Global Quality Composite",
        "csv_hint": "QUALITY_CORE_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "diversified_us": {
        "label": "US Core Equity Wave",
        "benchmark": "Total US Market",
        "csv_hint": "US_CORE_EQUITY_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "intl_developed": {
        "label": "International Developed Wave",
        "benchmark": "MSCI EAFE",
        "csv_hint": "INTL_DEV_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "emerging": {
        "label": "Emerging Markets Wave",
        "benchmark": "MSCI EM",
        "csv_hint": "EM_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "dividend_growth": {
        "label": "Dividend Growth Wave",
        "benchmark": "US Dividend Growth Index",
        "csv_hint": "DIVIDEND_GROWTH_WAVE.csv",
        "wave_type": "Income Wave",
    },
    "sector_rotation": {
        "label": "Sector Rotation Wave",
        "benchmark": "Sector-Neutral Composite",
        "csv_hint": "SECTOR_ROTATION_WAVE.csv",
        "wave_type": "Tactical Wave",
    },
}

# ---------------------------------------------------------
# Sidebar: control panel (Step 1 – no SmartSafe, no toggles)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<div style='font-size:1.1rem;font-weight:600;margin-bottom:0.25rem;'>"
        "🌊 WAVES Intelligence™</div>",
        unsafe_allow_html=True,
    )
    st.caption("Institutional Wave Console (alpha demo)")

    # Wave selector
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
        f"Suggested export: `{wave_cfg['csv_hint']}`",
        unsafe_allow_html=True,
    )

    portfolio_file = st.file_uploader(
        "Upload Wave CSV",
        type=["csv"],
        label_visibility="collapsed",
        key="wave_csv",
    )

# ---------------------------------------------------------
# Main header
# ---------------------------------------------------------
st.markdown(
    "<h1 style='margin-bottom:0.1rem;'>WAVES INTELLIGENCE™</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<span style='color:{TEXT_MUTED};font-size:0.9rem;'>"
    f"{wave_cfg['label']} — Institutional Portfolio Console</span>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<span style='color:{ACCENT_SOFT};font-size:0.8rem;font-weight:500;'>"
    f"AI-Managed Wave • Real-time demo • CSV-driven • No external data calls</span>",
    unsafe_allow_html=True,
)
st.markdown("")

# ---------------------------------------------------------
# If no portfolio file yet, show instructions and stop
# ---------------------------------------------------------
if portfolio_file is None:
    st.info(
        "Upload the latest Wave snapshot CSV in the sidebar to render the console. "
        "Use your Google Sheets export for the selected Wave."
    )
    st.stop()

# ---------------------------------------------------------
# Load & normalize data (no charts yet – just metrics & preview)
# ---------------------------------------------------------
try:
    raw_df = pd.read_csv(portfolio_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Normalize column names
raw_df.columns = [c.strip().replace(" ", "_") for c in raw_df.columns]
lower_cols = {c.lower(): c for c in raw_df.columns}


def pick(*candidates):
    """Pick the first matching column name from candidates (case-insensitive)."""
    for cand in candidates:
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
    return None


ticker_col = pick("Ticker")
price_col = pick("Price", "Last")
dollar_col = pick("Dollar_Alloc", "DollarAlloc", "Dollar_Value")
weight_col = pick("Weight_pct", "Weight", "Weight_%", "WeightPct")

missing_core = [name for name, col in
                [("Ticker", ticker_col), ("Price", price_col), ("Dollar_Alloc", dollar_col)]
                if col is None]

if missing_core:
    st.error(
        "CSV is missing required columns: "
        + ", ".join(missing_core)
        + ". Required: Ticker, Price, Dollar_Alloc.",
    )
    st.stop()

df = raw_df.rename(
    columns={
        ticker_col: "Ticker",
        price_col: "Price",
        dollar_col: "Dollar_Alloc",
        **({weight_col: "Weight_pct"} if weight_col else {}),
    }
)

# Ensure numeric
for col in ["Price", "Dollar_Alloc", "Weight_pct"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# De-duplicate tickers and recompute weights
group_cols = ["Ticker"]
agg_dict = {"Price": "last", "Dollar_Alloc": "sum"}
df = df.groupby(group_cols, as_index=False).agg(agg_dict)

total_nav = df["Dollar_Alloc"].sum()
if total_nav <= 0:
    st.error("Total NAV from Dollar_Alloc is non-positive. Check your CSV.")
    st.stop()

df["Weight_pct"] = df["Dollar_Alloc"] / total_nav * 100.0

num_holdings = df["Ticker"].nunique()
largest_position = df["Weight_pct"].max()
top10_conc = df.nlargest(10, "Weight_pct")["Weight_pct"].sum()

# ---------------------------------------------------------
# Metric row (Step 1)
# ---------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='metric-label'>TOTAL NAV</div>"
        f"<div class='metric-value'>${total_nav:,.0f}</div>"
        f"<div class='metric-sub'>Snapshot from uploaded CSV</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='metric-label'># OF HOLDINGS</div>"
        f"<div class='metric-value'>{num_holdings:,}</div>"
        f"<div class='metric-sub'>Unique securities in this Wave</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='metric-label'>LARGEST POSITION</div>"
        f"<div class='metric-value'>{largest_position:0.2f}%</div>"
        f"<div class='metric-sub'>Single-name weight</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='metric-label'>TOP 10 CONCENTRATION</div>"
        f"<div class='metric-value'>{top10_conc:0.2f}%</div>"
        f"<div class='metric-sub'>Sum of top 10 weights</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("")

# ---------------------------------------------------------
# Simple holdings preview (Step 1 – no charts yet)
# ---------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Holdings preview</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-caption'>Top 25 holdings by dollar allocation.</div>",
    unsafe_allow_html=True,
)

preview = df.sort_values("Dollar_Alloc", ascending=False).head(25).copy()
preview_display = preview[["Ticker", "Price", "Dollar_Alloc", "Weight_pct"]].copy()
preview_display["Price"] = preview_display["Price"].round(2)
preview_display["Dollar_Alloc"] = preview_display["Dollar_Alloc"].round(0)
preview_display["Weight_pct"] = preview_display["Weight_pct"].round(3)

st.dataframe(
    preview_display.rename(
        columns={"Dollar_Alloc": "Dollar_Alloc($)", "Weight_pct": "Weight_%"}
    ),
    use_container_width=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "Upload-based demo • Data source: Wave CSV exports • "
    "WAVES Intelligence™ • Internal demo only (not investment advice)."
)