from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
from database import Database
from .coin_prices_script import get_coins_data
import threading


class WatchlistItem(QWidget):

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.row_id = 0

        self.coin = QLineEdit()
        self.coin.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.watch_price = QLineEdit()
        self.watch_price.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.trigger_condition = QComboBox()
        self.trigger_condition.addItems(["> / =", "< / ="])

        self.current_price = QLineEdit("")
        self.current_price.setReadOnly(True)
        self.current_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_price.setToolTip("999999 - means either coin is invalid or there's a network issue")

        self.status = QLabel("WAIT")  # TO-DO: To set dynamically
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("background-color: #808080;")

        self.port_size = QLineEdit()
        self.port_size.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.var_percentage = QLineEdit()
        self.var_percentage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cut_percentage = QLineEdit()
        self.cut_percentage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cut_percentage.setToolTip("Percentage change between Entry & Cut in the chart")

        self.position_size = QLabel("USD")
        self.position_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_size.setStyleSheet("border: 1px solid black;")

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setEnabled(False)
        clear_button = QPushButton("Clear")

        layout.addWidget(self.coin)
        layout.addWidget(self.watch_price)
        layout.addWidget(self.trigger_condition)
        layout.addWidget(self.current_price)
        layout.addWidget(self.status)
        layout.addWidget(self.port_size)
        layout.addWidget(self.var_percentage)
        layout.addWidget(self.cut_percentage)
        layout.addWidget(self.position_size)
        layout.addWidget(self.calculate_button)
        layout.addWidget(clear_button)

        layout.setStretchFactor(self.coin, 1)
        layout.setStretchFactor(self.watch_price, 1)
        layout.setStretchFactor(self.trigger_condition, 1)
        layout.setStretchFactor(self.current_price, 1)
        layout.setStretchFactor(self.status, 1)
        layout.setStretchFactor(self.port_size, 1)
        layout.setStretchFactor(self.var_percentage, 1)
        layout.setStretchFactor(self.cut_percentage, 1)
        layout.setStretchFactor(self.position_size, 1)
        layout.setStretchFactor(self.calculate_button, 1)
        layout.setStretchFactor(clear_button, 1)

        # Connections
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_current_price)
        self.timer.start(30000)

        self.calculate_button.clicked.connect(self.calculate_pos_size)
        clear_button.clicked.connect(self.delete_row)

        # Update_current_price connections
        self.calculate_button.clicked.connect(self.update_current_price)
        self.coin.textChanged.connect(self.update_current_price)

        # Toggle_status connections
        self.current_price.textChanged.connect(self.toggle_status)
        self.trigger_condition.currentIndexChanged.connect(self.toggle_status)
        self.watch_price.textChanged.connect(self.toggle_status)

        # Toggle_calculate_button connections
        self.port_size.textChanged.connect(self.toggle_calculate_button)
        self.cut_percentage.textChanged.connect(self.toggle_calculate_button)
        self.var_percentage.textChanged.connect(self.toggle_calculate_button)

        self.show()

    def calculate_pos_size(self):
        port_size = float(self.port_size.text())
        var_percentage = float(self.var_percentage.text())
        var = port_size * (var_percentage / 100)
        cut_percentage = float(self.cut_percentage.text())
        pos_size = var / (cut_percentage / 100)
        formatted_pos_size = "{:.2f} USD".format(pos_size)
        self.position_size.setText(formatted_pos_size)

        condition = self.all_fields_filled()
        # All fields must be filled before storing row in the database
        if condition:
            database = Database()
            data_to_insert = (self.row_id, self.coin.text(), float(self.watch_price.text()),
                              self.trigger_condition.currentIndex(), port_size, var_percentage, cut_percentage, pos_size)

            database.cursor.execute("INSERT OR REPLACE INTO watchlist (id, coin_name, watch_price, condition,"
                                    " port_size, " "var_percentage, cut_percentage, position_size) "
                                    "VALUES (?,?,?,?,?,?,?,?)", data_to_insert)
            database.connection.commit()
            database.connection.close()

    def delete_row(self):
        database = Database()
        database.cursor.execute("DELETE from watchlist WHERE id=?", (self.row_id,))
        database.connection.commit()
        database.connection.close()

        self.set_default_values()

    def set_default_values(self):
        self.coin.setText("")
        self.watch_price.setText("")
        self.trigger_condition.setCurrentIndex(0)
        self.current_price.setText("")
        self.status.setText("WAIT")
        self.status.setStyleSheet("background-color: lightgray; color: black")
        self.port_size.setText("")
        self.var_percentage.setText("")
        self.cut_percentage.setText("")
        self.position_size.setText("USD")
        print("Clear Row")

    def set_row_id(self, row_id):
        self.row_id = row_id

    def load_row_data(self):
        database = Database()
        database.cursor.execute("SELECT * FROM watchlist WHERE id=?", (self.row_id,))
        row_data = database.cursor.fetchall()
        database.connection.close()

        if row_data:
            row_data = row_data[0]
            self.coin.setText(row_data[1])
            self.watch_price.setText(f"{row_data[2]}")
            self.trigger_condition.setCurrentIndex(row_data[3])
            self.port_size.setText(f"{row_data[4]}")
            self.var_percentage.setText(f"{row_data[5]}")
            self.cut_percentage.setText(f"{row_data[6]}")
            formatted_pos_size = "{:.2f} USD".format(row_data[7])
            self.position_size.setText(formatted_pos_size)

    def fetch_coin_data(self):
        try:
            coin_data = get_coins_data()
            self.update_current_price_thread(coin_data)
        except:
            self.current_price.setText("99999999")

    def update_current_price_thread(self, coin_data):
        coin_list = [each['symbol'] for each in coin_data]
        if self.coin.text().strip().upper() in coin_list:
            for each in coin_data:
                if each['symbol'] == self.coin.text().strip().upper():
                    print(each['symbol'], "-", each['price'])
                    self.current_price.setText(each['price'])
        elif self.coin.text().strip().upper() == "":
            self.current_price.setText("")
        else:
            self.current_price.setText("99999999")

    def update_current_price(self):
        # Thread is needed in order for the request does not disrupt the app
        thread = threading.Thread(target=self.fetch_coin_data)
        thread.start()

    def toggle_status(self):

        # watch price must not be empty before performing comparison
        if self.watch_price.text().strip() and self.current_price.text().strip():
            watch_price = float(self.watch_price.text())
            current_price = float(self.current_price.text())
            trigger_condition = self.trigger_condition.currentIndex()

            if trigger_condition == 0:
                if current_price >= watch_price:
                    self.status.setText("ALERT")
                    self.status.setStyleSheet("background-color: green; color: white;")
                else:
                    self.status.setText("WAIT")
                    self.status.setStyleSheet("background-color: lightgray; color: black")
            else:
                if current_price <= watch_price:
                    self.status.setText("ALERT")
                    self.status.setStyleSheet("background-color: red; color: white;")
                else:
                    self.status.setText("WAIT")
                    self.status.setStyleSheet("background-color: lightgray; color: black")
        else:
            pass

    def toggle_calculate_button(self):
        condition = self.port_size.text().strip() and self.var_percentage.text().strip() and \
                    self.cut_percentage.text().strip()
        if condition:
            self.calculate_button.setEnabled(True)
        else:
            self.calculate_button.setEnabled(False)

    def all_fields_filled(self):
        condition = self.coin.text().strip() and self.watch_price.text().strip() and self.port_size.text().strip() and \
                    self.var_percentage.text().strip() and self.cut_percentage.text().strip()
        if condition:
            return True
        else:
            return False


class Columns(QWidget):

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.setStyleSheet("""QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: none;
                font-weight: bold;
            }""")

        column1_label = QLabel("Coin Name")
        column1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column2_label = QLabel("Watch Price")
        column2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column3_label = QLabel("Condition")
        column3_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column5_label = QLabel("Current Price")
        column5_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column6_label = QLabel("Status")
        column6_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column7_label = QLabel("Port Size (USD)")
        column7_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column8_label = QLabel("VAR (%)")
        column8_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column9_label = QLabel("CUT (%)")
        column9_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column9_label.setToolTip("Percentage change between Entry & Cut in the chart")
        column10_label = QLabel(" Position Size ")
        column10_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # For column & row value alignment purpose only
        column11_label = QLabel("")
        column12_label = QLabel("")

        layout.addWidget(column1_label)
        layout.addWidget(column2_label)
        layout.addWidget(column3_label)
        layout.addWidget(column5_label)
        layout.addWidget(column6_label)
        layout.addWidget(column7_label)
        layout.addWidget(column8_label)
        layout.addWidget(column9_label)
        layout.addWidget(column10_label)
        layout.addWidget(column11_label)
        layout.addWidget(column12_label)

        layout.setStretchFactor(column1_label, 1)
        layout.setStretchFactor(column2_label, 1)
        layout.setStretchFactor(column3_label, 1)
        layout.setStretchFactor(column5_label, 1)
        layout.setStretchFactor(column6_label, 1)
        layout.setStretchFactor(column7_label, 1)
        layout.setStretchFactor(column8_label, 1)
        layout.setStretchFactor(column9_label, 1)
        layout.setStretchFactor(column10_label, 1)
        layout.setStretchFactor(column11_label, 1)
        layout.setStretchFactor(column12_label, 1)

        self.show()