import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="WAVES Intelligence™ – Institutional Wave Console",
    layout="wide",
    page_icon="🌊",
)

# ---------------------------------------------------------
# Dark theme & WAVES branding CSS
# ---------------------------------------------------------
st.markdown(
    """
<style>
/* Global app background */
.stApp {
    background-color: #02030A;
    color: #F5F7FA;
    font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

/* Remove default header background */
header[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #050716;
    border-right: 1px solid #111827;
}
section[data-testid="stSidebar"] * {
    color: #E5E7EB !important;
}

/* Metric cards */
.metric-card {
    background: radial-gradient(circle at top left, #0F172A, #020617);
    border-radius: 16px;
    padding: 14px 18px;
    border: 1px solid #1F2937;
}
.metric-label {
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9CA3AF;
}
.metric-value {
    font-size: 1.7rem;
    font-weight: 600;
    color: #F9FAFB;
}

/* Section titles */
.section-title {
    font-size: 0.8rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #A5B4FC;
}

/* Dataframe tweaks */
.stDataFrame {
    border-radius: 10px;
    border: 1px solid #1F2933;
    overflow: hidden;
}

/* WAVES neon brand */
.waves-title {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    background: linear-gradient(90deg, #00FFA7, #00E5FF);
    -webkit-background-clip: text;
    color: transparent;
}
.waves-subtitle {
    font-size: 0.95rem;
    color: #9CA3AF;
}
.badge {
    display: inline-flex;
    align-items: center;
    font-size: 0.7rem;
    border-radius: 999px;
    padding: 2px 9px;
    margin-right: 6px;
    border: 1px solid rgba(148, 163, 184, 0.6);
    color: #E5E7EB;
}
.badge-green {
    border-color: #22C55E;
    color: #BBF7D0;
}
.badge-outline {
    border-style: dashed;
}

/* Slider color tweak */
[data-baseweb="slider"] > div > div {
    background-color: #1F2937 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Altair base config helper (dark theme)
# ---------------------------------------------------------
def style_chart(chart):
    return (
        chart.configure_view(strokeWidth=0, fill="#02030A")
        .configure_title(color="#E5E7EB", fontSize=13)
        .configure_axis(
            labelColor="#9CA3AF",
            titleColor="#9CA3AF",
            gridColor="#111827"
        )
        .configure_legend(
            labelColor="#E5E7EB",
            titleColor="#E5E7EB",
            orient="top"
        )
        .properties(background="#02030A")
    )


# ---------------------------------------------------------
# Sidebar – Wave selector + SmartSafe
# ---------------------------------------------------------
st.sidebar.markdown("### 🌊 WAVES Intelligence™")
st.sidebar.caption("Institutional Wave Console (alpha demo)")

wave_options = {
    "sp500": {
        "label": "S&P 500 Wave (LIVE Demo)",
        "benchmark": "S&P 500 Index",
        "note": "Flagship US large-cap core Wave."
    },
    "us_growth": {
        "label": "US Growth Wave",
        "benchmark": "Russell 1000 Growth",
        "note": "Concentrated large-cap growth leaders."
    },
    "us_value": {
        "label": "US Value Wave",
        "benchmark": "Russell 1000 Value",
        "note": "Quality value & dividend tilt."
    },
    "smid_growth": {
        "label": "Small–Mid Growth Wave",
        "benchmark": "Russell 2500 Growth",
        "note": "Smaller company innovation beta."
    },
    "future_power": {
        "label": "Future Power & Energy Wave",
        "benchmark": "Clean + Next-Gen Energy Basket",
        "note": "Energy transition, renewables, grid."
    },
    "global_equity": {
        "label": "Global Universe Wave",
        "benchmark": "MSCI ACWI",
        "note": "All-world multi-region equity stack."
    },
    "equity_income": {
        "label": "Equity Income Wave",
        "benchmark": "High Dividend Equity Index",
        "note": "Cash-flow rich, dividend-focused equity."
    },
    "rwa_income": {
        "label": "RWA Income Wave",
        "benchmark": "Blended RWA / Credit Index",
        "note": "Tokenized income & real-world assets."
    },
    # Add more equity Waves here as needed…
}

wave_key = st.sidebar.selectbox(
    "Select Wave",
    options=list(wave_options.keys()),
    format_func=lambda k: wave_options[k]["label"],
)

selected_wave = wave_options[wave_key]

st.sidebar.markdown("##### SmartSafe™ level (for meeting demos)")
smart_safe = st.sidebar.radio(
    "",
    ["Standard", "Defensive", "Max Safety"],
    index=0,
)

st.sidebar.markdown(
    """
Tip: Use different SmartSafe™ levels live  
to narrate how WAVES can **dial risk down**  
without touching the core engine.
"""
)

# ---------------------------------------------------------
# Main header
# ---------------------------------------------------------
st.markdown(
    f"""
<div class="waves-title">WAVES INTELLIGENCE™</div>
<div class="waves-subtitle">
    {selected_wave["label"]} — Institutional Portfolio Console
</div>
<br>
<div>
    <span class="badge badge-green">AI-Managed Wave</span>
    <span class="badge">Benchmark: {selected_wave["benchmark"]}</span>
    <span class="badge badge-outline">SmartSafe™: {smart_safe}</span>
    <span class="badge badge-outline">Real-time demo · CSV-driven · No external data calls</span>
</div>
<br>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# File upload
# ---------------------------------------------------------
st.markdown(
    "#### Upload latest Wave snapshot  <span style='color:#22C55E'>(.csv)</span>",
    unsafe_allow_html=True,
)

st.caption(
    "Upload the most recent export for **this Wave** "
    "(e.g., `SP500_PORTFOLIO_FINAL.csv`). "
    "Expected core columns: `Ticker`, `Price`, `Dollar_Alloc`, `Index_Weight`."
)

uploaded_file = st.file_uploader(
    "Drag & drop file here, or browse",
    type=["csv"],
    label_visibility="collapsed",
)

if uploaded_file is None:
    st.info("👆 Upload a Wave snapshot CSV to activate the console.")
    st.stop()

# ---------------------------------------------------------
# Load + normalize CSV
# ---------------------------------------------------------
try:
    raw_df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Normalize column names (strip spaces, unify case)
norm_cols = {c: c.strip().replace(" ", "_") for c in raw_df.columns}
raw_df = raw_df.rename(columns=norm_cols)

# Expected column mapping
required_cols = ["Ticker", "Price", "Dollar_Alloc", "Index_Weight"]

missing = [c for c in required_cols if c not in raw_df.columns]
if missing:
    st.error(
        "Missing required columns in CSV: "
        + ", ".join(missing)
        + "<br><br>"
        + "Expected **at least**: `Ticker`, `Price`, `Dollar_Alloc`, `Index_Weight`.",
        icon="⚠️",
    )
    st.stop()

df = raw_df[required_cols].copy()

# ---------------------------------------------------------
# Clean & aggregate positions by Ticker
# ---------------------------------------------------------
for col in ["Price", "Dollar_Alloc", "Index_Weight"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Ticker", "Dollar_Alloc", "Index_Weight"])

agg_df = (
    df.groupby("Ticker", as_index=False)
    .agg(
        {
            "Price": "first",          # assume prices identical within ticker
            "Dollar_Alloc": "sum",     # sum exposure
            "Index_Weight": "sum",     # sum index weight share
        }
    )
)

total_alloc = agg_df["Dollar_Alloc"].sum()
if total_alloc <= 0 or pd.isna(total_alloc):
    st.error(
        "Total `Dollar_Alloc` is 0 or invalid after aggregation. "
        "Please check the uploaded file."
    )
    st.stop()

agg_df["Weight_pct"] = agg_df["Dollar_Alloc"] / total_alloc * 100.0
agg_df["Alpha_pct"] = agg_df["Weight_pct"] - agg_df["Index_Weight"]

df = agg_df.copy()
df_sorted = df.sort_values("Weight_pct", ascending=False).reset_index(drop=True)

# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------
total_nav = total_alloc
num_holdings = len(df_sorted)
largest_position = df_sorted["Weight_pct"].max()
top10_conc = df_sorted["Weight_pct"].nlargest(10).sum()

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label">Total NAV</div>
  <div class="metric-value">${total_nav:,.0f}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label"># of Holdings</div>
  <div class="metric-value">{num_holdings:,}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label">Largest Position</div>
  <div class="metric-value">{largest_position:.2f}%</div>
</div>
""",
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label">Top 10 Concentration</div>
  <div class="metric-value">{top10_conc:.2f}%</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---------------------------------------------------------
# Top holdings (table) + Alpha vs Index chart
# ---------------------------------------------------------
st.markdown('<div class="section-title">Top Holdings</div>', unsafe_allow_html=True)

top_rows = st.slider("Rows", min_value=10, max_value=50, value=20, step=5)

left, mid, right = st.columns([1.1, 1.2, 1.3])

with left:
    top_table = df_sorted.head(top_rows)[["Ticker", "Price", "Dollar_Alloc", "Weight_pct"]]
    st.dataframe(
        top_table,
        use_container_width=True,
        hide_index=True,
    )

with mid:
    st.markdown(
        '<div class="section-title">Allocation Alpha vs Index</div>',
        unsafe_allow_html=True,
    )
    top_alpha = df_sorted.head(15)

    alpha_chart = alt.Chart(top_alpha).mark_bar().encode(
        x=alt.X("Ticker:N", sort=None, title=None),
        y=alt.Y("Alpha_pct:Q", title="Active weight vs Index (pct)"),
        color=alt.condition(
            "datum.Alpha_pct >= 0",
            alt.value("#22C55E"),  # green for overweight
            alt.value("#F97373"),  # red for underweight
        ),
        tooltip=[
            alt.Tooltip("Ticker:N"),
            alt.Tooltip("Weight_pct:Q", title="Wave Weight (%)", format=".2f"),
            alt.Tooltip("Index_Weight:Q", title="Index Weight (%)", format=".2f"),
            alt.Tooltip("Alpha_pct:Q", title="Active vs Index (%)", format=".2f"),
        ],
    ).properties(
        height=260,
        title="Allocation Alpha vs Benchmark (Top 15)",
    )

    st.altair_chart(style_chart(alpha_chart), use_container_width=True)

with right:
    st.markdown(
        '<div class="section-title">Full Wave Allocation</div>',
        unsafe_allow_html=True,
    )
    full = df_sorted.head(150)

    alloc_chart = alt.Chart(full).mark_bar().encode(
        x=alt.X("Ticker:N", sort=None, title=None),
        y=alt.Y("Weight_pct:Q", title="% of Wave"),
        tooltip=[
            alt.Tooltip("Ticker:N"),
            alt.Tooltip("Weight_pct:Q", title="Wave Weight (%)", format=".2f"),
        ],
    ).properties(
        height=260,
        title="Weight distribution (top 150 names)",
    )

    st.altair_chart(style_chart(alloc_chart), use_container_width=True)

# ---------------------------------------------------------
# Bottom row: Top 10 by Weight + Alpha heatmap
# ---------------------------------------------------------
st.markdown("---")
st.markdown('<div class="section-title">Wave Concentration & Alpha Map</div>', unsafe_allow_html=True)

b1, b2 = st.columns([1.1, 1.6])

with b1:
    st.markdown("##### Top 10 by Weight")
    top10 = df_sorted.head(10)

    top10_chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X("Ticker:N", sort=None, title=None),
        y=alt.Y("Weight_pct:Q", title="% of Wave"),
        color=alt.value("#38BDF8"),
        tooltip=[
            alt.Tooltip("Ticker:N"),
            alt.Tooltip("Weight_pct:Q", title="Wave Weight (%)", format=".2f"),
        ],
    ).properties(height=260)

    st.altair_chart(style_chart(top10_chart), use_container_width=True)

    st.markdown("##### Largest Positions (Table)")
    st.dataframe(
        top10[["Ticker", "Weight_pct"]],
        use_container_width=True,
        hide_index=True,
    )

with b2:
    st.markdown("##### Alpha Heatmap (Top 50 by Weight)")
    top50 = df_sorted.head(50).copy()
    top50["Rank"] = np.arange(1, len(top50) + 1)

    heatmap = alt.Chart(top50).mark_rect().encode(
        x=alt.X("Rank:O", title="Weight rank (1 = largest)"),
        y=alt.Y("Ticker:N", sort=None, title=None),
        color=alt.Color(
            "Alpha_pct:Q",
            title="Active weight (%)",
            scale=alt.Scale(scheme="redyellowgreen", domainMid=0),
        ),
        tooltip=[
            alt.Tooltip("Ticker:N"),
            alt.Tooltip("Weight_pct:Q", title="Wave Weight (%)", format=".2f"),
            alt.Tooltip("Index_Weight:Q", title="Index Weight (%)", format=".2f"),
            alt.Tooltip("Alpha_pct:Q", title="Active vs Index (%)", format=".2f"),
        ],
    ).properties(
        height=360,
    )

    st.altair_chart(style_chart(heatmap), use_container_width=True)

# ---------------------------------------------------------
# Footer note
# ---------------------------------------------------------
st.markdown(
    """
---
<span style="font-size:0.7rem;color:#6B7280;">
CSV-upload demo only · No live trading.  
Wave weights & alpha are for **illustration** and internal discussion with Franklin / other institutional buyers.  
WAVES Intelligence™ · Engineered to outperform.
</span>
""",
    unsafe_allow_html=True,
)