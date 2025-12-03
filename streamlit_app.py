import streamlit as st
import pandas as pd
import numpy as np

# ============== BRAND COLORS & GLOBAL STYLES ============== #
BRAND_BG = "#050516"
PANEL_BG = "#0B0F1A"
PRIMARY = "#00FFA7"   # WAVES neon green
ACCENT = "#4DE2FA"    # soft teal/blue accent
TEXT_MAIN = "#F5F7FF"
TEXT_MUTED = "#A0AEC0"

st.set_page_config(
    page_title="WAVES Intelligence™ — S&P 500 Wave Alpha Console",
    layout="wide"
)

# Inject custom CSS for branding
st.markdown(
    f"""
    <style>
    /* App background */
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at top left, #101628 0, {BRAND_BG} 55%);
    }}
    [data-testid="stHeader"] {{
        background: transparent;
    }}
    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
        max-width: 1400px;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT_MAIN};
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "SF Pro Display", sans-serif;
    }}
    p, span, div {{
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}

    /* Metric strip */
    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, rgba(0,0,0,0.35), rgba(255,255,255,0.02));
        padding: 14px 18px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.06);
    }}
    [data-testid="stMetric"] label {{
        color: {TEXT_MUTED};
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    [data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {TEXT_MAIN};
        font-size: 1.2rem;
        font-weight: 600;
    }}

    /* Cards (dataframes & charts containers) */
    .stDataFrame, .stPlotlyChart, .plot-container, .stAltairChart {{
        border-radius: 14px !important;
    }}

    /* Slider label color */
    .stSlider > div > div > div > label {{
        color: {TEXT_MUTED};
    }}

    /* Section headings */
    .section-title {{
        font-size: 1.0rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {TEXT_MUTED};
        margin-bottom: 0.25rem;
    }}
    .section-subtitle {{
        font-size: 0.8rem;
        color: {TEXT_MUTED};
        margin-bottom: 0.75rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============== HEADER ============== #
st.markdown(
    f"""
    <div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:0.75rem;">
        <div>
            <div style="font-size:0.8rem;letter-spacing:0.22em;text-transform:uppercase;color:{TEXT_MUTED};">
                POWERED BY WAVES INTELLIGENCE™
            </div>
            <div style="font-size:1.8rem;font-weight:650;color:{TEXT_MAIN};margin-top:4px;">
                S&amp;P 500 Wave &mdash; Alpha Console
            </div>
        </div>
        <div style="text-align:right;font-size:0.8rem;color:{TEXT_MUTED};">
            <span style="color:{PRIMARY};font-weight:500;">Live allocation view</span><br/>
            Upload latest SP500_PORTFOLIO_FINAL snapshot
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ============== FILE UPLOAD ============== #
uploaded_file = st.file_uploader(
    "Upload SP500_PORTFOLIO_FINAL.csv",
    type="csv",
    help="Export the latest S&P 500 Wave snapshot from Google Sheets as CSV, then upload it here."
)

if uploaded_file is None:
    st.info("👆 Upload your **SP500_PORTFOLIO_FINAL.csv** to see the WAVES Alpha console.")
    st.stop()

# ============== LOAD DATA ============== #
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Normalize column names (strip spaces)
df.columns = [c.strip() for c in df.columns]

# Required base columns
required_cols = ["Ticker"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing required column(s) in CSV: {', '.join(missing)}")
    st.stop()

# Ensure Dollar_Alloc exists (compute if necessary)
if "Dollar_Alloc" not in df.columns:
    if {"Price", "Shares"}.issubset(df.columns):
        df["Dollar_Alloc"] = df["Price"] * df["Shares"]
    else:
        st.error("CSV must contain either 'Dollar_Alloc' or both 'Price' and 'Shares'.")
        st.stop()

# Fill missing numeric values with 0 for safety
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

# ============== CORE METRICS ============== #
total_nav = float(df["Dollar_Alloc"].sum())
if total_nav <= 0:
    st.error("Total NAV is 0 or negative. Check 'Dollar_Alloc' values in your CSV.")
    st.stop()

# Recompute portfolio weights from Dollar_Alloc
df["Weight_pct"] = df["Dollar_Alloc"] / total_nav * 100.0

# # of holdings with non-trivial allocation
num_holdings = int((df["Dollar_Alloc"] > 0).sum())

# Largest position weight
largest_weight = float(df["Weight_pct"].max())

# Top 10 concentration
top10_conc = float(df["Weight_pct"].nlargest(10).sum())

# ============== INDEX VS WAVE ("ALPHA") ============== #
if "Index_Weight" in df.columns:
    idx_raw = df["Index_Weight"].copy()

    # If the index weights look like decimals (<1), treat as 0.xx and convert to %
    if idx_raw.dropna().max() < 1.0:
        df["Index_Weight_pct"] = idx_raw * 100.0
    else:
        df["Index_Weight_pct"] = idx_raw

    df["Active_Weight_pct"] = df["Weight_pct"] - df["Index_Weight_pct"]
    has_alpha = True
else:
    df["Index_Weight_pct"] = np.nan
    df["Active_Weight_pct"] = np.nan
    has_alpha = False

# Sort by portfolio weight for all downstream displays
df = df.sort_values("Weight_pct", ascending=False).reset_index(drop=True)

# ============== TOP KPI STRIP ============== #
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total NAV", f"${total_nav:,.0f}")

with kpi2:
    st.metric("# of Holdings", f"{num_holdings:,}")

with kpi3:
    st.metric("Largest Position", f"{largest_weight:.2f}%")

with kpi4:
    st.metric("Top 10 Concentration", f"{top10_conc:.2f}%")

st.markdown("")

# ============== 3-COLUMN MAIN LAYOUT ============== #
left, mid, right = st.columns([1.4, 1.4, 1.8])

# ---------- LEFT: TOP HOLDINGS TABLE ---------- #
with left:
    st.markdown(f"<div class='section-title'>Top Holdings</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='section-subtitle'>Sorted by Wave weight; slider controls rows shown.</div>",
        unsafe_allow_html=True,
    )

    max_rows = min(50, len(df))
    rows = st.slider("Rows", min_value=5, max_value=max_rows, value=min(20, max_rows), step=1)

    show_cols = ["Ticker"]
    if "Price" in df.columns:
        show_cols.append("Price")
    show_cols.append("Dollar_Alloc")
    show_cols.append("Weight_pct")

    top_table = df.head(rows)[show_cols].copy()
    if "Price" in top_table.columns:
        top_table["Price"] = top_table["Price"].map(lambda x: f"${x:,.2f}")
    top_table["Dollar_Alloc"] = top_table["Dollar_Alloc"].map(lambda x: f"${x:,.0f}")
    top_table["Weight_pct"] = top_table["Weight_pct"].map(lambda x: f"{x:.2f}%")

    st.dataframe(
        top_table,
        use_container_width=True,
        hide_index=True,
        height=430,
    )

# ---------- MIDDLE: ALPHA + TOP 10 + BUCKETS ---------- #
with mid:
    # Allocation Alpha first
    st.markdown(
        "<div class='section-title'>Allocation Alpha vs S&amp;P 500 Index</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-subtitle'>Positive bars = overweight vs index. Negative bars = underweight.</div>",
        unsafe_allow_html=True,
    )

    if has_alpha and df["Active_Weight_pct"].abs().sum() > 0:
        alpha_df = (
            df[["Ticker", "Active_Weight_pct"]]
            .sort_values("Active_Weight_pct", key=lambda s: s.abs(), ascending=False)
            .head(15)
            .set_index("Ticker")
        )
        st.bar_chart(alpha_df, use_container_width=True, height=260)
    else:
        st.info("Index_Weight column not found in CSV, so allocation alpha cannot be computed.")

    st.markdown(
        "<div class='section-title' style='margin-top:0.75rem;'>Top 10 by Wave Weight</div>",
        unsafe_allow_html=True,
    )

    top10 = df.head(10)[["Ticker", "Weight_pct"]].set_index("Ticker")
    st.bar_chart(top10, use_container_width=True, height=240)

    st.markdown(
        "<div class='section-title' style='margin-top:0.75rem;'>Weight Buckets</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-subtitle'>Core ≥ 2%, Satellites 0.5–2%, Micro &lt; 0.5% by Wave weight.</div>",
        unsafe_allow_html=True,
    )

    core = df[df["Weight_pct"] >= 2.0]["Weight_pct"].sum()
    satellite = df[(df["Weight_pct"] >= 0.5) & (df["Weight_pct"] < 2.0)]["Weight_pct"].sum()
    micro = df[df["Weight_pct"] < 0.5]["Weight_pct"].sum()

    bucket_df = pd.DataFrame(
        {
            "Bucket": ["Core (≥ 2%)", "Satellite (0.5–2%)", "Micro (< 0.5%)"],
            "Weight_pct": [core, satellite, micro],
        }
    ).set_index("Bucket")

    st.bar_chart(bucket_df, use_container_width=True, height=220)

# ---------- RIGHT: FULL ALLOCATION + LARGEST POSITIONS ---------- #
with right:
    st.markdown("<div class='section-title'>Full Wave Allocation</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-subtitle'>Each bar is a holding’s % weight in the S&amp;P 500 Wave (top 150 shown).</div>",
        unsafe_allow_html=True,
    )

    max_full = min(150, len(df))
    full_df = df.head(max_full)[["Ticker", "Weight_pct"]].set_index("Ticker")
    st.bar_chart(full_df, use_container_width=True, height=280)

    st.markdown(
        "<div class='section-title' style='margin-top:0.75rem;'>Largest Positions (Table)</div>",
        unsafe_allow_html=True,
    )

    largest_df = df.head(15)[["Ticker", "Weight_pct"]].copy()
    largest_df["Weight_pct"] = largest_df["Weight_pct"].map(lambda x: f"{x:.2f}%")
    st.dataframe(
        largest_df.set_index("Ticker"),
        use_container_width=True,
        height=260,
    )

# ============== FOOTER / DISCLAIMER ============== #
st.markdown("---")
st.caption(
    """
    • Data source: **SP500_PORTFOLIO_FINAL.csv** (Google Sheets export).  
    • All weights are recomputed from *Dollar_Alloc* at upload time.  
    • “Allocation Alpha” = Wave portfolio weight minus S&P 500 index weight (Index_Weight).  
    • WAVES Intelligence™ — Internal demo console only (not investment advice).
    """
)
