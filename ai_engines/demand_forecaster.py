# demand_forecaster.py
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Forecasts future demand for fashion styles and travel
# destinations using Facebook Prophet time-series model.
# Run: python demand_forecaster.py
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

import pandas as pd
import numpy as np
from prophet import Prophet
from loguru import logger


def prepare_prophet_df(series):
    """Convert a Pandas Series into Prophet format (columns: ds, y)."""
    df = series.reset_index()
    df.columns = ["ds", "y"]
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"]  = pd.to_numeric(df["y"], errors="coerce")
    return df.dropna()


def forecast_trend(series, periods=30, freq="W"):
    """
    Forecast the future trend of a keyword or destination.

    Args:
        series:  Pandas Series with datetime index and values 0-100.
        periods: Number of future periods to predict.
        freq:    "D" daily, "W" weekly, "M" monthly.

    Returns:
        DataFrame with columns: ds, yhat, yhat_lower, yhat_upper, trend
    """
    df = prepare_prophet_df(series)

    model = Prophet(
        yearly_seasonality        = True,
        weekly_seasonality        = (freq in ["D", "W"]),
        daily_seasonality         = False,
        changepoint_prior_scale   = 0.3,
        seasonality_prior_scale   = 10.0,
        interval_width            = 0.8,
        uncertainty_samples       = 500,
    )
    model.add_country_holidays(country_name="IN")
    model.fit(df)

    future   = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    forecast["yhat"]       = forecast["yhat"].clip(0, 100)
    forecast["yhat_lower"] = forecast["yhat_lower"].clip(0, 100)
    forecast["yhat_upper"] = forecast["yhat_upper"].clip(0, 100)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "trend", "trend_lower", "trend_upper"]]


def get_trend_direction(forecast_df, future_weeks=4):
    """
    Summarise whether a trend is rising, falling, or stable.
    Returns direction, change %, current score, future score, peak date.
    """
    now_row    = forecast_df.iloc[-future_weeks - 1]
    future_row = forecast_df.iloc[-1]

    current  = round(float(now_row["yhat"]), 1)
    future   = round(float(future_row["yhat"]), 1)
    change   = round(((future - current) / max(current, 1)) * 100, 1)

    direction = "rising" if change > 5 else ("falling" if change < -5 else "stable")
    peak_idx  = forecast_df["yhat"].idxmax()
    peak_date = str(forecast_df.loc[peak_idx, "ds"].date())

    return {
        "direction":     direction,
        "change_pct":    change,
        "current_score": current,
        "future_score":  future,
        "peak_date":     peak_date,
    }


def rank_trends(keyword_series, periods=4):
    """
    Rank multiple keywords by predicted growth over N periods.
    Returns DataFrame sorted by forecasted growth.
    """
    rows = []
    for keyword, series in keyword_series.items():
        try:
            forecast = forecast_trend(series, periods=periods)
            info     = get_trend_direction(forecast, future_weeks=periods)
            rows.append({"keyword": keyword, **info})
        except Exception as e:
            logger.error(f"Forecast failed for '{keyword}': {e}")

    df = pd.DataFrame(rows).sort_values("change_pct", ascending=False)
    return df.reset_index(drop=True)


def generate_sample_series(keyword, n_weeks=52):
    """Generate a realistic synthetic time-series for testing."""
    np.random.seed(abs(hash(keyword)) % 2**31)
    dates  = pd.date_range(end=pd.Timestamp.today(), periods=n_weeks, freq="W")
    trend  = np.linspace(30, 60, n_weeks)
    season = 20 * np.sin(np.linspace(0, 4 * np.pi, n_weeks))
    noise  = np.random.normal(0, 5, n_weeks)
    return pd.Series(np.clip(trend + season + noise, 0, 100), index=dates)


if __name__ == "__main__":
    logger.info("Testing demand forecaster ...")

    keywords = ["boho style", "Goa trip", "minimalist fashion", "Bali travel"]
    keyword_series = {kw: generate_sample_series(kw) for kw in keywords}

    print("\nâ”€â”€ Trend ranking (next 4 weeks) â”€â”€")
    ranking = rank_trends(keyword_series, periods=4)
    print(ranking.to_string(index=False))

    print("\nâ”€â”€ Forecast: 'Goa trip' â”€â”€")
    forecast  = forecast_trend(keyword_series["Goa trip"], periods=8, freq="W")
    direction = get_trend_direction(forecast)
    print(f"  Direction: {direction['direction']} | Change: {direction['change_pct']:+.1f}% | Peak: {direction['peak_date']}")
