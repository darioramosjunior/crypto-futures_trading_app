import requests

URL = "https://fapi.binance.com/fapi/v1/ticker/price"


def get_coins_data(url=URL):
    response = requests.get(url)
    content = response.json()
    return content
