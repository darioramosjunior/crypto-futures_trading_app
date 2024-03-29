import requests
import threading


class TopGainersLosers:
    """
    This class provides functionality for retrieving the top gainers and losers for a list of cryptocurrencies.
    """

    def __init__(self):
        """
        Initialize the class by setting up the necessary variables and creating empty dictionaries to store the
        price changes and the price values.
        """
        self.coin_list = []
        self.price_coin_url = "https://fapi.binance.com/fapi/v1/ticker/price"
        self.base_url = "https://fapi.binance.com"
        self.kline_endpoint = "/fapi/v1/klines"
        self.up_price_changes = {}
        self.down_price_changes = {}
        self.price_changes = {}

    def get_coin_list(self):
        """
        Retrieve a list of all cryptocurrencies available on Binance and store it in the class variable coin_list.
        """
        response_local = requests.get(self.price_coin_url)
        data_local = response_local.json()
        self.coin_list = [each['symbol'] for each in data_local]

    def get_price_change_percent_thread(self, coin, interval='5m', limit=12):
        """
        Retrieve the price change percent for a specific cryptocurrency and store it in the appropriate dictionary.
        The price change percent is calculated by comparing the current price with the lowest and highest prices
        over a specific time interval.
        """
        params = {
            'symbol': coin,
            'interval': interval,
            'limit': limit
        }

        response = requests.get(self.base_url + self.kline_endpoint, params=params)
        if response.status_code == 200:
            data = response.json()

            # Get only closing prices for the past period (period = interval * limit)
            price_values = [float(each[4]) for each in data]
            current_price = price_values[-1]
            lowest_price = min(price_values)
            max_price = max(price_values)

            up_price_change = ((current_price - lowest_price) / lowest_price) * 100
            down_price_change = ((current_price - max_price) / max_price) * 100

            self.up_price_changes[coin] = up_price_change
            self.down_price_changes[coin] = down_price_change
            self.price_changes[coin] = {"Current_price": current_price, "Up_price_change": up_price_change,
                                        "Down_price_change": down_price_change}

        else:
            print(response.status_code, " - Not accessed")

    def get_price_change_percent(self, interval, limit):
        """
        Retrieve the price change percent for all cryptocurrencies in the class variable coin_list and store them in
        the appropriate dictionaries. This function uses threading to make multiple requests in parallel.
        """
        threads = []
        for coin in self.coin_list:
            thread = threading.Thread(target=self.get_price_change_percent_thread, args=(coin, interval, limit))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def get_sorted_top_gainers(self):
        """
        Sort the dictionary of price changes based on the value and return the top gainers.
        """
        raw_price_change_dict = self.up_price_changes
        top_gainers_dict = dict(sorted(raw_price_change_dict.items(), key=lambda item: item[1], reverse=True))
        return top_gainers_dict

    def get_sorted_top_losers(self):
        """
        Sort the dictionary of price changes based on the value and return the top losers.
        """
        raw_price_change_dict = self.down_price_changes
        top_losers_dict = dict(sorted(raw_price_change_dict.items(), key=lambda item: item[1], reverse=False))
        return top_losers_dict

    def get_price_values(self, coin_list):
        """
        Retrieve the current price for a list of cryptocurrencies and return them in a dictionary.
        """
        top_price_values = {}
        for coin in coin_list:
            top_price_values[coin] = self.price_changes[coin]
        return top_price_values





