import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_utils import fetch_market_data, compute_portfolio_value
from src.ml_models import forecast_prices

st.set_page_config(page_title="AI Investment Insights", layout="wide")
st.title("💹 AI-driven Investment Insights Dashboard")

st.markdown("""
Select one or more stock tickers below to visualize their performance, portfolio trend, and AI-based forecasts.
""")

# Sidebar
with st.sidebar:
    st.header("Portfolio Settings")
    tickers_input = st.text_input("Enter tickers (comma separated)", "AAPL, MSFT, TSLA")
    period = st.selectbox("Select time period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    forecast_days = st.slider("Forecast days", 7, 60, 30)
    st.info("Example: `AAPL, MSFT, TSLA`")

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# Fetch data
if tickers:
    with st.spinner("Fetching market data..."):
        df = fetch_market_data(tickers, period)
        portfolio_df = compute_portfolio_value(df)

    if not df.empty:
        tab1, tab2, tab3 = st.tabs(["📈 Individual Stocks", "💼 Portfolio Overview", "🤖 AI Forecasting"])

        # --- Tab 1: Individual Stocks ---
        with tab1:
            fig = px.line(df, x="date", y="close", color="ticker", title="Stock Price Performance")
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, width='stretch', key="stock_chart")

        # --- Tab 2: Portfolio Overview ---
        with tab2:
            st.subheader("Equal-weighted Portfolio Value")
            fig2 = px.line(portfolio_df, x="date", y="portfolio_value", title="Portfolio Trend")
            st.plotly_chart(fig2, width='stretch', key="portfolio_chart")

            col1, col2 = st.columns(2)
            with col1:
                current_val = portfolio_df["portfolio_value"].iloc[-1]
                st.metric("Current Portfolio Value", f"${current_val:,.2f}")
            with col2:
                ret = (current_val / portfolio_df["portfolio_value"].iloc[0] - 1) * 100
                st.metric("Return", f"{ret:.2f}%")

        # --- Tab 3: Forecasting ---
        with tab3:
            st.subheader(f"Forecasting next {forecast_days} days for {tickers[0]}")
            stock_df = df[df["ticker"] == tickers[0]][["date", "close"]]
            forecast, model = forecast_prices(stock_df, periods=forecast_days)

            if not forecast.empty:
                fig3 = px.line(
                    forecast,
                    x="ds",
                    y=["yhat", "yhat_lower", "yhat_upper"],
                    title=f"{tickers[0]} — Forecasted Price Trend",
                    labels={"value": "Price ($)", "ds": "Date"},
                )
                st.plotly_chart(fig3, width='stretch', key="forecast_chart")

                future_val = forecast["yhat"].iloc[-1]
                gain_loss = (future_val / stock_df["close"].iloc[-1] - 1) * 100

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Forecasted Price", f"${future_val:,.2f}")
                with col2:
                    st.metric("Expected Change", f"{gain_loss:.2f}%", delta=f"{gain_loss:.2f}%")

            else:
                st.warning("Insufficient data for forecasting.")

    else:
        st.warning("No data fetched. Please check tickers or period.")
else:
    st.info("Enter tickers in the sidebar to begin.")
