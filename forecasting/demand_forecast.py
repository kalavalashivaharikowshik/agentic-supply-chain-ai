from prophet import Prophet
import pandas as pd


class DemandForecast:

    def train_model(self, history):

        df = pd.DataFrame(history)
        df.columns = ["ds", "y"]

        model = Prophet()
        model.fit(df)

        return model


    def predict(self, model, periods=7):

        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        return forecast[["ds", "yhat"]].tail(periods)