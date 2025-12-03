import streamlit as st
import pandas as pd
import numpy as np

# ---------------- Page config ----------------

st.set_page_config(
    page_title="WAVES Intelligence™ — Institutional Wave Console",
    page_icon="🌊",
    layout="wide",
)

# ---------------- Sidebar: Wave selector & SmartSafe ----------------

st.sidebar.markdown("### 🌊 WAVES Intelligence™")
st.sidebar.caption("Institutional Wave Console (alpha demo)")

wave_options = {
    "S&P 500 Wave (LIVE Demo)": {
        "title": "S&P 500 Wave — Institutional Portfolio Console",
        "tag": "AI-Managed Wave",
        "benchmark_label": "S&P 500 Index",
        "csv_label": "SP500_PORTFOLIO_FINAL.csv",
    },
    "Global Universe Wave (Equity)": {
        "title": "Global Universe Wave — Institutional Portfolio Console",
        "tag": "AI-Managed Global Equity Wave",
        "benchmark_label": "Global Equity Index",
        "csv_label": "GLOBAL_UNIVERSE_FINAL.csv",
    },
    "US Growth Wave": {
        "title": "US Growth Wave — Institutional Portfolio Console",
        "tag": "High-Growth Equity Wave",
        "benchmark_label": "US Growth Index",
        "csv_label": "US_GROWTH_FINAL.csv",
    },
    "Small Cap Growth Wave": {
        "title": "Small Cap Growth Wave — Institutional Portfolio Console",
        "tag": "Small-Cap Growth Equity Wave",
        "benchmark_label": "Small Cap Growth Index",
        "csv_label": "SMALL_CAP_GROWTH_FINAL.csv",
    },
    "SMID Growth Wave": {
        "title": "SMID Growth Wave — Institutional Portfolio Console",
        "tag": "SMID-Cap Growth Equity Wave",
        "benchmark_label": "SMID Growth Index",
        "csv_label": "SMID_GROWTH_FINAL.csv",
    },
    "Future Power & Energy Wave": {
        "title": "Future Power & Energy Wave — Institutional Portfolio Console",
        "tag": "Energy & Transition Equity Wave",
        "benchmark_label": "Energy & Transition Benchmark",
        "csv_label": "FUTURE_POWER_ENERGY_FINAL.csv",
    },
    "Equity Income Wave": {
        "title": "Equity Income Wave — Institutional Portfolio Console",
        "tag": "Dividend & Income Equity Wave",
        "benchmark_label": "Equity Income Index",
        "csv_label": "EQUITY_INCOME_FINAL.csv",
    },
}

wave_name = st.sidebar.selectbox("Select Wave", list(wave_options.keys()))
wave_cfg = wave_options[wave_name]

st.sidebar.markdown(
    f"**Wave type:** {wave_cfg['tag']}  \n"
    f"**Benchmark:** {wave_cfg['benchmark_label']}"
)

smartsafe_level = st.sidebar.radio(
    "SmartSafe™ level (for meeting demos)",
    ["Standard", "Defensive", "Max Safety"],
    index=0,
)

# ---------------- Header & Branding ----------------

st.markdown(
    """
    <h1 style="color:#00FFA7;letter-spacing:0.12em;margin-bottom:0;margin-top:0.2rem;">
      WAVES INTELLIGENCE™
    </h1>
    """,
    unsafe_allow_html=True,
)

st.markdown(f"### {wave_cfg['title']}")

st.markdown(
    """
    <span style="background-color:#00FFA71A;color:#00FFA7;padding:3px 10px;
                 border-radius:20px;font-size:0.75rem;margin-right:6px;">
        AI-MANAGED WAVE
    </span>
    <span style="background-color:#222840;color:#A0AEC0;padding:3px 10px;
                 border-radius:20px;font-size:0.75rem;margin-right:6px;">
        Real-time demo • CSV-driven • No external data calls
    </span>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------- CSV upload ----------------

upload_label = f"Upload {wave_cfg['csv_label']} snapshot"

uploaded_file = st.file_uploader(
    upload_label,
    type="csv",
    help=f"Export the latest {wave_name} snapshot from Google Sheets as CSV, "
         f"then upload it here.",
)

if uploaded_file is None:
    st.info("👆 Upload your latest Wave CSV snapshot to see the dashboard.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

df.columns = [c.strip() for c in df.columns]

required_cols = ["Ticker", "Price", "Dollar_Alloc", "Weight_pct", "Index_Weight"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(
        "Missing required columns in CSV: "
        + ", ".join(missing)
        + ".\n\nExpected at least: "
        + ", ".join(required_cols)
    )
    st.stop()

df = df.copy()
df["Weight_pct"] = df["Weight_pct"].astype(float)
df["Dollar_Alloc"] = df["Dollar_Alloc"].astype(float)
df["Index_Weight"] = df["Index_Weight"].astype(float)
df["Alpha_pct"] = df["Weight_pct"] - df["Index_Weight"]

# ---------------- Top-line metrics ----------------

total_nav = float(df["Dollar_Alloc"].sum())
num_holdings = int(df["Ticker"].nunique())
largest_position = float(df["Weight_pct"].max())
top10_conc = float(
    df.sort_values("Weight_pct", ascending=False)
      .head(10)["Dollar_Alloc"].sum() / total_nav
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total NAV", f"${total_nav:,.0f}")
m2.metric("# of Holdings", f"{num_holdings:,}")
m3.metric("Largest Position", f"{largest_position:.2f}%")
m4.metric("Top 10 Concentration", f"{top10_conc*100:.2f}%")

st.markdown("---")

# ---------------- Layout: main panels ----------------

left, mid, right = st.columns([1.2, 1.1, 1.4])

# ---- Left: Top holdings table ----
with left:
    st.markdown("#### Top Holdings")
    st.caption(f"Sorted by weight in the {wave_name}.")
    rows = st.slider("Rows", min_value=10, max_value=50, value=20, step=5)
    top_df = (
        df.sort_values("Weight_pct", ascending=False)
        .head(rows)[["Ticker", "Price", "Dollar_Alloc", "Weight_pct"]]
    )
    st.dataframe(
        top_df,
        use_container_width=True,
        hide_index=True,
        height=420,
    )

# ---- Middle: Alpha vs Benchmark + Top 10 weights ----
with mid:
    st.markdown(f"#### Allocation Alpha vs {wave_cfg['benchmark_label']}")
    st.caption("Positive bars = overweight vs benchmark. Negative bars = underweight.")

    alpha_top = (
        df.sort_values("Alpha_pct", key=lambda s: s.abs(), ascending=False)
        .head(10)[["Ticker", "Alpha_pct"]]
        .set_index("Ticker")
    )
    st.bar_chart(alpha_top, use_container_width=True, height=220)

    st.markdown("#### Top 10 by Weight")
    wgt_top = (
        df.sort_values("Weight_pct", ascending=False)
        .head(10)[["Ticker", "Weight_pct"]]
        .set_index("Ticker")
    )
    st.bar_chart(wgt_top, use_container_width=True, height=220)

# ---- Right: Full allocation + alpha heatmap + largest table ----
with right:
    st.markdown("#### Full Wave Allocation")
    st.caption(f"Each bar is a holding’s % weight in the {wave_name} (top 150 shown).")
    all_weights = (
        df.sort_values("Weight_pct", ascending=False)
        .head(150)[["Ticker", "Weight_pct"]]
        .set_index("Ticker")
    )
    st.bar_chart(all_weights, use_container_width=True, height=220)

    st.markdown("#### Alpha Heatmap (Top 50)")
    st.caption("Quick view of overweight / underweight vs benchmark.")
    alpha_heat = (
        df.sort_values("Alpha_pct", ascending=False)
        .head(50)[["Ticker", "Alpha_pct"]]
        .set_index("Ticker")
    )

    heat_df = alpha_heat.copy()
    st.dataframe(
        heat_df.style.background_gradient(
            cmap="RdYlGn", axis=0, gmap=heat_df["Alpha_pct"]
        ),
        use_container_width=True,
        height=240,
    )

    st.markdown("#### Largest Positions (Table)")
    st.dataframe(
        df.sort_values("Weight_pct", ascending=False)
        .head(15)[["Ticker", "Weight_pct"]],
        use_container_width=True,
        hide_index=True,
        height=260,
    )

st.markdown("---")

# ---------------- SmartSafe™ demo panel ----------------

col1, col2, col3 = st.columns([1.2, 1.2, 1])

with col1:
    st.markdown("#### SmartSafe™ Scenario")
    if smartsafe_level == "Standard":
        cash_buffer = 5
        msg = "Standard SmartSafe™ keeps ~5% in cash for instant liquidity."
    elif smartsafe_level == "Defensive":
        cash_buffer = 15
        msg = "Defensive SmartSafe™ parks ~15% in cash to cushion volatility."
    else:
        cash_buffer = 30
        msg = "Max Safety SmartSafe™ holds ~30% in cash, ideal for stressed markets."
    st.write(msg)

with col2:
    invested = 100 - cash_buffer
    st.markdown("##### Allocation with SmartSafe™")
    st.write(f"• Cash buffer: **{cash_buffer}%**  ")
    st.write(f"• Invested in Wave engine: **{invested}%**")

with col3:
    st.markdown("#### Demo Notes")
    st.caption(
        "Use different SmartSafe™ levels live in the meeting to show how "
        "WAVES can de-risk without touching the core engine."
    )

# ---------------- Footer ----------------

st.markdown("---")
st.caption(
    "Upload-based view • Data source: CSV snapshots from WAVES Intelligence™ models.  \n"
    "WAVES Intelligence™ • Internal demo only (not investment advice)."
)
