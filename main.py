from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from tabs.watchlist_tab import WatchlistTab
from tabs.analytics_tab import AnalyticsTab
from tabs.news_tab import NewsTab
from tabs.trades_tab import TradesTab
from screener_tab import ScreenerTab
from database import Database

database = Database()
database.create_watchlist_table()
database.create_trades_table()
database.create_trades_results_table()
database.connection.close()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Futures Trading App")
        self.setMinimumSize(1250, 700)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a tab widget
        tab_widget = QTabWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(tab_widget)
        central_widget.setLayout(central_layout)

        # Create and add tabs to the tab widget
        watchlist_tab = WatchlistTab()
        screener_tab = ScreenerTab()
        news_tab = NewsTab()
        trades_tab = TradesTab(main_window_object=self)
        self.analytics_tab = AnalyticsTab(trades_tab.table_widget, trades_tab.get_port_size())

        tab_widget.addTab(watchlist_tab, "Watchlist")
        tab_widget.addTab(screener_tab, "Screener")
        tab_widget.addTab(news_tab, "News")
        tab_widget.addTab(trades_tab, "Trades")
        tab_widget.addTab(self.analytics_tab, "Performance")

        # Style the tab bar to make tab titles visible
        tab_bar = tab_widget.tabBar()

        tab_bar.setStyleSheet("""
            QTabBar::tab {
                background-color: #404040;
                color: #FFFFFF;
                font-weight: bold;
                border: 1px solid black;
                width: 150px;
                padding: 6px;
            }
            QTabBar::tab:selected {
                background-color: #555555;
            }
        """)

        # Apply a dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid black;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QLineEdit, QComboBox, QLabel, QTableWidget {
                background-color: #404040;
                color: #FFFFFF;
                border: 1px solid black;
                padding: 5px;
            }
        """)

        # Set the border of the tab widget content
        tab_widget.setStyleSheet("""
                    QTabWidget::pane {
                        border: 1px solid #404040; /* Set the border color to match the background */
                    }
                """)

        self.show()

    def update_analytics_start_port(self, start_port):
        self.analytics_tab.update_start_port(start_port)


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    app.exec()
