import threading

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QComboBox, QPushButton, QTableWidget, \
    QHeaderView, QTableWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from OI_screener import OIValues
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
        return str(number)


class ScreenerTab(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        self.oi_values = OIValues()
        self.timeframe_dict = {'15m': ('5m', 3), '30m': ('5m', 6), '1H': ('5m', 12), '4H': ('15m', 16),
                               '1D': ('2h', 12), '1W': ('1d', 7)}

        # Left Layout
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        oi_header = WidgetsHLayout()

        oi_label = QLabel("Top Open Interest")
        self.oi_tf_combobox = QComboBox()
        oi_tf_options = ("15m", "30m", "1H", "4H", "1D", "1W")
        self.oi_tf_combobox.addItems(oi_tf_options)
        oi_refresh_button = QPushButton()
        oi_refresh_button.setIcon(QIcon("images/refresh_icon.jpg"))

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

        right_label = QLabel("Right Label")

        right_layout.addWidget(right_label)

        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)

        self.set_default_values()

    def get_top_oi_thread(self):
        timeframe_selected = self.oi_tf_combobox.currentText()
        print(timeframe_selected)

        period, limit = self.timeframe_dict[timeframe_selected]

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

    def display_top_oi_details(self, oi_values):
        # Need to reset table contents
        self.oi_table.setRowCount(0)
        self.oi_table.setRowCount(18)

        row_index = 0
        for outer_key, inner_dict in oi_values.items():
            print(outer_key, inner_dict)

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

    def set_default_values(self):
        self.oi_tf_combobox.setCurrentIndex(2)


class WidgetsHLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

    def add_widget(self, widget):
        self.layout.addWidget(widget)

