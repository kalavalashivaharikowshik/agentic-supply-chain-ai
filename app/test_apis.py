from api_connectors.weather_api import WeatherAPI
from api_connectors.shipping_api import ShippingAPI


def test():

    weather = WeatherAPI()
    data = weather.get_weather(31.2304, 121.4737)

    print("Weather Data:")
    print(data)

    shipping = ShippingAPI()
    shipment = shipping.get_shipment_status(101)

    print("\nShipment Status:")
    print(shipment)


if __name__ == "__main__":
    test()