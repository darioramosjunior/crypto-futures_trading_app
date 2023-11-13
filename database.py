import sqlite3


class Database:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file
        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()

    def create_watchlist_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY,
                coin_name TEXT,
                watch_price REAL,
                condition INTEGER,
                port_size REAL,
                var_percentage REAL,
                cut_percentage REAL,
                position_size REAL)''')
        self.connection.commit()

    def create_trades_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, entry_date TEXT, 
                exit_date TEXT, ticker TEXT, side TEXT, aep REAL, axp REAL, quantity REAL, cost REAL, proceed REAL, 
                net_gain REAL, percent_gain REAL)''')
        self.connection.commit()


