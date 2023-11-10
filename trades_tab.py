from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QHBoxLayout, QLineEdit, \
    QTableWidgetItem
from PyQt6.QtCore import Qt
from trades import get_trades

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

        # Execute trades tab objects' fill_rows_table_widget method
        self.trades_tab.fill_rows_table_widget(trades)

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

        self.setLayout(layout)

    def fill_rows_table_widget(self, trades):
        self.table_widget.setRowCount(len(trades))
        for row_index, trade_object in enumerate(trades):
            column0 = QTableWidgetItem(trade_object.entry_date)
            column1 = QTableWidgetItem(trade_object.exit_date)
            column2 = QTableWidgetItem(trade_object.symbol)
            column3 = QTableWidgetItem(trade_object.trade_type)
            column4 = QTableWidgetItem("{:.6f}".format(trade_object.aep))
            column5 = QTableWidgetItem("{:.6f}".format(trade_object.axp))
            column6 = QTableWidgetItem("{:.2f}".format(trade_object.total_units))
            column7 = QTableWidgetItem("{:.2f}".format(trade_object.total_cost))
            column8 = QTableWidgetItem("{:.2f}".format(trade_object.total_proceeds))
            column9 = QTableWidgetItem("{:.3f}".format(trade_object.net_result))
            column10 = QTableWidgetItem("{:.2f}".format(trade_object.percent_return))

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




