import pandas as pd
from decimal import Decimal

path = r"C:\Users\ramosd\Desktop\Python Projects\Personal Projects\Desktop_TradingApp\Binance Export - Aug 2023.xlsx"

orig_df = pd.read_excel(path, sheet_name="sheet1")


class EntryOrder:
    def __init__(self, date, symbol, side, aep, units, total_cost):
        self.date = date
        self.symbol = symbol
        self.side = side
        self.aep = aep
        self.units = units
        self.total_cost = total_cost


class ExitOrder:
    def __init__(self, date, symbol, side, axp, units, total_proceeds):
        self.date = date
        self.symbol = symbol
        self.side = side
        self.axp = axp
        self.units = units
        self.total_proceeds = total_proceeds


class Trade:
    def __init__(self, entry_date, exit_date, aep, axp, net_result, net_result_percent, total_units, total_cost,
                 total_proceeds):
        self.entry_date = entry_date
        self.exit_date = exit_date
        self.aep = aep
        self.axp = axp
        self.net_result = net_result
        self.net_result_percent = net_result_percent
        self.total_units = total_units
        self.total_cost = total_cost
        self.total_proceeds = total_proceeds


def get_row_values(row):
    keys = ['date', 'index', 'symbol', 'side', 'price', 'quantity', 'amount', 'fee', 'profit']
    row_date = row['Date(UTC)'].values[0]
    row_index = row.index.values[0]
    row_symbol = row['Symbol'].values[0]
    row_side = row['Side'].values[0]
    row_price = row['Price'].values[0]
    row_quantity = row['Quantity'].values[0]
    row_amount = row['Amount'].values[0]
    row_fee = row['Fee'].values[0]
    row_profit = row['Realized Profit'].values[0]
    values = [row_date, row_index, row_symbol, row_side, row_price, row_quantity, row_amount, row_fee, row_profit]

    row_dict = {keys[i]: values[i] for i in range(len(keys))}
    return row_dict


def get_filtered_row_values(row):
    keys = ['date', 'index', 'symbol', 'side', 'price', 'quantity', 'amount', 'fee', 'profit']
    row_date = row[1]['Date(UTC)']
    row_index = row[0]
    row_symbol = row[1]['Symbol']
    row_side = row[1]['Side']
    row_price = row[1]['Price']
    row_quantity = row[1]['Quantity']
    row_amount = row[1]['Amount']
    row_fee = row[1]['Fee']
    row_profit = row[1]['Realized Profit']
    values = [row_date, row_index, row_symbol, row_side, row_price, row_quantity, row_amount, row_fee, row_profit]

    row_dict = {keys[i]: values[i] for i in range(len(keys))}
    return row_dict


def calculate_trades(df):
    rows_to_delete = []

    if not df.empty:
        first_row = df.head(1)
        first_row_values = get_row_values(first_row)
        rows_to_delete.append(first_row_values['index'])
        quantity = first_row_values['quantity']
        print('Exit Trade:', first_row_values)

        filtered_df = df[(df['Symbol'] == first_row_values['symbol']) & (df.index > first_row_values['index'])]

        # To offset precision issues in floating point numbers
        epsilon= 1e-9

        while abs(quantity) > epsilon:
            for filtered_row in filtered_df.iterrows():
                filtered_row_values = get_filtered_row_values(filtered_row)

                if filtered_row_values['side'] == first_row_values['side']:
                    print('Exit Trade:', filtered_row_values)
                    quantity = quantity + filtered_row_values['quantity']
                    rows_to_delete.append(filtered_row_values['index'])
                else:
                    print('Entry Trade:', filtered_row_values)
                    quantity = quantity - filtered_row_values['quantity']
                    rows_to_delete.append(filtered_row_values['index'])

                    if abs(quantity) < epsilon:
                        print("=============================================")
                        break

        return rows_to_delete
    else:
        return rows_to_delete


condition = True

while condition:
    num_rows = len(orig_df)
    print("=====================")

    if not (num_rows > 2):
        condition = False
        break

    current_rows_to_delete = calculate_trades(orig_df)
    orig_df = orig_df.drop(current_rows_to_delete)


