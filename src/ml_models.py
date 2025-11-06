import pandas as pd
from prophet import Prophet

def forecast_prices(df: pd.DataFrame, periods: int = 30):
    """
    Forecast future prices using Facebook Prophet.
    Expects df with ['date', 'close'] columns.
    Returns forecast dataframe and fitted model.
    """
    if df.empty or len(df) < 5:
        return pd.DataFrame(), None

    data = df.rename(columns={"date": "ds", "close": "y"})
    model = Prophet(daily_seasonality=True)
    model.fit(data)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast, model
