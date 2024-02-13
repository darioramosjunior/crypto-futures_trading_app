import requests
import threading


class OIValues:
    """
    This class provides methods to retrieve and analyze the open interest data for a list of cryptocurrencies.
    """

    def __init__(self):
        """
        Initialize the class attributes.
        """
        self.top_oi = {}
        self.oi_values = {}
        self.coin_list = []
        self.price_coin_url = "https://fapi.binance.com/fapi/v1/ticker/price"
        self.base_url = "https://fapi.binance.com"
        self.oi_end_point = "/futures/data/openInterestHist"
        self.oi_change = 0

    def get_coin_list(self):
        """
        Retrieve the list of cryptocurrencies available on the Binance exchange.

        Returns:
            A list of cryptocurrency symbols.
        """
        response_local = requests.get(self.price_coin_url)
        data_local = response_local.json()
        self.coin_list = [each['symbol'] for each in data_local]
        # return self.coin_list

    def get_oi_values_thread(self, coin, period='5m', limit=12):
        """
        Retrieve the open interest data for a specific cryptocurrency.

        Args:
            coin (str): The symbol of the cryptocurrency.
            period (str, optional): The time interval for the data. Defaults to '5m'.
            limit (int, optional): The number of data points to retrieve. Defaults to 12.

        Returns:
            None.
        """
        params = {
            'symbol': coin,
            'period': period,
            'limit': limit
        }
        response = requests.get(self.base_url + self.oi_end_point, params=params)
        if response.status_code == 200:
            data = response.json()

            if data:
                oi_values = [float(each['sumOpenInterestValue']) for each in data]
                latest_oi = oi_values[-1]
                lowest_oi_past_hr = min(oi_values)

                oi_difference = (latest_oi - lowest_oi_past_hr)
                oi_change_rate = (oi_difference / lowest_oi_past_hr)
                oi_change_percent = oi_change_rate * 100
                self.top_oi[coin] = oi_change_percent
                self.oi_values[coin] = {"OI": latest_oi, "OI_change": oi_difference, "OI_change_rate": oi_change_percent}
            else:
                pass
        else:
            print(f"Error: {response.status_code}, {response.text}")

    def get_oi_values(self, period, limit):
        """
        Retrieve the open interest data for a list of cryptocurrencies in parallel.

        Args:
            period (str): The time interval for the data.
            limit (int): The number of data points to retrieve.

        Returns:
            None.
        """
        threads = []
        for coin in self.coin_list:
            thread = threading.Thread(target=self.get_oi_values_thread, args=(coin, period, limit))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def get_sorted_top_oi(self):
        """
        Sort the open interest data by change in open interest and return the top coins.

        Returns:
            A dictionary of cryptocurrencies and their change in open interest.
        """
        raw_oi_dict = self.top_oi
        return dict(sorted(raw_oi_dict.items(), key=lambda item: item[1], reverse=True))

    def get_top_oi_values(self, top_oi_coins):
        """
        Retrieve the open interest data for the top coins.

        Args:
            top_oi_coins (list): A list of cryptocurrency symbols.

        Returns:
            A dictionary of cryptocurrencies and their open interest data.
        """
        top_oi_values = {}
        for coin in top_oi_coins:
            top_oi_values[coin] = self.oi_values[coin]
        return top_oi_values

