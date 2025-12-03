import streamlit as st
import pandas as pd
import numpy as np

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="WAVES Intelligence™ — S&P 500 Wave Console",
    layout="wide"
)

# ------------------ HEADER ------------------ #
st.markdown(
    """
    <h1 style="color:#00FFA7;margin-bottom:0;">WAVES INTELLIGENCE™</h1>
    <h3 style="color:#CCCCCC;margin-top:4px;">S&P 500 Wave — Live Portfolio Console</h3>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ------------------ FILE UPLOAD ------------------ #
uploaded_file = st.file_uploader(
    "Upload SP500_PORTFOLIO_FINAL.csv",
    type="csv",
    help="Export the latest S&P 500 Wave snapshot from Google Sheets as CSV, then upload it here."
)

if uploaded_file is None:
    st.info("👆 Upload your **SP500_PORTFOLIO_FINAL.csv** to see the dashboard.")
    st.stop()

# ------------------ LOAD DATA ------------------ #
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

# ------------------ CORE METRICS ------------------ #
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

# ------------------ INDEX VS WAVE ("ALPHA") ------------------ #
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

# ------------------ TOP KPI STRIP ------------------ #
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total NAV", f"${total_nav:,.0f}")

with kpi2:
    st.metric("# of Holdings", f"{num_holdings:,}")

with kpi3:
    st.metric("Largest Position", f"{largest_weight:.2f}%")

with kpi4:
    st.metric("Top 10 Concentration", f"{top10_conc:.2f}%")

st.markdown("---")

# ------------------ LAYOUT: 3 COLUMNS ------------------ #
left, mid, right = st.columns([1.4, 1.4, 1.8])

# ---------- LEFT: TOP HOLDINGS TABLE ---------- #
with left:
    st.markdown("### Top Holdings")

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
        height=400,
    )

# ---------- MIDDLE: ALPHA + TOP 10 + BUCKETS ---------- #
with mid:
    # Allocation Alpha first
    st.markdown("### Allocation Alpha vs S&P 500 Index")
    if has_alpha and df["Active_Weight_pct"].abs().sum() > 0:
        alpha_df = (
            df[["Ticker", "Active_Weight_pct"]]
            .sort_values("Active_Weight_pct", key=lambda s: s.abs(), ascending=False)
            .head(15)
            .set_index("Ticker")
        )
        st.caption("Positive bars = overweight vs index. Negative bars = underweight.")
        st.bar_chart(alpha_df, use_container_width=True, height=260)
    else:
        st.info("Index_Weight column not found in CSV, so allocation alpha cannot be computed.")

    st.markdown("### Top 10 by Weight")
    top10 = df.head(10)[["Ticker", "Weight_pct"]].set_index("Ticker")
    st.bar_chart(top10, use_container_width=True, height=260)

    st.markdown("### Weight Buckets")
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
    st.markdown("### Full Wave Allocation")
    st.caption("Each bar is a holding’s % weight in the S&P 500 Wave (top 150 shown).")

    max_full = min(150, len(df))
    full_df = df.head(max_full)[["Ticker", "Weight_pct"]].set_index("Ticker")
    st.bar_chart(full_df, use_container_width=True, height=280)

    st.markdown("### Largest Positions (Table)")
    largest_df = df.head(15)[["Ticker", "Weight_pct"]].copy()
    largest_df["Weight_pct"] = largest_df["Weight_pct"].map(lambda x: f"{x:.2f}%")
    st.dataframe(
        largest_df.set_index("Ticker"),
        use_container_width=True,
        height=260,
    )

# ------------------ FOOTER / DISCLAIMER ------------------ #
st.markdown("---")
st.caption(
    """
    • Data source: **SP500_PORTFOLIO_FINAL.csv** (Google Sheets export).  
    • All weights are recomputed from *Dollar_Alloc* at upload time.  
    • “Allocation Alpha” = Wave portfolio weight minus S&P 500 index weight (Index_Weight).  
    • WAVES Intelligence™ — Internal demo console only (not investment advice).
    """
)
