import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_market_data(tickers: list, period: str = "6mo") -> pd.DataFrame:
    """
    Fetch adjusted close prices for given tickers.
    Returns long-format DataFrame: date, ticker, close.
    """
    if not tickers:
        return pd.DataFrame()

    data = yf.download(tickers, period=period, interval="1d", auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]
    data = data.reset_index()
    df = data.melt(id_vars=["Date"], var_name="Ticker", value_name="Close")
    df = df.rename(columns={"Date": "date", "Ticker": "ticker", "Close": "close"})
    df = df.dropna()
    return df

def compute_portfolio_value(df: pd.DataFrame) -> pd.DataFrame:
    """Assumes equal weight across tickers."""
    if df.empty:
        return df
    pivot = df.pivot(index="date", columns="ticker", values="close")
    portfolio = pivot.mean(axis=1)
    result = pd.DataFrame({"date": portfolio.index, "portfolio_value": portfolio.values})
    return result
