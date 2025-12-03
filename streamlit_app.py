import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# -------------------------------------------------------------
# PAGE CONFIG & BRANDING
# -------------------------------------------------------------
st.set_page_config(
    page_title="WAVES Intelligence™ – S&P 500 Wave Console",
    page_icon="🌊",
    layout="wide",
)

# Custom CSS for WAVES branding
st.markdown(
    """
    <style>
    /* Global tweaks */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1350px;
    }
    /* Header */
    .waves-header {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: 0.15em;
        color: #00F7A7;
        text-transform: uppercase;
    }
    .waves-subheader {
        font-size: 16px;
        color: #d0d0d0;
        margin-top: 2px;
    }
    .waves-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        background: rgba(0, 247, 167, 0.10);
        color: #00F7A7;
        border: 1px solid rgba(0, 247, 167, 0.5);
        margin-left: 10px;
    }
    .franklin-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        background: rgba(0, 120, 200, 0.12);
        color: #6bb4ff;
        border: 1px solid rgba(107, 180, 255, 0.6);
        margin-left: 8px;
    }
    /* Metric cards */
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #aaaaaa;
        margin-bottom: 2px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #f5f5f5;
    }
    /* Section titles */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 4px;
    }
    .section-caption {
        font-size: 11px;
        color: #b0b0b0;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# SIDEBAR – WAVE SWITCHER & OPTIONS
# -------------------------------------------------------------
st.sidebar.markdown("### 🌊 WAVES Intelligence™")

wave_choice = st.sidebar.selectbox(
    "Select Wave",
    [
        "S&P 500 Wave (LIVE Demo)",
        "Global Universe (Coming Soon)",
        "Income Wave (Coming Soon)",
        "Crypto Wave (Coming Soon)",
    ],
    index=0,
)

franklin_mode = st.sidebar.toggle("Franklin Edition mode", value=False)

st.sidebar.markdown("---")
smart_safe_level = st.sidebar.slider(
    "SmartSafe™ allocation (%)",
    min_value=0,
    max_value=40,
    value=10,
    step=5,
    help="Hypothetical cash buffer allocated to SmartSafe™ inside this Wave.",
)

st.sidebar.markdown(
    """
    **Tip:** Use different SmartSafe™ levels live in the meeting  
    to show how WAVES can de-risk without touching the core engine.
    """
)

# If not S&P 500 Wave, just show a coming soon panel for now
if wave_choice != "S&P 500 Wave (LIVE Demo)":
    st.markdown(
        f"""
        <div class="waves-header">WAVES INTELLIGENCE™</div>
        <div class="waves-subheader">{wave_choice}</div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "This Wave will plug into the same console layout.\n\n"
        "For Friday, run the live demo using the **S&P 500 Wave (LIVE Demo)** option in the sidebar."
    )
    st.stop()

# -------------------------------------------------------------
# HEADER
# -------------------------------------------------------------
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown(
        """
        <div class="waves-header">WAVES INTELLIGENCE™</div>
        <div class="waves-subheader">
            S&P 500 Wave – Institutional Portfolio Console
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<span class="waves-badge">AI-MANAGED WAVE</span>',
        unsafe_allow_html=True,
    )
    if franklin_mode:
        st.markdown(
            '<span class="franklin-badge">Franklin Templeton – Private Demo</span>',
            unsafe_allow_html=True,
        )

with header_col2:
    st.caption("Session")
    st.write("• Real-time demo\n• CSV-driven\n• No external data calls")

st.markdown("---")

# -------------------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload **SP500_PORTFOLIO_FINAL.csv** snapshot",
    type="csv",
    help="Export your latest S&P 500 Wave snapshot from Google Sheets, then upload it here.",
)

if uploaded_file is None:
    st.info("👆 Upload your **SP500_PORTFOLIO_FINAL.csv** to see the full dashboard.")
    st.stop()

# -------------------------------------------------------------
# LOAD & NORMALIZE DATA
# -------------------------------------------------------------
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: `{e}`")
    st.stop()

# Strip column names and standardize
df.columns = [c.strip() for c in df.columns]

# Try to detect columns
ticker_col = "Ticker"
price_col = "Price"
dollar_col_candidates = ["Dollar_Alloc", "DollarAlloc", "Dollar_Allocation"]
weight_col_candidates = ["Weight_pct", "Weight", "WeightPercent"]
index_weight_candidates = ["Index_Weight", "IndexWeight", "Index_Wt"]

dollar_col = next((c for c in dollar_col_candidates if c in df.columns), None)
weight_col = next((c for c in weight_col_candidates if c in df.columns), None)
index_weight_col = next((c for c in index_weight_candidates if c in df.columns), None)

if ticker_col not in df.columns or price_col not in df.columns or dollar_col is None:
    st.error(
        "CSV is missing required columns. Need at least: "
        "`Ticker`, `Price`, and a dollar allocation column like `Dollar_Alloc`."
    )
    st.stop()

# Compute / normalize weights
total_nav = float(df[dollar_col].sum())

if weight_col is None:
    df["Weight_pct"] = df[dollar_col] / total_nav * 100.0
    weight_col = "Weight_pct"
else:
    # Convert to numeric and normalize into percent if needed
    df[weight_col] = pd.to_numeric(df[weight_col], errors="coerce")
    if df[weight_col].max() <= 1.0:
        df[weight_col] = df[weight_col] * 100.0

# Normalize index weights if present
if index_weight_col:
    df[index_weight_col] = pd.to_numeric(df[index_weight_col], errors="coerce")
    if df[index_weight_col].max() <= 1.0:
        df[index_weight_col] = df[index_weight_col] * 100.0

# Basic derived fields
df = df.sort_values(weight_col, ascending=False).reset_index(drop=True)
n_holdings = df.shape[0]
largest_pos = df[weight_col].max()
top10_conc = df.head(10)[weight_col].sum()

# Allocation alpha (vs index) if we have index weights
if index_weight_col:
    df["Alpha_pct"] = df[weight_col] - df[index_weight_col]
else:
    df["Alpha_pct"] = np.nan

# -------------------------------------------------------------
# TOP METRICS ROW
# -------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown('<div class="metric-label">Total NAV</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-value">${total_nav:,.0f}</div>',
        unsafe_allow_html=True,
    )

with m2:
    st.markdown('<div class="metric-label"># of Holdings</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-value">{n_holdings:,}</div>',
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        '<div class="metric-label">Largest Position</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="metric-value">{largest_pos:.2f}%</div>',
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        '<div class="metric-label">Top 10 Concentration</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="metric-value">{top10_conc:.2f}%</div>',
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------
# MAIN GRID LAYOUT (ONE SCREEN)
# -------------------------------------------------------------
# Left: Top holdings + SmartSafe summary
# Center: Alpha vs Index + Top 10 by Weight
# Right: Full Allocation + Alpha Heatmap + Largest Positions
st.markdown("")
upper_left, upper_mid, upper_right = st.columns([1.1, 1.1, 1.2])

# ---------- Upper Left: Top holdings + SmartSafe ----------
with upper_left:
    st.markdown('<div class="section-title">Top Holdings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Sorted by weight in the S&P 500 Wave.</div>',
        unsafe_allow_html=True,
    )
    rows = st.slider(
        "Rows",
        min_value=5,
        max_value=min(50, n_holdings),
        value=20,
        key="top_rows_slider",
        label_visibility="collapsed",
    )
    top_holdings = df[[ticker_col, price_col, dollar_col, weight_col]].head(rows)
    st.dataframe(
        top_holdings.rename(
            columns={
                ticker_col: "Ticker",
                price_col: "Price",
                dollar_col: "Dollar_Alloc",
                weight_col: "Weight_%",
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=360,
    )

    # SmartSafe summary
    st.markdown('<div class="section-title">SmartSafe™ Scenario</div>', unsafe_allow_html=True)
    safe_cash = total_nav * smart_safe_level / 100.0
    invested_nav = total_nav - safe_cash
    col_safe1, col_safe2 = st.columns(2)
    with col_safe1:
        st.caption("Cash Buffer (SmartSafe™)")
        st.write(f"`${safe_cash:,.0f}`")
    with col_safe2:
        st.caption("Invested in Wave")
        st.write(f"`${invested_nav:,.0f}`")

    st.caption(
        "SmartSafe™ lets you de-risk at the Wave level without touching the underlying logic. "
        "You can talk through different levels live."
    )

# ---------- Upper Middle: Alpha vs Index + Top 10 ----------
with upper_mid:
    st.markdown(
        '<div class="section-title">Allocation Alpha vs S&P 500 Index</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-caption">Positive bars = overweight vs index. Negative bars = underweight.</div>',
        unsafe_allow_html=True,
    )

    top_alpha = df.head(10)[[ticker_col, "Alpha_pct", weight_col]].copy()

    if index_weight_col and not top_alpha["Alpha_pct"].isna().all():
        alpha_chart = (
            alt.Chart(top_alpha)
            .mark_bar()
            .encode(
                x=alt.X(ticker_col, sort=None, title="Ticker"),
                y=alt.Y("Alpha_pct", title="Active weight vs index (pct)"),
                color=alt.condition(
                    alt.datum.Alpha_pct >= 0,
                    alt.value("#00F7A7"),
                    alt.value("#FF6B6B"),
                ),
                tooltip=[
                    alt.Tooltip(ticker_col, title="Ticker"),
                    alt.Tooltip("Alpha_pct", format=".2f", title="Active weight (%)"),
                ],
            )
            .properties(height=230)
        )
        st.altair_chart(alpha_chart, use_container_width=True)
    else:
        st.info(
            "Index weights not found in the CSV – alpha vs S&P 500 chart will appear once "
            "an index weight column (e.g. `Index_Weight`) is included."
        )

    st.markdown(
        '<div class="section-title" style="margin-top:12px;">Top 10 by Weight</div>',
        unsafe_allow_html=True,
    )
    top10 = df.head(10)[[ticker_col, weight_col]].copy()
    top10_chart = (
        alt.Chart(top10)
        .mark_bar()
        .encode(
            x=alt.X(ticker_col, sort=None, title=""),
            y=alt.Y(weight_col, title="Weight (%)"),
            tooltip=[
                alt.Tooltip(ticker_col, title="Ticker"),
                alt.Tooltip(weight_col, format=".2f", title="Weight (%)"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(top10_chart, use_container_width=True)

# ---------- Upper Right: Full allocation + Alpha heat strip + largest table ----------
with upper_right:
    st.markdown(
        '<div class="section-title">Full Wave Allocation</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-caption">Each bar is a holding’s % weight in the S&P 500 Wave.</div>',
        unsafe_allow_html=True,
    )

    # To avoid tiny ticks for 500 names, show top 150 by weight
    max_names = min(150, n_holdings)
    full_alloc = df.head(max_names)[[ticker_col, weight_col]].copy()
    full_alloc_chart = (
        alt.Chart(full_alloc)
        .mark_bar()
        .encode(
            x=alt.X(ticker_col, sort=None, title=""),
            y=alt.Y(weight_col, title="Weight (%)"),
            tooltip=[
                alt.Tooltip(ticker_col, title="Ticker"),
                alt.Tooltip(weight_col, format=".2f", title="Weight (%)"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(full_alloc_chart, use_container_width=True)

    # Alpha heat strip
    if index_weight_col and not df["Alpha_pct"].isna().all():
        st.markdown(
            '<div class="section-title" style="margin-top:10px;">Alpha Heatmap (Top 50)</div>',
            unsafe_allow_html=True,
        )
        alpha_strip = (
            alt.Chart(df.head(50))
            .mark_rect()
            .encode(
                x=alt.X(ticker_col, sort=None, title=""),
                y=alt.value(0),  # single strip
                color=alt.Color(
                    "Alpha_pct",
                    title="Active weight (%)",
                    scale=alt.Scale(scheme="redblue", reverse=True),
                ),
                tooltip=[
                    alt.Tooltip(ticker_col, title="Ticker"),
                    alt.Tooltip("Alpha_pct", format=".2f", title="Active weight (%)"),
                ],
            )
            .properties(height=60)
        )
        st.altair_chart(alpha_strip, use_container_width=True)

    # Largest Positions table
    st.markdown(
        '<div class="section-title" style="margin-top:10px;">Largest Positions (Table)</div>',
        unsafe_allow_html=True,
    )
    largest_tbl = df.head(10)[[ticker_col, weight_col]].copy()
    largest_tbl = largest_tbl.rename(
        columns={ticker_col: "Ticker", weight_col: "Weight_%"}
    )
    st.dataframe(
        largest_tbl,
        use_container_width=True,
        hide_index=True,
        height=190,
    )

# -------------------------------------------------------------
# WEIGHT BUCKETS + EXPORTS (BOTTOM BAR)
# -------------------------------------------------------------
st.markdown("---")
bottom_left, bottom_mid, bottom_right = st.columns([1.0, 1.0, 1.1])

with bottom_left:
    st.markdown('<div class="section-title">Weight Buckets</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Core vs Satellite vs Micro positions.</div>',
        unsafe_allow_html=True,
    )
    core = df[df[weight_col] >= 2.0][weight_col].sum()
    satellite = df[(df[weight_col] >= 0.5) & (df[weight_col] < 2.0)][weight_col].sum()
    micro = df[df[weight_col] < 0.5][weight_col].sum()
    bucket_df = pd.DataFrame(
        {
            "Bucket": ["Core (≥ 2%)", "Satellite (0.5–2%)", "Micro (< 0.5%)"],
            "Weight_%": [core, satellite, micro],
        }
    )
    bucket_chart = (
        alt.Chart(bucket_df)
        .mark_bar()
        .encode(
            x=alt.X("Bucket", sort=None, title=""),
            y=alt.Y("Weight_%", title="Share of Wave (%)"),
            tooltip=[
                alt.Tooltip("Bucket", title="Bucket"),
                alt.Tooltip("Weight_%", format=".2f", title="Weight (%)"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(bucket_chart, use_container_width=True)

with bottom_mid:
    st.markdown('<div class="section-title">Data Exports</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Instant CSV exports for diligence or follow-up.</div>',
        unsafe_allow_html=True,
    )
    export_top = top_holdings.rename(
        columns={
            ticker_col: "Ticker",
            price_col: "Price",
            dollar_col: "Dollar_Alloc",
            weight_col: "Weight_%",
        }
    )
    export_all = df.rename(
        columns={ticker_col: "Ticker", dollar_col: "Dollar_Alloc", weight_col: "Weight_%"}
    )

    st.download_button(
        "⬇️ Download Top Holdings (CSV)",
        data=export_top.to_csv(index=False).encode("utf-8"),
        file_name="waves_sp500_top_holdings.csv",
        mime="text/csv",
    )

    st.download_button(
        "⬇️ Download Full Wave Holdings (CSV)",
        data=export_all.to_csv(index=False).encode("utf-8"),
        file_name="waves_sp500_full_holdings.csv",
        mime="text/csv",
    )

    st.caption(
        "For the meeting: export top holdings and email them directly from the console if asked."
    )

with bottom_right:
    st.markdown('<div class="section-title">Notes & Disclaimers</div>', unsafe_allow_html=True)
    st.markdown(
        """
        - Upload-based view • Data source: **SP500_PORTFOLIO_FINAL.csv**  
        - Metrics and charts are for **internal demonstration only**.  
        - WAVES Intelligence™ is an **AI-managed Wave engine**, not a mutual fund or ETF.  
        - Performance and analytics are **hypothetical** unless explicitly labeled as live.
        """.strip()
    )
