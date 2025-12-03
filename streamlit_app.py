import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ------------------------------------------------------
# Page + global config
# ------------------------------------------------------

st.set_page_config(
    page_title="WAVES Intelligence™ – Institutional Wave Console",
    layout="wide",
)

# Wave metadata (you can edit names / benchmarks here)
WAVE_CONFIG = {
    "S&P 500 Wave (LIVE Demo)": {
        "subtitle": "S&P 500 Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "S&P 500 Index",
        "live": True,
    },
    "Global Universe Wave (Coming Soon)": {
        "subtitle": "Global Universe Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "Global Equity Index",
        "live": False,
    },
    "Income Wave (Coming Soon)": {
        "subtitle": "Income Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "US Dividend / Income Benchmark",
        "live": False,
    },
    "Small Cap Growth Wave (Coming Soon)": {
        "subtitle": "Small Cap Growth Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "US Small Cap Growth Index",
        "live": False,
    },
    "Sm/Mid Growth Wave (Coming Soon)": {
        "subtitle": "Small–Mid Growth Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "US SMID Growth Index",
        "live": False,
    },
    "Future Power & Energy Wave (Coming Soon)": {
        "subtitle": "Future Power & Energy Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "Future Energy / Power Benchmark",
        "live": False,
    },
    "Equity Income Wave (Coming Soon)": {
        "subtitle": "Equity Income Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "Equity Income Index",
        "live": False,
    },
    "RWA Income Wave (Coming Soon)": {
        "subtitle": "RWA Income Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "RWA / Credit Benchmark",
        "live": False,
    },
    "Crypto Income Wave (Coming Soon)": {
        "subtitle": "Crypto Income Wave — Institutional Portfolio Console",
        "badge": "AI-Managed Wave",
        "benchmark": "Crypto Benchmark",
        "live": False,
    },
}

# ------------------------------------------------------
# Sidebar – Wave selector + SmartSafe™
# ------------------------------------------------------

st.sidebar.markdown("### 🌊 WAVES Intelligence™")
st.sidebar.markdown("Institutional Wave Console (alpha demo)")

wave_name = st.sidebar.selectbox(
    "Select Wave",
    list(WAVE_CONFIG.keys()),
    index=0,
)

smart_safe = st.sidebar.radio(
    "SmartSafe™ level (for meeting demos)",
    ["Standard", "Defensive", "Max Safety"],
    index=0,
)

st.sidebar.markdown(
    """
Tip: Use different SmartSafe™ levels in the meeting  
to show how WAVES can **de-risk** without touching  
the core engine.
"""
)

wave_cfg = WAVE_CONFIG[wave_name]

# ------------------------------------------------------
# Header / Branding
# ------------------------------------------------------

st.markdown(
    """
    <h1 style="color:#00FFA7;margin-bottom:0;">WAVES INTELLIGENCE™</h1>
    """,
    unsafe_allow_html=True,
)

st.markdown(f"### {wave_cfg['subtitle']}")

badges_html = f"""
<div style="margin-top:4px;margin-bottom:20px;">
    <span style="
        background-color:#111827;
        color:#22C55E;
        padding:4px 10px;
        border-radius:999px;
        font-size:11px;
        margin-right:4px;
    ">{wave_cfg['badge']}</span>
    <span style="
        background-color:#0F172A;
        color:#9CA3AF;
        padding:4px 10px;
        border-radius:999px;
        font-size:11px;
        margin-right:4px;
    ">Real-time demo • CSV-driven • No external data calls</span>
    <span style="
        background-color:#020617;
        color:#FACC15;
        padding:4px 10px;
        border-radius:999px;
        font-size:11px;
    ">Benchmark: {wave_cfg['benchmark']}</span>
</div>
"""
st.markdown(badges_html, unsafe_allow_html=True)

# SmartSafe display hint
st.markdown(
    f"**SmartSafe™ Scenario:** `{smart_safe}` — adjust this live to narrate "
    "how WAVES can dial risk down without touching the core portfolio engine."
)

st.markdown("---")

# ------------------------------------------------------
# File upload
# ------------------------------------------------------

st.markdown("#### Upload latest Wave snapshot (`.csv`)")

uploaded_file = st.file_uploader(
    "Upload your SP500_PORTFOLIO_FINAL.csv (or equivalent for this Wave)",
    type=["csv"],
)

if uploaded_file is None:
    st.info(
        "👆 Upload a CSV to see the full dashboard. "
        "Required columns: `Ticker`, `Price`, `Dollar_Alloc`, `Index_Weight`. "
        "`Weight_pct` is optional – the app will calculate it if missing."
    )
    st.stop()

# ------------------------------------------------------
# Data loading + validation
# ------------------------------------------------------

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Normalize column names (strip spaces)
df.columns = [str(c).strip() for c in df.columns]

required_cols = ["Ticker", "Price", "Dollar_Alloc", "Index_Weight"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(
        "Missing required columns in CSV: "
        + ", ".join(missing)
        + "<br>Expected at least: "
        + ", ".join(required_cols + ["Weight_pct (optional)"]),
        icon="⚠️",
    )
    st.stop()

# If Weight_pct is not present, derive it from Dollar_Alloc
if "Weight_pct" not in df.columns:
    total_alloc = df["Dollar_Alloc"].replace({0: np.nan}).sum()
    if total_alloc == 0 or pd.isna(total_alloc):
        st.error(
            "Unable to derive `Weight_pct` because total `Dollar_Alloc` is 0. "
            "Please check the uploaded file."
        )
        st.stop()
    df["Weight_pct"] = df["Dollar_Alloc"] / total_alloc * 100.0

# Clean up types
for col in ["Price", "Dollar_Alloc", "Weight_pct", "Index_Weight"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Ticker", "Dollar_Alloc", "Weight_pct", "Index_Weight"])

# Add alpha column (portfolio weight minus benchmark weight)
df["Alpha_pct"] = df["Weight_pct"] - df["Index_Weight"]

# Sort by portfolio weight for various views
df_sorted = df.sort_values("Weight_pct", ascending=False).reset_index(drop=True)

# ------------------------------------------------------
# High-level metrics
# ------------------------------------------------------

total_nav = float(df["Dollar_Alloc"].sum())
num_holdings = int(df["Ticker"].nunique())
largest_pos = float(df["Weight_pct"].max())
top10_conc = float(df_sorted.head(10)["Dollar_Alloc"].sum() / total_nav * 100.0)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total NAV", f"${total_nav:,.0f}")
m2.metric("# of Holdings", f"{num_holdings}")
m3.metric("Largest Position", f"{largest_pos:.2f}%")
m4.metric("Top 10 Concentration", f"{top10_conc:.2f}%")

st.markdown("---")

# ------------------------------------------------------
# Layout: top holdings + charts
# ------------------------------------------------------

# Top holdings table (left)
left_col, mid_col, right_col = st.columns([1.2, 1.0, 1.2])

with left_col:
    st.markdown("#### Top Holdings")
    rows = st.slider("Rows", min_value=5, max_value=50, value=20, step=1)
    show_cols = ["Ticker", "Price", "Dollar_Alloc", "Weight_pct"]
    st.dataframe(
        df_sorted.head(rows)[show_cols],
        use_container_width=True,
        hide_index=True,
        height=420,
    )

# Allocation Alpha vs Index (middle)
with mid_col:
    st.markdown("#### Allocation Alpha vs Index")
    st.caption("Positive bars = overweight vs index. Negative bars = underweight.")

    # Focus on the 10 largest absolute alpha positions
    alpha_df = df.copy()
    alpha_df["abs_alpha"] = alpha_df["Alpha_pct"].abs()
    alpha_top = alpha_df.sort_values("abs_alpha", ascending=False).head(10)

    alpha_chart = (
        alt.Chart(alpha_top)
        .mark_bar()
        .encode(
            x=alt.X("Ticker:N", sort=None, title=""),
            y=alt.Y("Alpha_pct:Q", title="Active weight vs index (pct)"),
            color=alt.condition(
                "datum.Alpha_pct >= 0",
                alt.value("#22C55E"),  # green for overweight
                alt.value("#F97373"),  # red for underweight
            ),
            tooltip=[
                "Ticker",
                alt.Tooltip("Weight_pct:Q", title="Wave Weight %", format=".2f"),
                alt.Tooltip("Index_Weight:Q", title="Index Weight %", format=".2f"),
                alt.Tooltip("Alpha_pct:Q", title="Active Weight %", format=".2f"),
            ],
        )
        .properties(height=260)
    )

    st.altair_chart(alpha_chart, use_container_width=True)

    st.markdown("#### Top 10 by Weight")
    top10 = df_sorted.head(10)
    top10_chart = (
        alt.Chart(top10)
        .mark_bar()
        .encode(
            x=alt.X("Ticker:N", sort=None, title=""),
            y=alt.Y("Weight_pct:Q", title="% of Wave"),
            tooltip=[
                "Ticker",
                alt.Tooltip("Weight_pct:Q", title="Weight %", format=".2f"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(top10_chart, use_container_width=True)

# Full wave allocation + "heatmap" (right)
with right_col:
    st.markdown("#### Full Wave Allocation")
    st.caption("Each bar is a holding’s % weight in the Wave (top 150 shown).")

    top150 = df_sorted.head(150)

    full_chart = (
        alt.Chart(top150)
        .mark_bar()
        .encode(
            x=alt.X("Ticker:N", sort=None, title=""),
            y=alt.Y("Weight_pct:Q", title="% of Wave"),
            tooltip=[
                "Ticker",
                alt.Tooltip("Weight_pct:Q", title="Weight %", format=".2f"),
            ],
        )
        .properties(height=260)
    )
    st.altair_chart(full_chart, use_container_width=True)

    st.markdown("#### Alpha Heatmap (Top 50)")
    heat_df = (
        df.copy()
        .assign(rank=lambda x: x["Weight_pct"].rank(ascending=False, method="first"))
        .query("rank <= 50")
    )

    heat_chart = (
        alt.Chart(heat_df)
        .mark_rect()
        .encode(
            x=alt.X("Ticker:N", sort=None, title=""),
            y=alt.value(0),  # single row "heat strip"
            color=alt.Color(
                "Alpha_pct:Q",
                title="Active weight (%)",
                scale=alt.Scale(scheme="redblue", domainMid=0),
            ),
            tooltip=[
                "Ticker",
                alt.Tooltip("Weight_pct:Q", title="Wave Weight %", format=".2f"),
                alt.Tooltip("Index_Weight:Q", title="Index Weight %", format=".2f"),
                alt.Tooltip("Alpha_pct:Q", title="Active Weight %", format=".2f"),
            ],
        )
        .properties(height=60)
    )
    st.altair_chart(heat_chart, use_container_width=True)

# ------------------------------------------------------
# Largest positions table
# ------------------------------------------------------

st.markdown("#### Largest Positions (Table)")
largest_df = df_sorted[["Ticker", "Weight_pct"]].head(25)
st.dataframe(
    largest_df,
    use_container_width=True,
    hide_index=True,
    height=300,
)

# ------------------------------------------------------
# Footer / disclaimer
# ------------------------------------------------------

st.markdown("---")
st.caption(
    "Upload-based view • Data source: internal Wave CSV snapshots • "
    "WAVES Intelligence™ • Internal demo only (not investment advice)."
)
