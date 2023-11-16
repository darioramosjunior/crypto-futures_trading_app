from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QHBoxLayout, QLineEdit, \
    QTableWidgetItem, QLabel
from PyQt6.QtCore import Qt
from trades import get_trades
from database import Database
import threading

file_path = ""


def store_file_path(path):
    with open("tabs/configurations.txt", 'r') as file:
        content = file.readlines()
    for index, line in enumerate(content):
        if "File_path:" in line:
            content[index] = f"File_path:{path}" + "\n"

    with open("tabs/configurations.txt", 'w') as file:
        file.writelines(content)


def get_file_path():
    with open("tabs/configurations.txt", 'r') as file:
        content = file.readlines()
    for line in content:
        if "File_path:" in line:
            path = line.split("File_path:")
            return path


def store_port_size(port_size):
    with open("tabs/configurations.txt", 'r') as file:
        content = file.readlines()
    for index, line in enumerate(content):
        if "Port_size:" in line:
            content[index] = f"Port_size:{port_size}" + "\n"

    with open("tabs/configurations.txt", 'w') as file:
        file.writelines(content)


def get_port_size():
    with open("tabs/configurations.txt", 'r') as file:
        content = file.readlines()
    for line in content:
        if "Port_size:" in line:
            path = line.split("Port_size:")
            return path


class FileSelector(QWidget):
    def __init__(self, trades_tab_object):
        super().__init__()
        # Need to pass TradesTab instance as argument to access its methoda
        self.trades_tab = trades_tab_object

        layout = QHBoxLayout()

        self.button = QPushButton("Select File")

        self.label = QLineEdit("--- File Path ---")
        self.label.setReadOnly(True)

        self.start_port_label = QLabel("Starting Portfolio $")
        self.start_port = QLineEdit()

        self.file_dialog = QFileDialog()

        # Connections
        self.button.clicked.connect(self.open_file_selector)
        self.label.textChanged.connect(self.get_trades_list)
        self.label.textChanged.connect(self.calculate_port_effects)
        self.label.textChanged.connect(self.save_file_path)
        self.start_port.textChanged.connect(self.calculate_port_effects)
        self.start_port.textChanged.connect(self.save_port_size)

        layout.addWidget(self.button)
        layout.addWidget(self.label, stretch=2)
        layout.addWidget(self.start_port_label)
        layout.addWidget(self.start_port)

        self.fill_filepath_thread()
        self.fill_port_size_thread()

        self.setLayout(layout)

    def open_file_selector(self):
        self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        file_name, _ = self.file_dialog.getOpenFileName(
            self, "Select Trade History", "", "Excel Workbook (*.xlsx);;All Files (*)"
        )

        if file_name:
            self.label.setText(f"{file_name}")

    def get_trades_list(self):
        trades = get_trades(path=self.label.text())
        trades.reverse()

        if trades:
            self.trades_tab.clear_table()
            self.trades_tab.clear_trades_db()
            self.trades_tab.clear_trades_results_db()

            # Execute trades tab objects' fill_rows_table_widget method
            self.trades_tab.store_to_database(trades)
            self.trades_tab.fill_rows_table_widget()
            self.calculate_port_effects()

    def calculate_port_effects(self):
        if self.start_port.text() != "":
            start_port = float(self.start_port.text())
            self.trades_tab.calc_port_effects(start_port)
        else:
            self.trades_tab.clear_trades_results_db()
            self.trades_tab.clear_new_ports_port_effects()

    def save_file_path(self):
        path = self.label.text()
        store_file_path(path)

    def fill_filepath(self):
        path = get_file_path()
        path = path[1].replace("\n", "")
        self.label.setText(path)

    def fill_filepath_thread(self):
        thread = threading.Thread(target=self.fill_filepath)
        thread.start()

    def save_port_size(self):
        port_size = self.start_port.text()
        store_port_size(port_size)

    def fill_port_size(self):
        port_size = get_port_size()
        port_size = port_size[1].replace("\n", "")
        self.start_port.setText(port_size)

    def fill_port_size_thread(self):
        thread = threading.Thread(target=self.fill_port_size)
        thread.start()


class TradesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # File Selector
        file_selector = FileSelector(trades_tab_object=self)

        # Table Widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(13)
        table_headers = ["Entry Date", "Exit Date", "Ticker", "Side", "AEP", "AXP", "Quantity", "Cost", "Proceed",
                         "Net Gain", "% Gain", "New Port", "Port Effect %"]
        self.table_widget.setHorizontalHeaderLabels(table_headers)
        self.table_widget.horizontalHeader().setStyleSheet("::section {background-color: #404040; color: white; "
                                                           "font-weight: bold;}")

        layout.addWidget(file_selector)
        layout.addWidget(self.table_widget)
        self.fill_rows_table_widget()

        self.setLayout(layout)

    def fill_rows_table_widget(self):
        database = Database()
        database.cursor.execute('SELECT * FROM trades')
        trades = database.cursor.fetchall()

        self.table_widget.setRowCount(len(trades))
        for row_index, trade in enumerate(trades):
            column0 = QTableWidgetItem(trade[1])
            column1 = QTableWidgetItem(trade[2])
            column2 = QTableWidgetItem(trade[3])
            column3 = QTableWidgetItem(trade[4])
            column4 = QTableWidgetItem("{:.6f}".format(trade[5]))
            column5 = QTableWidgetItem("{:.6f}".format(trade[6]))
            column6 = QTableWidgetItem("{:.2f}".format(trade[7]))
            column7 = QTableWidgetItem("{:.2f}".format(trade[8]))
            column8 = QTableWidgetItem("{:.2f}".format(trade[9]))
            column9 = QTableWidgetItem("{:.3f}".format(trade[10]))
            column10 = QTableWidgetItem("{:.2f}".format(trade[11]))

            column0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column3.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column5.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column6.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column7.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column8.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column9.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            column10.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table_widget.setItem(row_index, 0, column0)
            self.table_widget.setItem(row_index, 1, column1)
            self.table_widget.setItem(row_index, 2, column2)
            self.table_widget.setItem(row_index, 3, column3)
            self.table_widget.setItem(row_index, 4, column4)
            self.table_widget.setItem(row_index, 5, column5)
            self.table_widget.setItem(row_index, 6, column6)
            self.table_widget.setItem(row_index, 7, column7)
            self.table_widget.setItem(row_index, 8, column8)
            self.table_widget.setItem(row_index, 9, column9)
            self.table_widget.setItem(row_index, 10, column10)

    def store_to_database(self, trades):
        database = Database()
        for trade in trades:
            data_to_insert = (trade.entry_date, trade.exit_date, trade.symbol, trade.trade_type, trade.aep, trade.axp,
                              trade.total_units, trade.total_cost, trade.total_proceeds, trade.net_result,
                              trade.percent_return)

            database.cursor.execute("INSERT INTO trades (entry_date, exit_date, ticker, side, aep, axp, quantity, cost,"
                                    " proceed, net_gain, percent_gain) VALUES (?,?,?,?,?,?,?,?,?,?,?)", data_to_insert)
        database.connection.commit()
        database.connection.close()

    def clear_table(self):
        self.table_widget.setRowCount(0)

    def clear_trades_db(self):
        database = Database()
        database.cursor.execute("DELETE FROM trades")
        database.connection.commit()
        database.connection.close()

    def calc_port_effects(self, start_port):
        net_gain_column = 9
        new_port_column = 11
        port_effect_column = 12
        exit_date_column = 1
        old_port = start_port
        database = Database()

        for row in range(self.table_widget.rowCount()):
            # Get net_gain for particular 'row'
            net_gain = float(self.table_widget.item(row, net_gain_column).text())
            new_port = old_port + net_gain

            # Create cell items for New Port
            new_port_item = QTableWidgetItem("{:.3f}".format(new_port))
            new_port_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, new_port_column, new_port_item)

            # Create cell items for Port Effect %
            port_effect = (net_gain / old_port) * 100
            port_effect_item = QTableWidgetItem("{:.2f}".format(port_effect))
            port_effect_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_widget.setItem(row, port_effect_column, port_effect_item)

            old_port = new_port

            # Add or modify trades_results database
            exit_date = self.table_widget.item(row, exit_date_column).text()
            data_to_insert = (row, exit_date, port_effect)
            database.cursor.execute("INSERT OR REPLACE INTO trades_results (id, exit_date, port_effect_percent) "
                                    "VALUES (?,?,?)", data_to_insert)

        database.connection.commit()
        database.connection.close()

    def clear_trades_results_db(self):
        database = Database()
        database.cursor.execute("DELETE from trades_results")
        database.connection.commit()
        database.connection.close()

    def clear_new_ports_port_effects(self):
        new_port_column = 11
        port_effect_column = 12
        for row in range(self.table_widget.rowCount()):
            new_port_item = QTableWidgetItem("")
            self.table_widget.setItem(row, new_port_column, new_port_item)

            port_effect_item = QTableWidgetItem("")
            self.table_widget.setItem(row, port_effect_column, port_effect_item)



