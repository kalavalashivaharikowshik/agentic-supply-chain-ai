"""Demand forecasting.

Uses Facebook Prophet when it is installed and there is enough history;
otherwise falls back to a least-squares linear trend, so forecasts always work.
"""

from __future__ import annotations

from typing import List, Sequence

import numpy as np
import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)

try:  # Prophet is optional (heavy dependency)
    from prophet import Prophet  # type: ignore

    HAS_PROPHET = True
except Exception:  # pragma: no cover
    HAS_PROPHET = False

MIN_PROPHET_POINTS = 14


class DemandForecast:
    def train_model(self, history):
        """Train Prophet on ``[(date, value), ...]`` or a DataFrame with ds/y columns."""
        if not HAS_PROPHET:
            raise RuntimeError("prophet is not installed; use forecast_demand() instead")
        df = pd.DataFrame(history)
        df.columns = ["ds", "y"]
        model = Prophet(daily_seasonality=False, weekly_seasonality=len(df) >= 14)
        model.fit(df)
        return model

    def predict(self, model, periods: int = 7) -> pd.DataFrame:
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return forecast[["ds", "yhat"]].tail(periods)

    @staticmethod
    def linear_forecast(values: Sequence[float], periods: int = 7) -> List[float]:
        y = np.asarray(values, dtype=float)
        if len(y) == 0:
            return [0.0] * periods
        if len(y) == 1:
            return [float(y[0])] * periods
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        future_x = np.arange(len(y), len(y) + periods)
        return [round(max(0.0, float(v)), 2) for v in slope * future_x + intercept]

    def forecast_demand(self, sales_history: Sequence[float], periods: int = 7) -> List[float]:
        """Forecast the next ``periods`` values of a daily demand series."""
        if HAS_PROPHET and len(sales_history) >= MIN_PROPHET_POINTS:
            try:
                dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=len(sales_history))
                model = self.train_model(list(zip(dates, sales_history)))
                preds = self.predict(model, periods)["yhat"].tolist()
                return [round(max(0.0, float(v)), 2) for v in preds]
            except Exception as exc:  # pragma: no cover
                logger.warning("Prophet failed (%s); using linear trend", exc)
        return self.linear_forecast(sales_history, periods)
