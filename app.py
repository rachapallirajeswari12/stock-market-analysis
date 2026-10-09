
import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Stock Market Analysis | Rajeswari",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM STYLE: TITLE BAR, NAVIGATION, FOOTER
# --------------------------------------------------
st.markdown("""
<style>
.main-title {
    background: linear-gradient(90deg, #123456, #167D9A);
    color: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 12px;
}
.main-title h1 {
    color: white;
    margin: 0;
    font-size: 34px;
}
.main-title p {
    color: #EAF6FF;
    margin: 8px 0 0 0;
    font-size: 16px;
}
.section-title {
    color: #167D9A;
    font-size: 23px;
    font-weight: bold;
    padding-bottom: 6px;
    border-bottom: 2px solid #167D9A;
}
.footer {
    text-align: center;
    color: gray;
    padding: 20px;
    margin-top: 30px;
    border-top: 1px solid #DDDDDD;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# STOCK TABLES
# --------------------------------------------------
STOCK_TABLES = {
    "Bajaj Auto": "bajaj_auto",
    "Eicher Motors": "eicher_motors",
    "Hero MotoCorp": "hero_motocorp",
    "Infosys": "infosys",
    "TCS": "tcs",
    "TVS Motors": "tvs_motors"
}

COLUMNS = [
    "date",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "wap",
    "no_of_shares",
    "no_of_trades",
    "total_turnover",
    "deliverable_quantity",
    "delivery_percentage",
    "spread_high_low",
    "spread_close_open"
]

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
def get_connection(host, port, database, username, password):
    return psycopg2.connect(
        host=host,
        port=int(port),
        dbname=database,
        user=username,
        password=password,
        connect_timeout=10
    )


def load_stock_data(connection, table_name):
    column_sql = ", ".join(f'"{column}"' for column in COLUMNS)

    query = f"""
        SELECT {column_sql}
        FROM "{table_name}"
        ORDER BY "date"
    """

    df = pd.read_sql_query(query, connection)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        numeric_columns = [
            col for col in COLUMNS
            if col != "date"
        ]

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["daily_change_pct"] = (
            df["close_price"].pct_change() * 100
        )

        df["signal"] = "HOLD"
        df.loc[
            df["close_price"] > df["open_price"], "signal"
        ] = "BUY"
        df.loc[
            df["close_price"] < df["open_price"], "signal"
        ] = "SELL"

        df["moving_avg_20"] = (
            df["close_price"].rolling(20, min_periods=1).mean()
        )

        df["moving_avg_50"] = (
            df["close_price"].rolling(50, min_periods=1).mean()
        )

    return df


# --------------------------------------------------
# SIDEBAR: BRANDING AND NAVIGATION
# --------------------------------------------------
st.sidebar.title("📊 Stock Analytics")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📈 Stock Analysis",
        "🏢 Company Comparison",
        "🧹 Data Quality",
        "📋 Raw Data"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("Database Connection")

host = st.sidebar.text_input("Host", value="localhost")
port = st.sidebar.text_input("Port", value="5432")
database = st.sidebar.text_input("Database Name", value="postgres")
username = st.sidebar.text_input("Username", value="postgres")
password = st.sidebar.text_input("Password", type="password")

connect_button = st.sidebar.button(
    "Connect to PostgreSQL",
    type="primary",
    use_container_width=True
)

# Store connection status in session
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if "stock_data" not in st.session_state:
    st.session_state.stock_data = {}

if connect_button:
    try:
        connection = get_connection(
            host, port, database, username, password
        )

        loaded_data = {}
        errors = []

        for company, table in STOCK_TABLES.items():
            try:
                loaded_data[company] = load_stock_data(
                    connection, table
                )
            except Exception as error:
                errors.append(f"{company}: {error}")

        connection.close()

        st.session_state.stock_data = loaded_data
        st.session_state.db_connected = len(loaded_data) > 0

        if st.session_state.db_connected:
            st.sidebar.success(
                f"Connected! Loaded {len(loaded_data)} table(s)."
            )

        if errors:
            for error in errors:
                st.sidebar.warning(error)

        if not st.session_state.db_connected:
            st.sidebar.error(
                "No stock tables could be loaded. "
                "Check the database name and table columns."
            )

    except Exception as error:
        st.session_state.db_connected = False
        st.sidebar.error(f"Connection failed: {error}")

# --------------------------------------------------
# MAIN TITLE BAR
# --------------------------------------------------
st.markdown("""
<div class="main-title">
    <h1>📈 Stock Market Analysis Dashboard</h1>
    <p>Historical Stock Prices • Trading Activity • Trend Analysis</p>
    <p>Created by Rajeswari</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Analyze six companies using historical stock market data stored in PostgreSQL."
)

if not st.session_state.db_connected:
    st.info(
        "Please enter your PostgreSQL connection details in the sidebar "
        "and click **Connect to PostgreSQL**."
    )

    st.markdown("### Companies included")
    st.write(
        "Bajaj Auto • Eicher Motors • Hero MotoCorp • "
        "Infosys • TCS • TVS Motors"
    )

    st.markdown("""
    ### Dashboard navigation
    - **Dashboard:** Overall summary and company overview
    - **Stock Analysis:** Price trends, moving averages and daily signals
    - **Company Comparison:** Compare companies using available metrics
    - **Data Quality:** Check missing values and duplicate dates
    - **Raw Data:** View and download imported stock records
    """)

else:
    stock_data = st.session_state.stock_data

    available_companies = [
        company for company, df in stock_data.items()
        if not df.empty
    ]

    if not available_companies:
        st.warning("No stock records are available in the loaded tables.")
    else:
        # --------------------------------------------------
        # GLOBAL FILTERS
        # --------------------------------------------------
        st.sidebar.subheader("Filters")

        selected_company = st.sidebar.selectbox(
            "Select Company",
            available_companies
        )

        selected_df = stock_data[selected_company].copy()
        selected_df = selected_df.dropna(subset=["date"])

        if not selected_df.empty:
            min_date = selected_df["date"].min().date()
            max_date = selected_df["date"].max().date()

            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range
                selected_df = selected_df[
                    (selected_df["date"].dt.date >= start_date) &
                    (selected_df["date"].dt.date <= end_date)
                ]

        # --------------------------------------------------
        # PAGE 1: DASHBOARD
        # --------------------------------------------------
        if page == "🏠 Dashboard":
            st.markdown(
                '<div class="section-title">Market Overview</div>',
                unsafe_allow_html=True
            )

            all_records = sum(len(df) for df in stock_data.values())
            companies_loaded = len(available_companies)

            company_closes = []
            for company, df in stock_data.items():
                valid = df.dropna(subset=["close_price"])
                if not valid.empty:
                    company_closes.append({
                        "Company": company,
                        "Latest Date": valid["date"].max(),
                        "Latest Close": valid.sort_values("date")[
                            "close_price"
                        ].iloc[-1]
                    })

            comparison_df = pd.DataFrame(company_closes)

            col1, col2, col3 = st.columns(3)
            col1.metric("Companies Loaded", companies_loaded)
            col2.metric("Total Records", f"{all_records:,}")
            col3.metric(
                "Selected Company",
                selected_company
            )

            st.subheader(f"{selected_company}: Price Summary")

            if not selected_df.empty:
                valid_close = selected_df.dropna(
                    subset=["close_price"]
                ).sort_values("date")

                if not valid_close.empty:
                    first_close = valid_close["close_price"].iloc[0]
                    last_close = valid_close["close_price"].iloc[-1]

                    change_pct = (
                        ((last_close - first_close) / first_close) * 100
                        if first_close != 0 else 0
                    )

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Latest Close", f"{last_close:,.2f}")
                    c2.metric("Highest Close", f"{valid_close['close_price'].max():,.2f}")
                    c3.metric("Lowest Close", f"{valid_close['close_price'].min():,.2f}")
                    c4.metric("Period Change", f"{change_pct:.2f}%")

                    fig = px.line(
                        valid_close,
                        x="date",
                        y="close_price",
                        title=f"{selected_company} - Closing Price Trend",
                        labels={
                            "date": "Date",
                            "close_price": "Closing Price"
                        }
                    )
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)

            st.subheader("Company Comparison - Latest Available Close")

            if not comparison_df.empty:
                comparison_df["Latest Date"] = (
                    comparison_df["Latest Date"].dt.strftime("%Y-%m-%d")
                )

                fig = px.bar(
                    comparison_df,
                    x="Company",
                    y="Latest Close",
                    color="Company",
                    title="Latest Closing Price by Company",
                    hover_data=["Latest Date"]
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(comparison_df, use_container_width=True)

        # --------------------------------------------------
        # PAGE 2: STOCK ANALYSIS
        # --------------------------------------------------
        elif page == "📈 Stock Analysis":
            st.markdown(
                '<div class="section-title">Individual Stock Analysis</div>',
                unsafe_allow_html=True
            )

            st.subheader(selected_company)

            if selected_df.empty:
                st.warning("No records available for the selected date range.")
            else:
                chart_df = selected_df.sort_values("date").copy()
                chart_df = chart_df.dropna(subset=["close_price"])

                if not chart_df.empty:
                    latest_close = chart_df["close_price"].iloc[-1]
                    highest_close = chart_df["close_price"].max()
                    lowest_close = chart_df["close_price"].min()

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Latest Close", f"{latest_close:,.2f}")
                    c2.metric("Highest Close", f"{highest_close:,.2f}")
                    c3.metric("Lowest Close", f"{lowest_close:,.2f}")

                    st.subheader("Closing Price and Moving Averages")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=chart_df["date"],
                        y=chart_df["close_price"],
                        mode="lines",
                        name="Closing Price"
                    ))
                    fig.add_trace(go.Scatter(
                        x=chart_df["date"],
                        y=chart_df["moving_avg_20"],
                        mode="lines",
                        name="20-Day Moving Average"
                    ))
                    fig.add_trace(go.Scatter(
                        x=chart_df["date"],
                        y=chart_df["moving_avg_50"],
                        mode="lines",
                        name="50-Day Moving Average"
                    ))
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Price",
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Daily BUY / SELL / HOLD Signals")
                    st.caption(
                        "Simple educational rule: Close > Open = BUY, "
                        "Close < Open = SELL, and Close = Open = HOLD. "
                        "These are not investment recommendations."
                    )

                    signal_counts = (
                        chart_df["signal"].value_counts()
                        .reindex(["BUY", "SELL", "HOLD"], fill_value=0)
                        .rename_axis("Signal")
                        .reset_index(name="Number of Days")
                    )

                    fig = px.bar(
                        signal_counts,
                        x="Signal",
                        y="Number of Days",
                        color="Signal",
                        title="Daily Signal Counts"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Daily Percentage Change")
                    fig = px.line(
                        chart_df,
                        x="date",
                        y="daily_change_pct",
                        title="Daily Closing Price Percentage Change",
                        labels={
                            "date": "Date",
                            "daily_change_pct": "Change (%)"
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Trading Activity")
                    activity_metric = st.selectbox(
                        "Choose Trading Metric",
                        [
                            "no_of_shares",
                            "no_of_trades",
                            "total_turnover",
                            "delivery_percentage"
                        ]
                    )

                    fig = px.line(
                        chart_df,
                        x="date",
                        y=activity_metric,
                        title=f"{selected_company} - {activity_metric}",
                        labels={
                            "date": "Date",
                            activity_metric: activity_metric.replace("_", " ").title()
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Year-wise Closing Price")
                    yearly_df = chart_df.dropna(
                        subset=["close_price"]
                    ).copy()
                    yearly_df["Year"] = yearly_df["date"].dt.year

                    yearly_summary = (
                        yearly_df.groupby("Year", as_index=False)
                        .agg(
                            Average_Close=("close_price", "mean"),
                            Maximum_Close=("close_price", "max"),
                            Minimum_Close=("close_price", "min")
                        )
                    )

                    fig = px.line(
                        yearly_summary,
                        x="Year",
                        y="Average_Close",
                        markers=True,
                        title="Average Closing Price by Year"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(yearly_summary, use_container_width=True)

                    csv_data = chart_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download Selected Stock CSV",
                        data=csv_data,
                        file_name=f"{selected_company.lower().replace(' ', '_')}_analysis.csv",
                        mime="text/csv"
                    )

        # --------------------------------------------------
        # PAGE 3: COMPANY COMPARISON
        # --------------------------------------------------
        elif page == "🏢 Company Comparison":
            st.markdown(
                '<div class="section-title">Company Comparison</div>',
                unsafe_allow_html=True
            )

            summary_rows = []

            for company, df in stock_data.items():
                valid = df.dropna(
                    subset=["date", "close_price"]
                ).sort_values("date")

                if valid.empty:
                    continue

                first_close = valid["close_price"].iloc[0]
                last_close = valid["close_price"].iloc[-1]

                period_change = (
                    (last_close - first_close) / first_close * 100
                    if first_close != 0 else None
                )

                summary_rows.append({
                    "Company": company,
                    "Records": len(df),
                    "Start Date": valid["date"].min(),
                    "End Date": valid["date"].max(),
                    "First Close": first_close,
                    "Latest Close": last_close,
                    "Highest Close": valid["close_price"].max(),
                    "Lowest Close": valid["close_price"].min(),
                    "Period Change (%)": period_change,
                    "Average Daily Shares": df["no_of_shares"].mean(),
                    "Average Delivery (%)": df["delivery_percentage"].mean()
                })

            summary_df = pd.DataFrame(summary_rows)

            if not summary_df.empty:
                st.dataframe(
                    summary_df.round(2),
                    use_container_width=True
                )

                comparison_metric = st.selectbox(
                    "Compare Using",
                    [
                        "Latest Close",
                        "Average Daily Shares",
                        "Average Delivery (%)",
                        "Period Change (%)"
                    ]
                )

                fig = px.bar(
                    summary_df,
                    x="Company",
                    y=comparison_metric,
                    color="Company",
                    title=f"Company Comparison: {comparison_metric}"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Closing Price Trends Across Companies")

                trend_frames = []
                for company, df in stock_data.items():
                    temp = df[["date", "close_price"]].copy()
                    temp["Company"] = company
                    trend_frames.append(temp)

                trends = pd.concat(trend_frames, ignore_index=True)
                trends = trends.dropna(
                    subset=["date", "close_price"]
                )

                fig = px.line(
                    trends,
                    x="date",
                    y="close_price",
                    color="Company",
                    title="Historical Closing Prices"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.download_button(
                    "⬇️ Download Company Comparison CSV",
                    data=summary_df.to_csv(index=False).encode("utf-8"),
                    file_name="company_comparison.csv",
                    mime="text/csv"
                )

        # --------------------------------------------------
        # PAGE 4: DATA QUALITY
        # --------------------------------------------------
        elif page == "🧹 Data Quality":
            st.markdown(
                '<div class="section-title">Data Quality Checks</div>',
                unsafe_allow_html=True
            )

            quality_rows = []

            for company, df in stock_data.items():
                quality_rows.append({
                    "Company": company,
                    "Total Rows": len(df),
                    "Duplicate Dates": int(
                        df["date"].duplicated().sum()
                    ) if "date" in df.columns else None,
                    "Missing Dates": int(df["date"].isna().sum()),
                    "Missing Close Prices": int(
                        df["close_price"].isna().sum()
                    ),
                    "Missing Open Prices": int(
                        df["open_price"].isna().sum()
                    ),
                    "Missing Share Counts": int(
                        df["no_of_shares"].isna().sum()
                    ),
                    "Zero or Negative Close": int(
                        (df["close_price"] <= 0).sum()
                    ),
                    "Negative Area not applicable": "N/A"
                })

            quality_df = pd.DataFrame(quality_rows)

            st.dataframe(quality_df, use_container_width=True)

            st.subheader(f"Inspect {selected_company}")

            if not selected_df.empty:
                missing_df = (
                    selected_df.isna().sum()
                    .rename("Missing Values")
                    .reset_index()
                    .rename(columns={"index": "Column"})
                )

                fig = px.bar(
                    missing_df,
                    x="Column",
                    y="Missing Values",
                    title="Missing Values by Column"
                )
                st.plotly_chart(fig, use_container_width=True)

                duplicate_rows = selected_df[
                    selected_df["date"].duplicated(keep=False)
                ]

                st.write("Duplicate-date records:")
                if duplicate_rows.empty:
                    st.success("No duplicate dates found in the filtered records.")
                else:
                    st.dataframe(
                        duplicate_rows,
                        use_container_width=True
                    )

                invalid_close = selected_df[
                    selected_df["close_price"] <= 0
                ]

                st.write("Zero or negative closing prices:")
                if invalid_close.empty:
                    st.success("No zero or negative closing prices found.")
                else:
                    st.dataframe(
                        invalid_close,
                        use_container_width=True
                    )

        # --------------------------------------------------
        # PAGE 5: RAW DATA
        # --------------------------------------------------
        elif page == "📋 Raw Data":
            st.markdown(
                '<div class="section-title">Stock Market Raw Data</div>',
                unsafe_allow_html=True
            )

            st.write(f"Selected company: **{selected_company}**")

            if selected_df.empty:
                st.warning("No data is available for the selected filters.")
            else:
                st.write(f"Rows shown: {len(selected_df):,}")
                st.dataframe(
                    selected_df,
                    use_container_width=True,
                    height=500
                )

                st.download_button(
                    "⬇️ Download Raw Data CSV",
                    data=selected_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"{selected_company.lower().replace(' ', '_')}_raw_data.csv",
                    mime="text/csv"
                )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("""
<div class="footer">
    <strong>Stock Market Analysis Dashboard</strong><br>
    Created by Rachapalli Rajeswari<br>
    PostgreSQL • Python • Streamlit • Plotly
</div>
""", unsafe_allow_html=True)