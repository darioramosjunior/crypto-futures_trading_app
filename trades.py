import pandas as pd

# path = "C:\Users\ramosd\Desktop\Python Projects\Personal Projects\Desktop_TradingApp\Binance Export - Aug 2023.xlsx"


# orig_df = pd.read_excel(path, sheet_name="sheet1")
# orig_df = pd.read_excel(path)

trades = []


class Trade:
    def __init__(self, entry_date, exit_date, symbol, trade_type, aep, axp, net_result, percent_return, total_units,
                 total_cost, total_proceeds):
        self.entry_date = entry_date
        self.exit_date = exit_date
        self.trade_type = trade_type
        self.symbol = symbol
        self.aep = aep
        self.axp = axp
        self.net_result = net_result
        self.percent_return = percent_return
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
        # Get the very first row of the table
        first_row = df.head(1)

        first_row_values = get_row_values(first_row)
        rows_to_delete.append(first_row_values['index'])

        quantity = first_row_values['quantity']

        # Fees, cost, proceeds & net return calculation
        total_fees = first_row_values['fee']
        total_profit = first_row_values['profit']
        total_proceeds = first_row_values['amount']
        total_cost = 0

        # aep & axp calculation
        exit_price = [first_row_values['price']]
        exit_quantity = [quantity]
        entry_price = []
        entry_quantity = []

        # print('Exit Trade:', first_row_values)

        # Filter succeeding rows with the same symbol
        filtered_df = df[(df['Symbol'] == first_row_values['symbol']) & (df.index > first_row_values['index'])]

        # To offset precision issues in floating point numbers
        epsilon= 1e-9

        # Use quantity as the basis to check if the trade is complete
        while abs(quantity) > epsilon:
            # Iterate each row of filtered df
            for filtered_row in filtered_df.iterrows():
                filtered_row_values = get_filtered_row_values(filtered_row)

                if filtered_row_values['side'] == first_row_values['side']:
                    # print('Exit Trade:', filtered_row_values)

                    quantity = quantity + filtered_row_values['quantity']
                    total_fees = total_fees + filtered_row_values['fee']
                    total_proceeds = total_proceeds + filtered_row_values['amount']
                    total_profit = total_profit + filtered_row_values['profit']

                    exit_price.append(filtered_row_values['price'])
                    exit_quantity.append(filtered_row_values['quantity'])

                    rows_to_delete.append(filtered_row_values['index'])
                else:
                    # print('Entry Trade:', filtered_row_values)

                    quantity = quantity - filtered_row_values['quantity']
                    total_fees = total_fees + filtered_row_values['fee']
                    total_cost = total_cost + filtered_row_values['amount']
                    total_profit = total_profit + filtered_row_values['profit']

                    entry_price.append(filtered_row_values['price'])
                    entry_quantity.append(filtered_row_values['quantity'])

                    rows_to_delete.append(filtered_row_values['index'])

                    if abs(quantity) < epsilon:
                        trade_side = filtered_row_values['side']
                        if trade_side == "BUY":
                            cost = total_cost + total_fees
                            proceed = total_proceeds
                            total_return = proceed - cost
                            # print("Total return:", total_return)
                        else:
                            cost = total_proceeds + total_fees
                            proceed = total_cost
                            total_return = proceed - cost
                            # print("Total return:", total_return)

                        exit_date = first_row_values['date'].split(" ")[0]
                        entry_date = filtered_row_values['date'].split(" ")[0]
                        trade_type = 'LONG' if trade_side == 'BUY' else 'SHORT'
                        ticker = first_row_values['symbol']

                        # axp calculation
                        total_exit_price = sum(price * quantity for price,quantity in zip(exit_price, exit_quantity))
                        total_exit_quantity = sum(exit_quantity)
                        axp = total_exit_price / total_exit_quantity

                        # aep calculation
                        total_entry_price = sum(price * quantity for price, quantity in zip(entry_price, entry_quantity))
                        total_entry_quantity = sum(entry_quantity)
                        aep = total_entry_price / total_entry_quantity

                        # % Gain/Loss
                        percent_return = (total_return / cost) * 100

                        # Create Trade Object
                        trades.append(Trade(entry_date, exit_date, ticker, trade_type, axp, aep, total_return,
                                            percent_return, total_entry_quantity, cost, proceed))

                        print("=============================================")
                        break

        return rows_to_delete
    else:
        return rows_to_delete


def get_trades(path):
    file_path = rf"{path}"
    orig_df = pd.read_excel(file_path)

    condition = True
    while condition:
        num_rows = len(orig_df)

        if not (num_rows > 2):
            condition = False
            break

        current_rows_to_delete = calculate_trades(orig_df)
        orig_df = orig_df.drop(current_rows_to_delete)

    return trades



