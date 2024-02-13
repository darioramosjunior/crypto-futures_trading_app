import requests
import threading


class OIValues:
    def __init__(self):
        self.top_oi = {}
        self.oi_values = {}
        self.coin_list = []
        self.price_coin_url = "https://fapi.binance.com/fapi/v1/ticker/price"
        self.base_url = "https://fapi.binance.com"
        self.oi_end_point = "/futures/data/openInterestHist"
        self.oi_change = 0

    def get_coin_list(self):
        response_local = requests.get(self.price_coin_url)
        data_local = response_local.json()
        self.coin_list = [each['symbol'] for each in data_local]
        # return self.coin_list

    def get_oi_values_thread(self, coin, period='5m', limit=12):
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
        threads = []
        for coin in self.coin_list:
            thread = threading.Thread(target=self.get_oi_values_thread, args=(coin, period, limit))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def get_sorted_top_oi(self):
        raw_oi_dict = self.top_oi
        return dict(sorted(raw_oi_dict.items(), key=lambda item: item[1], reverse=True))

    def get_top_oi_values(self, top_oi_coins):
        top_oi_values = {}
        for coin in top_oi_coins:
            top_oi_values[coin] = self.oi_values[coin]
        return top_oi_values

