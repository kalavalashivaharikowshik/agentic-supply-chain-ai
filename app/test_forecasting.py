from forecasting.model_loader import ModelLoader


def run():

    models = ModelLoader().load_models()

    demand_model = models["demand_model"]
    inventory_model = models["inventory_model"]

    sales_history = [100,120,110,130,140]

    predicted_demand = demand_model.forecast_demand(sales_history)

    print("Predicted Demand:", predicted_demand)

    days_left = inventory_model.predict_stockout(1000,100)

    print("Days until stockout:", days_left)


if __name__ == "__main__":
    run()