import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="WAVES Intelligence™ — S&P 500 Wave",
    layout="wide",
)

st.markdown(
    "<h2 style='color:#00FFA7;margin-bottom:0'>WAVES INTELLIGENCE™</h2>"
    "<h4 style='color:#CCCCCC;margin-top:2px'>S&P 500 Wave — Live Portfolio Console</h4>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------- CSV UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload SP500_PORTFOLIO_FINAL.csv",
    type=["csv"],
    help="Export the latest S&P 500 Wave snapshot from Google Sheets as CSV, then upload it here."
)

if uploaded_file is None:
    st.info("👆 Upload your SP500_PORTFOLIO_FINAL.csv to see the dashboard.")
    st.stop()

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV: {e}")
    st.stop()

# Normalize column names
df.columns = [c.strip() for c in df.columns]

# Try to map your expected columns
# Adjust these names if your CSV uses slightly different headers
candidate_columns = {
    "ticker": ["Ticker", "ticker", "Symbol", "symbol"],
    "price": ["Price", "price", "Last", "Close"],
    "value": ["Dollar_Alloc", "Dollar Alloc", "Value", "Position_Value", "Total_Value"],
}

def find_col(possible):
    for name in possible:
        if name in df.columns:
            return name
    return None

ticker_col = find_col(candidate_columns["ticker"])
price_col = find_col(candidate_columns["price"])
value_col = find_col(candidate_columns["value"])

missing = []
if ticker_col is None:
    missing.append("Ticker")
if price_col is None:
    missing.append("Price")
if value_col is None:
    missing.append("Dollar_Alloc / Value")

if missing:
    st.error(
        "Missing one or more required columns in the uploaded CSV:<br>"
        + ", ".join(missing)
        + "<br><br>Found columns: "
        + ", ".join(df.columns),
        icon="⚠️",
    )
    st.stop()

# Clean + compute weights
df = df[[ticker_col, price_col, value_col]].copy()
df.columns = ["Ticker", "Price", "Dollar_Alloc"]

df["Dollar_Alloc"] = pd.to_numeric(df["Dollar_Alloc"], errors="coerce").fillna(0.0)
total_nav = df["Dollar_Alloc"].sum()

if total_nav <= 0:
    st.error("Total NAV from Dollar_Alloc is zero or negative.")
    st.stop()

df["Weight_pct"] = df["Dollar_Alloc"] / total_nav * 100.0
df = df.sort_values("Dollar_Alloc", ascending=False).reset_index(drop=True)

# ---------------- KPI ROW ----------------
def fmt_money(x):
    try:
        return f"${x:,.0f}"
    except Exception:
        return "-"

num_holdings = len(df)
largest_weight = float(df["Weight_pct"].max())
top10_nav = float(df.head(10)["Dollar_Alloc"].sum())
top10_conc = top10_nav / total_nav * 100.0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total NAV", fmt_money(total_nav))
with k2:
    st.metric("# of Holdings", f"{num_holdings}")
with k3:
    st.metric("Largest Position", f"{largest_weight:0.2f}%")
with k4:
    st.metric("Top 10 Concentration", f"{top10_conc:0.2f}%")

st.markdown("---")

# ---------------- MAIN BLOOMBERG-STYLE LAYOUT ----------------
left, mid, right = st.columns([1.3, 1.0, 1.0])

# ---- Left: Top holdings table ----
with left:
    st.markdown("#### Top Holdings")
    top_n = st.slider("Rows", min_value=10, max_value=50, value=20, step=5)
    top = df.head(top_n).copy()

    show_df = top[["Ticker", "Price", "Dollar_Alloc", "Weight_pct"]].copy()
    show_df["Dollar_Alloc"] = show_df["Dollar_Alloc"].map(fmt_money)
    show_df["Weight_pct"] = show_df["Weight_pct"].map(lambda x: f"{x:0.2f}%")

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True,
        height=480,
    )

# ---- Middle: Top 10 weights + buckets ----
with mid:
    st.markdown("#### Top 10 by Weight")
    bar_data = df.head(10)[["Ticker", "Weight_pct"]].set_index("Ticker")
    st.bar_chart(bar_data, use_container_width=True)

    st.markdown("#### Weight Buckets")
    core = df[df["Weight_pct"] >= 2.0]["Weight_pct"].sum()
    satellite = df[(df["Weight_pct"] >= 0.5) & (df["Weight_pct"] < 2.0)]["Weight_pct"].sum()
    micro = df[df["Weight_pct"] < 0.5]["Weight_pct"].sum()

    bucket_df = pd.DataFrame(
        {
            "Bucket": ["Core (≥ 2%)", "Satellite (0.5–2%)", "Micro (< 0.5%)"],
            "Weight_pct": [core, satellite, micro],
        }
    ).set_index("Bucket")

    st.bar_chart(bucket_df, use_container_width=True)

# ---- Right: Full-wave allocation ----
with right:
    st.markdown("#### Full Wave Allocation")
    st.caption("Each bar is a holding’s % weight in the S&P 500 Wave.")
    all_weights = df[["Ticker", "Weight_pct"]].set_index("Ticker")
    st.bar_chart(all_weights, use_container_width=True)

    st.markdown("#### Largest Positions (Table)")
    st.dataframe(
        df.head(10)[["Ticker", "Weight_pct"]],
        use_container_width=True,
        hide_index=True,
        height=260,
    )

st.markdown("---")
st.caption(
    "Upload-based view • Data source: SP500_PORTFOLIO_FINAL.csv • "
    "WAVES Intelligence™ • Internal demo (not investment advice)."
)
