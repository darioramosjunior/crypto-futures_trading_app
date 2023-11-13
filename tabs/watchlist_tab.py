from PyQt6.QtWidgets import QWidget, QVBoxLayout
from watchlist_item import WatchlistItem, Columns


class WatchlistTab(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        coin_list = []
        columns = Columns()

        coin1 = WatchlistItem()
        coin_list.append(coin1)
        coin2 = WatchlistItem()
        coin_list.append(coin2)
        coin3 = WatchlistItem()
        coin_list.append(coin3)
        coin4 = WatchlistItem()
        coin_list.append(coin4)
        coin5 = WatchlistItem()
        coin_list.append(coin5)
        coin6 = WatchlistItem()
        coin_list.append(coin6)
        coin7 = WatchlistItem()
        coin_list.append(coin7)
        coin8 = WatchlistItem()
        coin_list.append(coin8)
        coin9 = WatchlistItem()
        coin_list.append(coin9)
        coin10 = WatchlistItem()
        coin_list.append(coin10)

        # Set unique id for each row or coin
        for row_id, coin in enumerate(coin_list):
            coin.set_row_id(row_id+1)

        # Load row data from the database
        for coin in coin_list:
            coin.load_row_data()

        layout.addWidget(columns)
        layout.addWidget(coin1)
        layout.addWidget(coin2)
        layout.addWidget(coin3)
        layout.addWidget(coin4)
        layout.addWidget(coin5)
        layout.addWidget(coin6)
        layout.addWidget(coin7)
        layout.addWidget(coin8)
        layout.addWidget(coin9)
        layout.addWidget(coin10)

        self.setLayout(layout)

        self.show()

