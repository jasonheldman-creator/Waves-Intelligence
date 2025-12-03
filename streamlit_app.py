# --- OPTIONAL: Trade / Activity log upload (same for all Waves) ---
st.sidebar.markdown("##### Optional: Trade / Activity Log (.csv)")
trade_file = st.sidebar.file_uploader(
    "Upload trade log",
    type=["csv"],
    key="trade_log",
    label_visibility="collapsed",
)
# ---------------------------------------------------------
# Optional: Activity / Trade log for this Wave
# ---------------------------------------------------------
if trade_file is not None:
    st.markdown("---")
    st.markdown(
        '<div class="section-title">Recent Activity / Trade Log</div>',
        unsafe_allow_html=True,
    )

    try:
        trades_raw = pd.read_csv(trade_file)
    except Exception as e:
        st.error(f"Error reading trade log CSV: {e}")
    else:
        # Normalize column names
        trades_raw.columns = [c.strip().replace(" ", "_") for c in trades_raw.columns]

        needed_trade_cols = ["Timestamp", "Wave", "Ticker", "Side", "Quantity", "Price"]
        missing_trades = [c for c in needed_trade_cols if c not in trades_raw.columns]

        if missing_trades:
            st.error(
                "Trade log missing columns: "
                + ", ".join(missing_trades)
                + "<br>Expected: Timestamp, Wave, Ticker, Side, Quantity, Price (+ optional Dollar_Amount).",
                icon="⚠️",
            )
        else:
            trades = trades_raw.copy()

            # Filter to current Wave key (e.g. 'sp500', 'us_growth', etc.)
            trades = trades[trades["Wave"].str.lower() == wave_key.lower()]

            if trades.empty:
                st.info("No trades found in the log for this Wave.")
            else:
                # Make sure types look sane
                trades["Timestamp"] = pd.to_datetime(
                    trades["Timestamp"], errors="coerce"
                )
                trades["Quantity"] = pd.to_numeric(
                    trades["Quantity"], errors="coerce"
                )
                trades["Price"] = pd.to_numeric(trades["Price"], errors="coerce")

                if "Dollar_Amount" not in trades.columns:
                    trades["Dollar_Amount"] = trades["Quantity"] * trades["Price"]

                trades = trades.dropna(subset=["Timestamp", "Ticker"])

                # Sort newest first
                trades = trades.sort_values("Timestamp", ascending=False)

                # High-level turnover chart (last 30 days)
                recent = trades[
                    trades["Timestamp"]
                    >= (trades["Timestamp"].max() - pd.Timedelta(days=30))
                ]
                recent_daily = (
                    recent.assign(
                        Date=recent["Timestamp"].dt.date,
                        SignedAmount=np.where(
                            recent["Side"].str.upper().isin(["SELL", "TRIM"]),
                            -recent["Dollar_Amount"],
                            recent["Dollar_Amount"],
                        ),
                    )
                    .groupby("Date", as_index=False)["SignedAmount"]
                    .sum()
                )

                if not recent_daily.empty:
                    turnover_chart = (
                        alt.Chart(recent_daily)
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
                                alt.value("#22C55E"),
                                alt.value("#F97373"),
                            ),
                            tooltip=[
                                alt.Tooltip("Date:T"),
                                alt.Tooltip(
                                    "SignedAmount:Q",
                                    title="Net traded",
                                    format="$,.