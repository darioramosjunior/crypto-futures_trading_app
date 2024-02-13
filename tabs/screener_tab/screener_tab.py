import threading

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QComboBox, QPushButton, QTableWidget, \
    QHeaderView, QTableWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from .oi_screener import OIValues
from .top_gainLose_screener import TopGainersLosers
from itertools import islice


# Helper Functions
def format_large_number(number):
    if abs(number) >= 1e9:
        return f'{number / 1e9:.2f} B'
    elif abs(number) >= 1e6:
        return f'{number / 1e6:.2f} M'
    elif abs(number) >= 1e3:
        return f'{number / 1e3:.2f} K'
    else:
        return f'{number:.2f}'


class ScreenerTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        self.oi_values = OIValues()
        self.price_changes = TopGainersLosers()
        self.oi_timeframe_dict = {'15m': ('5m', 3), '30m': ('5m', 6), '1H': ('5m', 12), '4H': ('15m', 16),
                                  '1D': ('2h', 12), '1W': ('1d', 7)}
        self.gain_lose_timeframe_dict = {'15m': ('5m', 3), '30m': ('5m', 6), '1H': ('5m', 12), '4H': ('15m', 16),
                                         '1D': ('2h', 12), '1W': ('1d', 7)}

        # Left Layout
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        oi_header = WidgetsHLayout()

        oi_label = QLabel("Top Open Interest")
        oi_label.setStyleSheet("font-weight: bold;")
        self.oi_tf_combobox = QComboBox()
        oi_tf_options = ("15m", "30m", "1H", "4H", "1D", "1W")
        self.oi_tf_combobox.addItems(oi_tf_options)
        self.oi_tf_combobox.setStyleSheet("font-weight: bold;")
        oi_refresh_button = QPushButton("-- SCAN --")
        oi_refresh_button.setStyleSheet("color: white; font-weight: bold;")

        self.oi_table = QTableWidget()
        self.oi_table.setColumnCount(3)
        self.oi_table.setRowCount(18)
        oi_table_labels = ["Coin", "Open Interest", "Open Interest Change"]
        self.oi_table.setHorizontalHeaderLabels(oi_table_labels)
        self.oi_table.horizontalHeader().setStyleSheet("::section {background-color: #404040; color: white; "
                                                  "font-weight: bold;}")
        self.oi_table.verticalHeader().hide()

        oi_header.add_widget(oi_label)
        oi_header.add_widget(self.oi_tf_combobox)
        oi_header.add_widget(oi_refresh_button)

        left_layout.addWidget(oi_header)
        left_layout.addWidget(self.oi_table)

        # Set column stretch to make them equally fill the available space
        for i in range(3):
            self.oi_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        oi_refresh_button.clicked.connect(self.get_top_oi)
        self.oi_tf_combobox.currentIndexChanged.connect(self.get_top_oi)

        # Right layout
        right_layout = QVBoxLayout()

        top_gain_lose_header = WidgetsHLayout()

        self.gain_lose_combobox = QComboBox()
        gain_lose_options = ("Top Gainers", "Top Losers")
        self.gain_lose_combobox.addItems(gain_lose_options)
        self.gain_lose_combobox.setStyleSheet("font-weight: bold;")
        self.gain_lose_tf_combobox = QComboBox()
        gain_lose_tf_combobox_options = ("15m", "30m", "1H", "4H", "1D", "1W")
        self.gain_lose_tf_combobox.addItems(gain_lose_tf_combobox_options)
        gain_lose_refresh_button = QPushButton("-- SCAN --")
        gain_lose_refresh_button.setStyleSheet("color: white; font-weight: bold;")

        gain_lose_refresh_button.clicked.connect(self.get_top_gain_lose)
        self.gain_lose_tf_combobox.currentIndexChanged.connect(self.get_top_gain_lose)
        self.gain_lose_combobox.currentIndexChanged.connect(self.get_top_gain_lose)

        top_gain_lose_header.add_widget(self.gain_lose_combobox)
        top_gain_lose_header.add_widget(self.gain_lose_tf_combobox)
        top_gain_lose_header.add_widget(gain_lose_refresh_button)

        self.gain_lose_table = QTableWidget()
        self.gain_lose_table.setColumnCount(3)
        self.gain_lose_table.setRowCount(18)
        gain_lose_table_labels = ["Coin", "Current Price", "Price Change (%)"]
        self.gain_lose_table.setHorizontalHeaderLabels(gain_lose_table_labels)
        self.gain_lose_table.horizontalHeader().setStyleSheet("::section {background-color: #404040; color: white; "
                                                              "font-weight: bold;}")
        self.gain_lose_table.verticalHeader().hide()

        right_layout.addWidget(top_gain_lose_header)
        right_layout.addWidget(self.gain_lose_table)

        # Set column stretch to make them equally fill the available space
        for i in range(3):
            self.gain_lose_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)

        self.set_default_values()

    def get_top_oi_thread(self):
        """
        This function is used to get the top open interest for a given timeframe and display them in the GUI.

        Parameters:
        timeframe_selected (str): The timeframe selected by the user from the drop-down menu.

        Returns:
        None

        """
        timeframe_selected = self.oi_tf_combobox.currentText()
        # print(timeframe_selected)

        period, limit = self.oi_timeframe_dict[timeframe_selected]

        self.oi_values.get_coin_list()
        self.oi_values.get_oi_values(period=period, limit=limit)
        top_oi_coins = []
        sorted_top_oi = self.oi_values.get_sorted_top_oi()
        [top_oi_coins.append(each[0]) for each in islice(sorted_top_oi.items(), 18)]
        oi_values = self.oi_values.get_top_oi_values(top_oi_coins)

        self.display_top_oi_details(oi_values)

    def get_top_oi(self):
        thread = threading.Thread(target=self.get_top_oi_thread)
        thread.start()

    def display_top_oi_details(self, oi_values: dict):
        """
        This function is used to display the top open interest values in the GUI.

        Parameters:
        oi_values (dict): A dictionary containing the open interest values for each coin. The dictionary is in the form
        of {coin_name: {OI, OI_change, OI_change_rate}}.

        Returns:
        None

        """
        # Need to reset table contents
        self.oi_table.setRowCount(0)
        self.oi_table.setRowCount(18)

        row_index = 0
        for outer_key, inner_dict in oi_values.items():
            # print(outer_key, inner_dict)

            oi = format_large_number(float(inner_dict["OI"]))
            oi_change = format_large_number(float(inner_dict["OI_change"]))
            oi_change_rate = float(inner_dict["OI_change_rate"])
            oi_change_rate = "{:.2f}".format(oi_change_rate)

            column0 = QTableWidgetItem(outer_key)
            column1 = QTableWidgetItem(oi)
            column2 = QTableWidgetItem(f"{oi_change} ({oi_change_rate}%)")

            column0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.oi_table.setItem(row_index, 0, column0)
            self.oi_table.setItem(row_index, 1, column1)
            self.oi_table.setItem(row_index, 2, column2)

            row_index = row_index + 1

    def get_top_gain_lose(self):
        thread = threading.Thread(target=self.get_top_gain_lose_thread)
        thread.start()

    def get_top_gain_lose_thread(self):
        """
        This function is used to get the top gainers and losers for a given timeframe and display them in the GUI.

        Parameters:
        timeframe_selected (str): The timeframe selected by the user from the drop-down menu.
        top_selected (int): The index of the top selection (0 for gainers, 1 for losers)

        Returns:
        None

        """
        timeframe_selected = self.gain_lose_tf_combobox.currentText()
        top_selected = self.gain_lose_combobox.currentIndex()

        interval, limit = self.gain_lose_timeframe_dict[timeframe_selected]

        self.price_changes.get_coin_list()

        self.price_changes.get_price_change_percent(interval, limit)
        if top_selected == 0:  # Top gainers
            top_gainer_coins = []
            top_gainers = self.price_changes.get_sorted_top_gainers()
            [top_gainer_coins.append(each[0]) for each in islice(top_gainers.items(), 18)]
            top_gainers_values = self.price_changes.get_price_values(top_gainer_coins)

            self.display_top_values_details(top_gainers_values)
        else:  # Top losers
            top_loser_coins = []
            top_losers = self.price_changes.get_sorted_top_losers()
            [top_loser_coins.append(each[0]) for each in islice(top_losers.items(), 18)]
            top_loser_values = self.price_changes.get_price_values(top_loser_coins)

            self.display_top_values_details(top_loser_values)

    def display_top_values_details(self, values_dict):
        # Need to reset table contents
        self.gain_lose_table.setRowCount(0)
        self.gain_lose_table.setRowCount(18)

        # Get top gain/lose selection
        top_selected = self.gain_lose_combobox.currentIndex()

        row_index = 0

        for outer_key, inner_dict in values_dict.items():
            # print(outer_key, inner_dict)

            current_price = str(inner_dict['Current_price'])
            if top_selected == 0:                   # Top gainers
                price_change_rate = float(inner_dict['Up_price_change'])
            else:                                   # Top losers
                price_change_rate = float(inner_dict['Down_price_change'])

            price_change_rate = "{:.2f}".format(price_change_rate)

            column0 = QTableWidgetItem(outer_key)
            column1 = QTableWidgetItem(current_price)
            column2 = QTableWidgetItem(f"{price_change_rate}%")

            column0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.gain_lose_table.setItem(row_index, 0, column0)
            self.gain_lose_table.setItem(row_index, 1, column1)
            self.gain_lose_table.setItem(row_index, 2, column2)

            row_index = row_index + 1

    def set_default_values(self):
        self.oi_tf_combobox.setCurrentIndex(2)
        self.gain_lose_combobox.setCurrentIndex(0)
        self.gain_lose_tf_combobox.setCurrentIndex(2)


class WidgetsHLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

    def add_widget(self, widget):
        self.layout.addWidget(widget)

