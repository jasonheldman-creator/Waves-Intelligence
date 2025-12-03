import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ---------------------------------------------------------
# Cached helper functions for performance
# ---------------------------------------------------------
@st.cache_data
def normalize_columns(df):
    """Normalize column names to use underscores instead of spaces/dashes."""
    df = df.copy()
    df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]
    return df

@st.cache_data
def compute_dataframe(df, ticker_col, price_col, dollar_col, weight_col, index_weight_col):
    """Process and aggregate dataframe by ticker with caching."""
    # Build working dataframe with standard names
    rename_dict = {
        ticker_col: "Ticker",
        price_col: "Price",
        dollar_col: "Dollar_Alloc",
    }
    if weight_col:
        rename_dict[weight_col] = "Weight_pct"
    if index_weight_col:
        rename_dict[index_weight_col] = "Index_Weight"
    
    df = df.rename(columns=rename_dict)
    
    # Ensure numeric types
    for col in ["Price", "Dollar_Alloc", "Weight_pct", "Index_Weight"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Group by ticker (remove duplicate rows per name)
    group_cols = ["Ticker"]
    agg_dict = {"Price": "last", "Dollar_Alloc": "sum"}
    if "Weight_pct" in df.columns:
        agg_dict["Weight_pct"] = "sum"
    if "Index_Weight" in df.columns:
        agg_dict["Index_Weight"] = "mean"
    
    df = df.groupby(group_cols, as_index=False).agg(agg_dict)
    
    # Recompute weight_pct from Dollar_Alloc to be consistent
    total_nav = df["Dollar_Alloc"].sum()
    df["Weight_pct"] = df["Dollar_Alloc"] / total_nav * 100.0
    
    return df

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="WAVES Intelligence™ — Institutional Wave Console",
    layout="wide",
)

# ---------------------------------------------------------
# Dark theme + simple WAVES styling (hard-coded colors)
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #020617 !important;  /* almost black */
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1350px;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #E5E7EB !important;  /* light gray */
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
        margin-bottom: 0.2rem;
    }
    .section-caption {
        font-size: 0.75rem;
        color: #9CA3AF;
        margin-bottom: 0.5rem;
    }
    .sidebar-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Colors for charts (must match CSS but not referenced inside it)
DARK_BG = "#020617"
TEXT_MUTED = "#9CA3AF"
ACCENT_GREEN = "#22C55E"
ACCENT_BLUE = "#38BDF8"
ACCENT_RED = "#F97373"

# ---------------------------------------------------------
# Wave definitions (15 Waves)
# ---------------------------------------------------------
WAVES = {
    "sp500": {
        "label": "S&P 500 Wave (LIVE Demo)",
        "benchmark": "S&P 500 Index",
        "csv_hint": "SP500_PORTFOLIO_FINAL.csv",
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
# Sidebar: control panel (Wave + risk + overrides + upload)
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
        f"<span style='font-size:0.8rem;color:{TEXT_MUTED};'>"
        f"{wave_cfg['wave_type']} • Benchmark: {wave_cfg['benchmark']}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # SmartSafe level
    st.markdown("<div class='sidebar-title'>SmartSafe™ level</div>", unsafe_allow_html=True)
    smartsafe = st.radio(
        "SmartSafe level",
        ["Standard", "Defensive", "Max Safety"],
        index=0,
        label_visibility="collapsed",
    )

    # Risk mode (this is your Alpha / Alpha−Beta / Private Logic switch)
    st.markdown("<div class='sidebar-title'>Risk / alpha mode</div>", unsafe_allow_html=True)
    risk_mode = st.radio(
        "Risk mode",
        ["Standard", "Alpha-minus-Beta", "Private Logic"],
        index=0,
        label_visibility="collapsed",
    )

    # Human overrides – this is your “money manager” panel
    st.markdown("<div class='sidebar-title'>Human overrides (simulated)</div>", unsafe_allow_html=True)
    cash_override = st.slider(
        "Extra SmartSafe™ cash buffer",
        min_value=0,
        max_value=40,
        value=0,
        step=5,
        help="Layers additional cash on top of the Wave’s internal risk engine.",
    )
    tilt = st.slider(
        "Style tilt (Growth  ⟶  Value)",
        min_value=-2,
        max_value=2,
        value=0,
        step=1,
        help="Negative = tilt to Growth names, Positive = tilt to Value/Defensive.",
    )

    st.caption(
        "These controls do **not** change the CSV; they simulate how a human "
        "manager could lean in / de-risk around the AI engine.",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # CSV upload
    st.markdown("<div class='sidebar-title'>Upload latest Wave snapshot (.csv)</div>", unsafe_allow_html=True)
    st.caption(
        "Columns can be loose, but ideally include: "
        "`Ticker`, `Price`, `Dollar_Alloc` (optional: `Weight_pct`, `Index_Weight`). "
        f"Suggested export for this Wave: `{wave_cfg['csv_hint']}`"
    )

    uploaded_file = st.file_uploader(
        "Browse files",
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
    f"<span style='color:{ACCENT_BLUE};font-size:0.8rem;font-weight:500;'>"
    f"AI-Managed Wave • Real-time demo • CSV-driven • No external data calls</span>",
    unsafe_allow_html=True,
)
st.markdown("")

# ---------------------------------------------------------
# Session state initialization for validation
# ---------------------------------------------------------
if "validated" not in st.session_state:
    st.session_state.validated = False
if "last_file_id" not in st.session_state:
    st.session_state.last_file_id = None

# If no CSV yet, just show instructions and stop
if uploaded_file is None:
    st.session_state.validated = False
    st.session_state.last_file_id = None
    st.info(
        "Upload the latest Wave snapshot CSV in the sidebar to render the console. "
        "Use your Google Sheets export for the selected Wave."
    )
    st.stop()

# ---------------------------------------------------------
# Load & normalize data with validation state
# ---------------------------------------------------------
# Create a unique identifier for the uploaded file
current_file_id = (uploaded_file.name, uploaded_file.size)

# Only reprocess if it's a new file
if st.session_state.last_file_id != current_file_id:
    st.session_state.validated = False
    st.session_state.last_file_id = current_file_id

try:
    raw_df = pd.read_csv(uploaded_file)
    if not st.session_state.validated:
        st.session_state.validated = True
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Normalize column names (cached function)
raw_df = normalize_columns(raw_df)

lower_cols = {c.lower(): c for c in raw_df.columns}


def pick_column(*names):
    for n in names:
        key = n.lower()
        if key in lower_cols:
            return lower_cols[key]
    return None


ticker_col = pick_column("ticker", "symbol")
price_col = pick_column("price", "last")
dollar_col = pick_column("dollar_alloc", "dollar_value", "notional")
weight_col = pick_column("weight_pct", "weight", "weight_%")
index_weight_col = pick_column("index_weight", "benchmark_weight", "idx_weight")

missing_requirements = [
    label
    for label, col in [
        ("Ticker", ticker_col),
        ("Price", price_col),
        ("Dollar_Alloc", dollar_col),
    ]
    if col is None
]

if missing_requirements:
    st.error(
        "CSV is missing required columns: "
        + ", ".join(missing_requirements)
        + ". Required: Ticker, Price, Dollar_Alloc. "
        + "Optional: Weight_pct, Index_Weight."
    )
    st.stop()

# Process dataframe using cached function
df = compute_dataframe(raw_df, ticker_col, price_col, dollar_col, weight_col, index_weight_col)

# Validate total NAV
total_nav = df["Dollar_Alloc"].sum()
if total_nav <= 0:
    st.error("Total NAV calculated from Dollar_Alloc is not positive. Check your CSV.")
    st.stop()

num_holdings = df["Ticker"].nunique()
largest_position = df["Weight_pct"].max()
top10_conc = df.nlargest(10, "Weight_pct")["Weight_pct"].sum()

# ---------------------------------------------------------
# Human override math → "current exposure" card
# ---------------------------------------------------------
# Base equity exposure from SmartSafe level
if smartsafe == "Standard":
    base_equity = 1.00  # 100% invested
elif smartsafe == "Defensive":
    base_equity = 0.80
else:  # Max Safety
    base_equity = 0.50

# Risk mode influence – this is more "narrative" than exact
if risk_mode == "Alpha-minus-Beta":
    base_equity *= 0.9
elif risk_mode == "Private Logic":
    base_equity *= 1.05

# Extra SmartSafe cash override
equity_exposure = max(0.0, min(1.0, base_equity - cash_override / 100.0))
cash_exposure = 1.0 - equity_exposure

# Simple text for tilt
if tilt < 0:
    tilt_text = "Leaning to **Growth / leadership** names."
elif tilt > 0:
    tilt_text = "Leaning to **Value / defensive** names."
else:
    tilt_text = "Neutral style tilt — pure Wave engine."

# ---------------------------------------------------------
# Chart helper for dark mode (cached for performance)
# ---------------------------------------------------------
@st.cache_data
def get_chart_config():
    """Return chart configuration dict for reuse."""
    return {
        "background": DARK_BG,
        "axis": {
            "labelColor": TEXT_MUTED,
            "titleColor": TEXT_MUTED,
            "gridColor": "#111827",
        },
        "view": {"strokeOpacity": 0},
        "legend": {
            "labelColor": TEXT_MUTED,
            "titleColor": TEXT_MUTED,
        },
    }

def base_chart(data: pd.DataFrame) -> alt.Chart:
    config = get_chart_config()
    return (
        alt.Chart(data, background=config["background"])
        .configure_axis(**config["axis"])
        .configure_view(**config["view"])
        .configure_legend(**config["legend"])
    )


def ticker_link(ticker: str) -> str:
    url = f"https://www.google.com/search?q={ticker}+stock"
    return f"[{ticker}]({url})"


# ---------------------------------------------------------
# Metric row (NAV / holdings / concentration / exposure)
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
        f"<div class='metric-label'>TOP 10 CONCENTRATION</div>"
        f"<div class='metric-value'>{top10_conc:0.2f}%</div>"
        f"<div class='metric-sub'>Sum of top 10 weights</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='metric-label'>CURRENT EXPOSURE</div>"
        f"<div class='metric-value'>{equity_exposure*100:0.1f}%</div>"
        f"<div class='metric-sub'>Equity • {cash_exposure*100:0.1f}% in SmartSafe™ / cash</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("")

# ---------------------------------------------------------
# First row: Top holdings • Alpha vs Index • Full allocation
# ---------------------------------------------------------
c1, c2, c3 = st.columns([1.1, 1.1, 1.4])

# Left: Top holdings table
with c1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top Holdings</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Sorted by Wave weight. "
        "Tickers link out to live research.</div>",
        unsafe_allow_html=True,
    )

    max_rows = st.slider("Rows", 5, min(50, num_holdings), 20, key="top_rows")
    top_df = df.sort_values("Weight_pct", ascending=False).head(max_rows).copy()

    view = pd.DataFrame(
        {
            "Ticker": [ticker_link(t) for t in top_df["Ticker"]],
            "Price": top_df["Price"].round(2),
            "Dollar_Alloc": top_df["Dollar_Alloc"].round(0),
            "Weight_%": top_df["Weight_pct"].round(3),
        }
    )
    st.markdown(view.to_markdown(index=False), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Middle: Alpha vs index
with c2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Allocation Alpha vs Index</div>", unsafe_allow_html=True)

    if "Index_Weight" not in df.columns:
        st.markdown(
            "<div class='section-caption'>Add an `Index_Weight` column to your CSV "
            "to unlock overweight / underweight vs benchmark.</div>",
            unsafe_allow_html=True,
        )
        st.info("`Index_Weight` not found in CSV. Skipping alpha chart.")
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
                    alt.value(ACCENT_GREEN),
                    alt.value(ACCENT_RED),
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

# Right: Full allocation
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
        .mark_bar(color=ACCENT_BLUE)
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
# Second row: Top 10 chart • Alpha heatmap • Largest positions table
# ---------------------------------------------------------
c4, c5, c6 = st.columns([1, 1.2, 1])

with c4:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top 10 by Weight</div>", unsafe_allow_html=True)

    top10 = df.sort_values("Weight_pct", ascending=False).head(10)
    top10_chart = (
        base_chart(top10)
        .mark_bar(color=ACCENT_GREEN)
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

with c5:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Alpha Heatmap (Top 50)</div>", unsafe_allow_html=True)

    if "Index_Weight" not in df.columns:
        st.markdown(
            "<div class='section-caption'>Provide `Index_Weight` in your CSV to see "
            "active weight heatmap.</div>",
            unsafe_allow_html=True,
        )
        st.info("`Index_Weight` not found in CSV. Skipping heatmap.")
    else:
        st.markdown(
            "<div class='section-caption'>Sorted by absolute active weight (over / under the index).</div>",
            unsafe_allow_html=True,
        )
        alpha_df = df.copy()
        alpha_df["Active_pct"] = alpha_df["Weight_pct"] - alpha_df["Index_Weight"]
        heat_df = alpha_df.reindex(
            alpha_df["Active_pct"].abs().sort_values(ascending=False).head(50).index
        )

        heat_chart = (
            base_chart(heat_df)
            .mark_bar()
            .encode(
                x=alt.X("Ticker:N", sort=None, title=None),
                y=alt.Y(
                    "Active_pct:Q",
                    title="Active vs Index",
                    axis=alt.Axis(format=".1f"),
                ),
                color=alt.condition(
                    "datum.Active_pct >= 0",
                    alt.value(ACCENT_GREEN),
                    alt.value(ACCENT_RED),
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

with c6:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Largest Positions (Table)</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Top 20 holdings by % weight. "
        "Click tickers for more detail.</div>",
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
# Exposure narrative / overrides explanation (for Franklin)
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div class='section-title'>AI engine + human override narrative</div>",
    unsafe_allow_html=True,
)
st.markdown(
    f"- **Risk mode:** `{risk_mode}`  •  **SmartSafe™:** `{smartsafe}`  •  "
    f"**Extra cash override:** `{cash_override}%`  \n"
    f"- Implied equity exposure: **{equity_exposure*100:0.1f}%**  •  "
    f"SmartSafe™ / cash: **{cash_exposure*100:0.1f}%**  \n"
    f"- {tilt_text}",
    unsafe_allow_html=True,
)

st.caption(
    "Upload-based demo • Data source: Wave CSV exports • "
    "WAVES Intelligence™ • Internal demo only (not investment advice)."
)