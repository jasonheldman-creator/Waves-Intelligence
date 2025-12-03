import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ---------------------------------------------------------
# Basic page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="WAVES Intelligence™ — Wave Console",
    layout="wide",
)

# ---------------------------------------------------------
# Simple dark styling
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #020617;
        color: #E5E7EB;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        color: #E5E7EB;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }
    .metric-card {
        background: #020818;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        border: 1px solid #1F2937;
        box-shadow: 0 16px 32px rgba(0,0,0,0.6);
    }
    .metric-label {
        font-size: 0.72rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #9CA3AF;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 600;
        margin-top: 2px;
    }
    .metric-sub {
        font-size: 0.72rem;
        color: #9CA3AF;
    }
    .section-card {
        background: #020818;
        border-radius: 12px;
        padding: 1rem 1.1rem 1.1rem 1.1rem;
        border: 1px solid #1F2937;
    }
    .section-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .section-caption {
        font-size: 0.76rem;
        color: #9CA3AF;
        margin-bottom: 0.6rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

ACCENT = "#22C55E"
ACCENT_SOFT = "#38BDF8"

# ---------------------------------------------------------
# Wave definitions (simplified)
# ---------------------------------------------------------
WAVES = {
    "sp500": {
        "label": "S&P 500 Wave (LIVE Demo)",
        "benchmark": "S&P 500 Index",
    },
    "tech_leaders": {
        "label": "Tech Leaders Wave",
        "benchmark": "NASDAQ 100",
    },
    "quality_core": {
        "label": "Quality Core Wave",
        "benchmark": "Global Quality Composite",
    },
    "us_core": {
        "label": "US Core Equity Wave",
        "benchmark": "Total US Market",
    },
}

# ---------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌊 WAVES Intelligence™")
    st.caption("Simple Wave Console v1 (CSV-driven demo)")

    # Wave selector
    label_to_key = {cfg["label"]: key for key, cfg in WAVES.items()}
    chosen_label = st.selectbox(
        "Select Wave",
        options=list(label_to_key.keys()),
        index=0,
    )
    wave_key = label_to_key[chosen_label]
    wave_cfg = WAVES[wave_key]

    st.markdown(
        f"**Wave type:** AI-Managed Wave  \n"
        f"**Benchmark:** {wave_cfg['benchmark']}"
    )

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload Wave snapshot (.csv)",
        type=["csv"],
        help=(
            "Expected columns (names can vary): "
            "Ticker, Price, Dollar_Alloc "
            "(optional: Weight_pct, Index_Weight)."
        ),
    )

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown("## WAVES INTELLIGENCE™")
st.markdown(
    f"**{wave_cfg['label']}** — Institutional Portfolio Console"
)
st.markdown(
    f"<span style='color:{ACCENT_SOFT};font-size:0.85rem;'>"
    f"CSV-driven demo • No external market data</span>",
    unsafe_allow_html=True,
)
st.markdown("")

# ---------------------------------------------------------
# If no CSV yet, show instructions and stop
# ---------------------------------------------------------
if uploaded_file is None:
    st.info(
        "Upload the latest Wave snapshot CSV in the sidebar to render the console. "
        "Use your Google Sheets export for this Wave."
    )
    st.stop()

# ---------------------------------------------------------
# Load & normalize CSV
# ---------------------------------------------------------
try:
    raw_df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Standardize column names
raw_df.columns = [c.strip().replace(" ", "_") for c in raw_df.columns]
lower_cols = {c.lower(): c for c in raw_df.columns}


def pick(*candidates):
    """Pick the first matching column from a set of candidate names."""
    for cand in candidates:
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
    return None


ticker_col = pick("Ticker")
price_col = pick("Price", "Last")
dollar_col = pick("Dollar_Alloc", "DollarAlloc", "Dollar_Value")
weight_col = pick("Weight_pct", "Weight", "Weight_%", "WeightPct")
index_weight_col = pick("Index_Weight", "Benchmark_Weight", "Idx_Weight")

missing = [
    name
    for name, col in [
        ("Ticker", ticker_col),
        ("Price", price_col),
        ("Dollar_Alloc", dollar_col),
    ]
    if col is None
]

if missing:
    st.error(
        "CSV is missing required columns: "
        + ", ".join(missing)
        + ". Required: Ticker, Price, Dollar_Alloc.",
        icon="⚠️",
    )
    st.stop()

# Rename to standard schema
df = raw_df.rename(
    columns={
        ticker_col: "Ticker",
        price_col: "Price",
        dollar_col: "Dollar_Alloc",
        **({weight_col: "Weight_pct"} if weight_col else {}),
        **({index_weight_col: "Index_Weight"} if index_weight_col else {}),
    }
)

# Ensure numeric where needed
for col in ["Price", "Dollar_Alloc", "Weight_pct", "Index_Weight"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Group by ticker in case of duplicates
agg = {"Price": "last", "Dollar_Alloc": "sum"}
if "Weight_pct" in df.columns:
    agg["Weight_pct"] = "sum"
if "Index_Weight" in df.columns:
    agg["Index_Weight"] = "mean"

df = df.groupby("Ticker", as_index=False).agg(agg)

# Recompute weights to ensure consistency
total_nav = df["Dollar_Alloc"].sum()
if total_nav <= 0:
    st.error("Total NAV from Dollar_Alloc is non-positive. Check your CSV.")
    st.stop()

df["Weight_pct"] = df["Dollar_Alloc"] / total_nav * 100.0

num_holdings = df["Ticker"].nunique()
largest_position = df["Weight_pct"].max()
top10_conc = df.nlargest(10, "Weight_pct")["Weight_pct"].sum()

# ---------------------------------------------------------
# Helper for charts
# ---------------------------------------------------------
def base_chart(data: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(data)
        .configure_axis(
            labelColor="#9CA3AF",
            titleColor="#9CA3AF",
            gridColor="#111827",
        )
        .configure_view(strokeOpacity=0)
        .configure_legend(
            labelColor="#9CA3AF",
            titleColor="#9CA3AF",
        )
    )

# ---------------------------------------------------------
# Metric row
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">TOTAL NAV</div>
          <div class="metric-value">${total_nav:,.0f}</div>
          <div class="metric-sub">From uploaded CSV</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label"># OF HOLDINGS</div>
          <div class="metric-value">{num_holdings}</div>
          <div class="metric-sub">Unique tickers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">LARGEST POSITION</div>
          <div class="metric-value">{largest_position:.2f}%</div>
          <div class="metric-sub">Max single-name weight</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">TOP 10 CONCENTRATION</div>
          <div class="metric-value">{top10_conc:.2f}%</div>
          <div class="metric-sub">Sum of top 10 weights</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

# ---------------------------------------------------------
# Top holdings & bar chart
# ---------------------------------------------------------
left, right = st.columns([1, 1.2])

# ----- Left: top holdings table -----
with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Top Holdings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Sorted by % weight in the Wave.</div>',
        unsafe_allow_html=True,
    )

    top_n = min(25, num_holdings)
    top_df = df.sort_values("Weight_pct", ascending=False).head(top_n).copy()

    # Create simple view
    view = top_df[["Ticker", "Price", "Dollar_Alloc", "Weight_pct"]].copy()
    view["Price"] = view["Price"].round(2)
    view["Dollar_Alloc"] = view["Dollar_Alloc"].round(0)
    view["Weight_pct"] = view["Weight_pct"].round(3)

    st.dataframe(
        view.rename(
            columns={
                "Dollar_Alloc": "Dollar_Alloc ($)",
                "Weight_pct": "Weight (%)",
            }
        ),
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Right: allocation chart -----
with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Wave Allocation (Top 50)</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-caption">Each bar is a holding’s % weight in the Wave.</div>',
        unsafe_allow_html=True,
    )

    alloc = df.sort_values("Weight_pct", ascending=False).head(50)
    chart = (
        base_chart(alloc)
        .mark_bar(color=ACCENT_SOFT)
        .encode(
            x=alt.X("Ticker:N", sort=None, title=None),
            y=alt.Y(
                "Weight_pct:Q",
                title="Weight (%)",
                axis=alt.Axis(format=".1f"),
            ),
            tooltip=[
                alt.Tooltip("Ticker:N"),
                alt.Tooltip("Weight_pct:Q", title="Weight (%)", format=".2f"),
                alt.Tooltip(
                    "Dollar_Alloc:Q", title="Dollar alloc", format="$,.0f"
                ),
            ],
        )
        .properties(height=260)
    )
    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "CSV-driven demo • WAVES Intelligence™ • Internal prototype only (not investment advice)."
)