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
# Theme colors (keep these simple to avoid CSS syntax issues)
# ---------------------------------------------------------
DARK_BG = "#020617"      # almost black
CARD_BG = "#020818"
TEXT_MAIN = "#E5E7EB"
TEXT_MUTED = "#9CA3AF"
ACCENT = "#22C55E"       # neon-ish green
ACCENT_SOFT = "#38BDF8"  # teal / blue
BORDER = "#1F2937"

# ---------------------------------------------------------
# Minimal CSS for dark look (NO f-strings to avoid braces issues)
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #020617 !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1350px;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #E5E7EB !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }
    .metric-card {
        background: radial-gradient(circle at top left, #0F172A, #020617);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        border: 1px solid #1F2937;
        box-shadow: 0 18px 40px rgba(0,0,0,0.60);
    }
    .metric-label {
        font-size: 0.72rem;
        letter-spacing: .16em;
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
        border-radius: 14px;
        padding: 1rem 1.25rem 1.1rem 1.25rem;
        border: 1px solid #1F2937;
    }
    .section-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .section-caption {
        font-size: 0.75rem;
        color: #9CA3AF;
        margin-bottom: 0.6rem;
    }
    .sidebar-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Wave definitions (15 slots, all equity-style Waves)
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
        "label": "Small–Mid Cap Growth Wave",
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
    "us_core": {
        "label": "US Core Equity Wave",
        "benchmark": "Total US Market",
        "csv_hint": "US_CORE_EQUITY_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "intl_dev": {
        "label": "International Developed Wave",
        "benchmark": "MSCI EAFE",
        "csv_hint": "INTL_DEV_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "em": {
        "label": "Emerging Markets Wave",
        "benchmark": "MSCI EM",
        "csv_hint": "EM_WAVE.csv",
        "wave_type": "Core Wave",
    },
    "div_growth": {
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
# Sidebar: control panel
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
        "<div class='sidebar-title'>Wave type:</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"{wave_cfg['wave_type']} • Benchmark: {wave_cfg['benchmark']}")

    st.markdown("---")

    st.markdown(
        "<div class='sidebar-title'>SmartSafe™ level (for meeting demos)</div>",
        unsafe_allow_html=True,
    )
    smartsafe = st.radio(
        "SmartSafe level",
        ["Standard", "Defensive", "Max Safety"],
        index=0,
        label_visibility="collapsed",
    )

    if smartsafe == "Standard":
        safe_caption = "Standard — fully invested, normal risk budget."
    elif smartsafe == "Defensive":
        safe_caption = "Defensive — elevated cash / SmartSafe™, trimmed tails."
    else:
        safe_caption = "Max Safety — high cash / SmartSafe™, risk engine throttled."

    st.caption(safe_caption)

    st.markdown("---")

    st.markdown(
        "<div class='sidebar-title'>Upload latest Wave snapshot (.csv)</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Expected columns (any order): **Ticker, Price, Dollar_Alloc** "
        "(optional: Weight_pct, Index_Weight).<br>"
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
# Header
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
    "AI-Managed Wave • Real-time demo • CSV-driven • No external data calls</span>",
    unsafe_allow_html=True,
)
st.markdown("")

# ---------------------------------------------------------
# If no CSV yet, show instructions and stop
# ---------------------------------------------------------
if portfolio_file is None:
    st.info(
        "Upload the latest Wave snapshot CSV in the sidebar to render the console. "
        "Use your Google Sheets export for the selected Wave."
    )
    st.stop()

# ---------------------------------------------------------
# Load & normalize data
# ---------------------------------------------------------
try:
    raw_df = pd.read_csv(portfolio_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Normalize column names
raw_df.columns = [c.strip().replace(" ", "_") for c in raw_df.columns]
lower_cols = {c.lower(): c for c in raw_df.columns}


def pick_col(*candidates):
    for cand in candidates:
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
    return None


ticker_col = pick_col("Ticker")
price_col = pick_col("Price", "Last")
dollar_col = pick_col("Dollar_Alloc", "DollarAlloc", "Dollar_Value")
weight_col = pick_col("Weight_pct", "Weight", "Weight_%", "WeightPct")
index_weight_col = pick_col("Index_Weight", "Benchmark_Weight", "Idx_Weight")

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
        "CSV is missing required columns: " + ", ".join(missing)
        + ". Required: Ticker, Price, Dollar_Alloc. "
        + "Optional: Weight_pct, Index_Weight."
    )
    st.stop()

# Rename to standard names
rename_map = {
    ticker_col: "Ticker",
    price_col: "Price",
    dollar_col: "Dollar_Alloc",
}
if weight_col:
    rename_map[weight_col] = "Weight_pct"
if index_weight_col:
    rename_map[index_weight_col] = "Index_Weight"

df = raw_df.rename(columns=rename_map)

# Ensure numeric
for col in ["Price", "Dollar_Alloc", "Weight_pct", "Index_Weight"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# De-duplicate tickers: sum allocations, last price, etc.
agg = {"Price": "last", "Dollar_Alloc": "sum"}
if "Weight_pct" in df.columns:
    agg["Weight_pct"] = "sum"
if "Index_Weight" in df.columns:
    agg["Index_Weight"] = "mean"

df = df.groupby("Ticker", as_index=False).agg(agg)

# Recompute weights from Dollar_Alloc for consistency
total_nav = df["Dollar_Alloc"].sum()
if total_nav <= 0:
    st.error("Total NAV from Dollar_Alloc is non-positive. Check your CSV.")
    st.stop()

df["Weight_pct"] = df["Dollar_Alloc"] / total_nav * 100.0

num_holdings = df["Ticker"].nunique()
largest_position = df["Weight_pct"].max()
top10_conc = df.nlargest(10, "Weight_pct")["Weight_pct"].sum()

# Helper: ticker → Google search link
def ticker_link(ticker: str) -> str:
    url = f"https://www.google.com/search?q={ticker}+stock"
    return f"[{ticker}]({url})"


# ---------------------------------------------------------
# Altair base chart config (dark mode)
# ---------------------------------------------------------
def base_chart(data: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(data)
        .configure_axis(labelColor=TEXT_MUTED, titleColor=TEXT_MUTED, gridColor="#111827")
        .configure_view(strokeOpacity=0)
        .configure_legend(labelColor=TEXT_MUTED, titleColor=TEXT_MUTED)
    )

# ---------------------------------------------------------
# Metric row
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
# Row 1: Top holdings + Alpha vs Index + Full allocation
# ---------------------------------------------------------
c1, c2, c3 = st.columns([1.1, 1.1, 1.4])

# ----- Top holdings table -----
with c1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top Holdings</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Sorted by Wave weight. "
        "Tickers link out to live research.</div>",
        unsafe_allow_html=True,
    )

    if num_holdings <= 5:
        top_df = df.sort_values("Weight_pct", ascending=False)
    else:
        max_rows = min(50, num_holdings)
        default_rows = min(20, max_rows)
        rows = st.slider("Rows", 5, max_rows, default_rows, key="top_rows")
        top_df = df.sort_values("Weight_pct", ascending=False).head(rows)

    table_view = pd.DataFrame(
        {
            "Ticker": [ticker_link(t) for t in top_df["Ticker"]],
            "Price": top_df["Price"].round(2),
            "Dollar_Alloc": top_df["Dollar_Alloc"].round(0),
            "Weight_%": top_df["Weight_pct"].round(3),
        }
    )
    st.markdown(table_view.to_markdown(index=False), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Allocation Alpha vs Index -----
with c2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Allocation Alpha vs Index</div>", unsafe_allow_html=True)

    if "Index_Weight" not in df.columns:
        st.markdown(
            "<div class='section-caption'>Add an `Index_Weight` column to your CSV "
            "to view overweight / underweight vs benchmark.</div>",
            unsafe_allow_html=True,
        )
        st.info("No `Index_Weight` column found. Skipping alpha chart.")
    else:
        st.markdown(
            "<div class='section-caption'>Positive bars = overweight vs index. "
            "Negative bars = underweight.</div>",
            unsafe_allow_html=True,
        )
        alpha_df = df.copy()
        alpha_df["Active_pct"] = alpha_df["Weight_pct"] - alpha_df["Index_Weight"]
        alpha_top = alpha_df.reindex(
            alpha_df["Active_pct"].abs().sort_values(ascending=False).head(10).index
        )

        chart = (
            base_chart(alpha_top)
            .mark_bar()
            .encode(
                x=alt.X("Ticker:N", sort=None, title=None),
                y=alt.Y(
                    "Active_pct:Q",
                    title="Active weight vs Index (pct)",
                    axis=alt.Axis(format=".1f"),
                ),
                color=alt.condition(
                    "datum.Active_pct >= 0",
                    alt.value(ACCENT),
                    alt.value("#F97373"),
                ),
                tooltip=[
                    alt.Tooltip("Ticker:N"),
                    alt.Tooltip("Weight_pct:Q", title="Wave weight", format=".2f"),
                    alt.Tooltip("Index_Weight:Q", title="Index weight", format=".2f"),
                    alt.Tooltip("Active_pct:Q", title="Active", format=".2f"),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----- Full Wave Allocation -----
with c3:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Full Wave Allocation</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Each bar is a holding’s % weight in the Wave "
        "(top 150 holdings shown).</div>",
        unsafe_allow_html=True,
    )

    alloc = df.sort_values("Weight_pct", ascending=False).head(150)
    alloc_chart = (
        base_chart(alloc)
        .mark_bar(color=ACCENT_SOFT)
        .encode(
            x=alt.X("Ticker:N", sort=None, title=None),
            y=alt.Y(
                "Weight_pct:Q",
                title="% of Wave",
                axis=alt.Axis(format=".1f"),
            ),
            tooltip=[
                alt.Tooltip("Ticker:N"),
                alt.Tooltip("Weight_pct:Q", title="Weight", format=".2f"),
                alt.Tooltip("Dollar_Alloc:Q", title="Dollar", format="$.0f"),
            ],
        )
        .properties(height=260)
    )
    st.altair_chart(alloc_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

# ---------------------------------------------------------
# Row 2: Top 10, Alpha heatmap, Largest positions
# ---------------------------------------------------------
c4, c5, c6 = st.columns([1, 1.2, 1])

# ----- Top 10 by weight -----
with c4:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top 10 by Weight</div>", unsafe_allow_html=True)

    top10 = df.sort_values("Weight_pct", ascending=False).head(10)
    top10_chart = (
        base_chart(top10)
        .mark_bar(color=ACCENT)
        .encode(
            x=alt.X("Ticker:N", sort=None, title=None),
            y=alt.Y(
                "Weight_pct:Q",
                title="Weight (%)",
                axis=alt.Axis(format=".1f"),
            ),
            tooltip=[
                alt.Tooltip("Ticker:N"),
                alt.Tooltip("Weight_pct:Q", title="Weight", format=".2f"),
                alt.Tooltip("Dollar_Alloc:Q", title="Dollar", format="$.0f"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(top10_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Alpha “heatmap” (bar) -----
with c5:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Alpha Heatmap (Top 50)</div>", unsafe_allow_html=True)

    if "Index_Weight" not in df.columns:
        st.markdown(
            "<div class='section-caption'>Add `Index_Weight` to unlock the alpha heatmap.</div>",
            unsafe_allow_html=True,
        )
        st.info("No `Index_Weight` column found. Skipping heatmap.")
    else:
        st.markdown(
            "<div class='section-caption'>Sorted by absolute active weight (over / under index).</div>",
            unsafe_allow_html=True,
        )
        alpha_df2 = df.copy()
        alpha_df2["Active_pct"] = alpha_df2["Weight_pct"] - alpha_df2["Index_Weight"]
        heat_df = alpha_df2.reindex(
            alpha_df2["Active_pct"].abs().sort_values(ascending=False).head(50).index
        )

        heat_chart = (
            base_chart(heat_df)
            .mark_bar()
            .encode(
                x=alt.X("Ticker:N", sort=None, title=None),
                y=alt.Y(
                    "Active_pct:Q",
                    title="Active vs Index (pct)",
                    axis=alt.Axis(format=".1f"),
                ),
                color=alt.condition(
                    "datum.Active_pct >= 0",
                    alt.value(ACCENT),
                    alt.value("#F97373"),
                ),
                tooltip=[
                    alt.Tooltip("Ticker:N"),
                    alt.Tooltip("Weight_pct:Q", title="Wave weight", format=".2f"),
                    alt.Tooltip("Index_Weight:Q", title="Index weight", format=".2f"),
                    alt.Tooltip("Active_pct:Q", title="Active", format=".2f"),
                ],
            )
            .properties(height=220)
        )
        st.altair_chart(heat_chart, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----- Largest positions table -----
with c6:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Largest Positions (Table)</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Top 20 holdings by % weight. Click tickers for detail.</div>",
        unsafe_allow_html=True,
    )

    big = df.sort_values("Weight_pct", ascending=False).head(20)
    big_view = pd.DataFrame(
        {
            "Ticker": [ticker_link(t) for t in big["Ticker"]],
            "Weight_%": big["Weight_pct"].round(3),
        }
    )
    st.markdown(big_view.to_markdown(index=False), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "Upload-based demo • Data source: Wave CSV exports • "
    "WAVES Intelligence™ • Internal demo only (not investment advice)."
)