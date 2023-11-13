from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QHBoxLayout, QLineEdit, \
    QTableWidgetItem
from PyQt6.QtCore import Qt
from trades import get_trades
from database import Database
import threading

file_path = ""


class FileSelector(QWidget):
    def __init__(self, trades_tab_object):
        super().__init__()
        # Need to pass TradesTab instance as argument to access its fill_rows_table_widget() method
        self.trades_tab = trades_tab_object

        layout = QHBoxLayout()

        self.button = QPushButton("Select File")

        self.label = QLineEdit("--- File Path ---")
        self.label.setReadOnly(True)

        self.file_dialog = QFileDialog()

        # Connections
        self.button.clicked.connect(self.open_file_selector)
        self.label.textChanged.connect(self.get_trades_list)

        layout.addWidget(self.button)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def open_file_selector(self):
        self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        file_name, _ = self.file_dialog.getOpenFileName(
            self, "Select Trade History", "", "Excel Workbook (*.xlsx);;All Files (*)"
        )

        if file_name:
            self.label.setText(f"{file_name}")

    def get_trades_list(self):
        print(self.label.text())
        trades = get_trades(path=self.label.text())

        if trades:
            self.trades_tab.clear_table()
            self.trades_tab.clear_trades_db()

            # Execute trades tab objects' fill_rows_table_widget method
            self.trades_tab.store_to_database(trades)
            self.trades_tab.fill_rows_table_widget()


class TradesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # File Selector
        file_selector = FileSelector(trades_tab_object=self)

        # Table Widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(12)
        table_headers = ["Entry Date", "Exit Date", "Ticker", "Side", "AEP", "AXP", "Quantity", "Cost", "Proceed",
                         "Net Gain", "% Gain", "Port Effect"]
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
        print(trades)

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



