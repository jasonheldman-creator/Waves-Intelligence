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
# Dark theme colors (no formatting inside CSS to avoid syntax issues)
# ---------------------------------------------------------
DARK_BG = "#020617"      # almost black
CARD_BG = "#020818"
TEXT_MAIN = "#E5E7EB"
TEXT_MUTED = "#9CA3AF"
ACCENT = "#22C55E"
ACCENT_SOFT = "#38BDF8"
BORDER = "#1F2937"

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
# Helper: ticker → Google search link
# ---------------------------------------------------------
def ticker_link(ticker: str) -> str:
    url = f"https://www.google.com/search?q={ticker}+stock"
    return f"[{ticker}]({url})"

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
        f"<div class='sidebar-title'>Wave type:</div>"
        f"<span style='font-size:0.8rem;color:{TEXT_MUTED};'>{wave_cfg['wave_type']} • "
        f"Benchmark: {wave_cfg['benchmark']}</span>",
        unsafe_allow_html=True,
    )

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
        "(optional: Weight_pct, Index_Weight).",
        unsafe_allow_html=True,
    )

    portfolio_file = st.file_uploader(
        "Upload Wave CSV",
        type=["csv"],
        label_visibility="collapsed",
        key="wave_csv",
    )

    st.markdown("##### Optional: Trade / Activity log (.csv)")
    st.caption(
        "Format: Timestamp, Wave, Ticker, Side, Quantity, Price, (optional Dollar_Amount).",
        unsafe_allow_html=True,
    )
    trade_file = st.file_uploader(
        "Upload trade log",
        type=["csv"],
        label_visibility="collapsed",
        key="trade_log",
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
    "<span style='color:#38BDF8;font-size:0.8rem;font-weight:500;'>"
    "AI-Managed Wave • Real-time demo • CSV-driven • No external data calls</span>",
    unsafe_allow_html=True,
)
st.markdown("")

# ---------------------------------------------------------
# If no portfolio file yet, show instructions
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

# Flexible column picking
lower_cols = {c.lower(): c for c in raw_df.columns}


def pick(*candidates):
    for cand in candidates:
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
    return None


ticker_col = pick("Ticker")
price_col = pick("Price", "Last")
dollar_col = pick("Dollar_Alloc", "DollarAlloc", "Dollar_Value")
weight_col = pick("Weight_pct", "Weight", "Weight_%", "WeightPct")
index_weight_col = pick("Index_Weight", "Benchmark_Weight", "Idx_Weight")

missing_core = []
if ticker_col is None:
    missing_core.append("Ticker")
if price_col is None:
    missing_core.append("Price")
if dollar_col is None:
    missing_core.append("Dollar_Alloc")

if missing_core:
    st.error(
        "CSV is missing required columns: "
        + ", ".join(missing_core)
        + ". Required: Ticker, Price, Dollar_Alloc. Optional: Weight_pct, Index_Weight."
    )
    st.stop()

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

# De-duplicate tickers
group_cols = ["Ticker"]
agg_dict = {"Price": "last", "Dollar_Alloc": "sum"}
if "Weight_pct" in df.columns:
    agg_dict["Weight_pct"] = "sum"
if "Index_Weight" in df.columns:
    agg_dict["Index_Weight"] = "mean"

df = df.groupby(group_cols, as_index=False).agg(agg_dict)

# Recompute weights from Dollar_Alloc
total_nav = df["Dollar_Alloc"].sum()
if total_nav <= 0:
    st.error("Total NAV from Dollar_Alloc is non-positive. Check your CSV.")
    st.stop()

df["Weight_pct"] = df["Dollar_Alloc"] / total_nav * 100.0

num_holdings = df["Ticker"].nunique()
largest_position = df["Weight_pct"].max()
top10_conc = df.nlargest(10, "Weight_pct")["Weight_pct"].sum()

# ---------------------------------------------------------
# Helper: Altair chart with dark styling
# ---------------------------------------------------------
def base_chart(data: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(data, background=DARK_BG)
        .configure_axis(
            labelColor=TEXT_MUTED,
            titleColor=TEXT_MUTED,
            gridColor="#111827",
        )
        .configure_view(strokeOpacity=0)
        .configure_legend(labelColor=TEXT_MUTED, titleColor=TEXT_MUTED)
    )

# ---------------------------------------------------------
# Metric row
# ---------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        "<div class='metric-card'>"
        "<div class='metric-label'>TOTAL NAV</div>"
        f"<div class='metric-value'>${total_nav:,.0f}</div>"
        "<div class='metric-sub'>Snapshot from uploaded CSV</div>"
        "</div>",
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        "<div class='metric-card'>"
        "<div class='metric-label'># OF HOLDINGS</div>"
        f"<div class='metric-value'>{num_holdings:,}</div>"
        "<div class='metric-sub'>Unique securities in this Wave</div>"
        "</div>",
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        "<div class='metric-card'>"
        "<div class='metric-label'>LARGEST POSITION</div>"
        f"<div class='metric-value'>{largest_position:0.2f}%</div>"
        "<div class='metric-sub'>Single-name weight</div>"
        "</div>",
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        "<div class='metric-card'>"
        "<div class='metric-label'>TOP 10 CONCENTRATION</div>"
        f"<div class='metric-value'>{top10_conc:0.2f}%</div>"
        "<div class='metric-sub'>Sum of top 10 weights</div>"
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("")

# ---------------------------------------------------------
# First row: Top holdings + Alpha vs Index + Full allocation
# ---------------------------------------------------------
c1, c2, c3 = st.columns([1.1, 1.1, 1.4])

# ---- Left: Top holdings table ----
with c1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top Holdings</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Sorted by weight in the Wave. "
        "Tickers link out to live research.</div>",
        unsafe_allow_html=True,
    )

    min_rows = 5
    max_rows_allowed = min(50, max(min_rows, num_holdings))
    default_rows = min(20, max_rows_allowed)

    rows = st.slider(
        "Rows",
        min_rows,
        max_rows_allowed,
        default_rows,
        key="top_rows",
    )

    top_df = df.sort_values("Weight_pct", ascending=False).head(rows).copy()
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

# ---- Middle: Allocation Alpha vs Index ----
with c2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-title'>Allocation Alpha vs Index</div>",
        unsafe_allow_html=True,
    )

    if "Index_Weight" not in df.columns:
        st.markdown(
            "<div class='section-caption'>Add an `Index_Weight` column to your CSV "
            "to see overweight / underweight vs benchmark.</div>",
            unsafe_allow_html=True,
        )
        st.info("No `Index_Weight` found in CSV. Skipping alpha chart.")
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

# ---- Right: Full Wave Allocation ----
with c3:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-title'>Full Wave Allocation</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='section-caption'>Each bar is a holding’s % weight in the Wave "
        "(top 150 shown).</div>",
        unsafe_allow_html=True,
    )

    alloc = df.sort_values("Weight_pct", ascending=False).head(150)
    alloc_chart = (
        base_chart(alloc)
        .mark_bar(color=ACCENT_SOFT)
        .encode(
            x=alt.X("Ticker:N", sort=None, title=None),
            y=alt.Y("Weight_pct:Q", title="% of Wave", axis=alt.Axis(format=".1f")),
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
# Second row: Top 10, Alpha heatmap, Largest positions
# ---------------------------------------------------------
c4, c5, c6 = st.columns([1, 1.2, 1])

# ---- Top 10 by weight ----
with c4:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top 10 by Weight</div>", unsafe_allow_html=True)

    top10 = df.sort_values("Weight_pct", ascending=False).head(10)
    top10_chart = (
        base_chart(top10)
        .mark_bar(color=ACCENT)
        .encode(
            x=alt.X("Ticker:N", sort=None, title=None),
            y=alt.Y("Weight_pct:Q", title="Weight (%)", axis=alt.Axis(format=".1f")),
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

# ---- Alpha heatmap ----
with c5:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Alpha Heatmap (Top 50)</div>", unsafe_allow_html=True)

    if "Index_Weight" not in df.columns:
        st.markdown(
            "<div class='section-caption'>Add `Index_Weight` to unlock alpha heatmap.</div>",
            unsafe_allow_html=True,
        )
        st.info("No `Index_Weight` found in CSV. Skipping heatmap.")
    else:
        st.markdown(
            "<div class='section-caption'>Sorted by absolute active weight "
            "(over / under weight).</div>",
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

# ---- Largest positions table ----
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
# Optional: activity / trade log
# ---------------------------------------------------------
if trade_file is not None:
    st.markdown("---")
    st.markdown(
        "<div class='section-title'>Recent Activity / Trade Log</div>",
        unsafe_allow_html=True,
    )

    try:
        trades_raw = pd.read_csv(trade_file)
    except Exception as e:
        st.error(f"Error reading trade log CSV: {e}")
    else:
        trades_raw.columns = [c.strip().replace(" ", "_") for c in trades_raw.columns]
        needed_trade_cols = ["Timestamp", "Wave", "Ticker", "Side", "Quantity", "Price"]
        missing_trades = [c for c in needed_trade_cols if c not in trades_raw.columns]

        if missing_trades:
            st.error(
                "Trade log missing columns: "
                + ", ".join(missing_trades)
                + ". Expected: Timestamp, Wave, Ticker, Side, Quantity, Price "
                "(+ optional Dollar_Amount)."
            )
        else:
            trades = trades_raw.copy()
            trades = trades[trades["Wave"].str.lower() == wave_key.lower()]

            if trades.empty:
                st.info("No trades found in the log for this Wave.")
            else:
                trades["Timestamp"] = pd.to_datetime(trades["Timestamp"], errors="coerce")
                trades["Quantity"] = pd.to_numeric(trades["Quantity"], errors="coerce")
                trades["Price"] = pd.to_numeric(trades["Price"], errors="coerce")

                if "Dollar_Amount" not in trades.columns:
                    trades["Dollar_Amount"] = trades["Quantity"] * trades["Price"]

                trades = trades.dropna(subset=["Timestamp", "Ticker"])
                trades = trades.sort_values("Timestamp", ascending=False)

                recent = trades[
                    trades["Timestamp"] >= trades["Timestamp"].max() - pd.Timedelta(days=30)
                ].copy()

                if not recent.empty:
                    recent["Date"] = recent["Timestamp"].dt.date
                    recent["SignedAmount"] = np.where(
                        recent["Side"].str.upper().isin(["SELL", "TRIM"]),
                        -recent["Dollar_Amount"],
                        recent["Dollar_Amount"],
                    )
                    daily = recent.groupby("Date", as_index=False)["SignedAmount"].sum()

                    flow_chart = (
                        base_chart(daily)
                        .mark_bar()
                        .encode(
                            x=alt.X("Date:T", title=None),
                            y=alt.Y(
                                "SignedAmount:Q",
                                title="Net traded (USD)",
                                axis=alt.Axis(format="$,.0f"),
                            ),
                            color=alt.condition(
                                "datum.SignedAmount >= 0",
                                alt.value(ACCENT),
                                alt.value("#F97373"),
                            ),
                            tooltip=[
                                alt.Tooltip("Date:T"),
                                alt.Tooltip("SignedAmount:Q", title="Net traded", format="$,.0f"),
                            ],
                        )
                        .properties(height=220, title="Net trading flow (last 30 days)")
                    )
                    st.altair_chart(flow_chart, use_container_width=True)

                st.markdown(
                    "<div class='section-caption'>Most recent trades for this Wave.</div>",
                    unsafe_allow_html=True,
                )
                log = trades.head(50).copy()
                log_view = log[
                    ["Timestamp", "Ticker", "Side", "Quantity", "Price", "Dollar_Amount"]
                ]
                log_view["Ticker"] = [ticker_link(t) for t in log_view["Ticker"]]
                st.markdown(log_view.to_markdown(index=False), unsafe_allow_html=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "Upload-based demo • Data source: Wave CSV exports • "
    "WAVES Intelligence™ • Internal demo only (not investment advice)."
)