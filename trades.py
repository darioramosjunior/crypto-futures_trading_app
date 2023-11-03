import pandas as pd

path = r"C:\Users\ramosd\Desktop\Python Projects\Personal Projects\Desktop_TradingApp\Binance Export - Aug 2023.xlsx"

orig_df = pd.read_excel(path, sheet_name="sheet1")


class EntryOrder():
    def __init__(self, date, symbol, side, aep, units, total_cost):
        self.date = date
        self.symbol = symbol
        self.side = side
        self.aep = aep
        self.units = units
        self.total_cost = total_cost


class ExitOrder():
    def __init__(self, date, symbol, side, axp, units, total_proceeds):
        self.date = date
        self.symbol = symbol
        self.side = side
        self.axp = axp
        self.units = units
        self.total_proceeds = total_proceeds


class Trade():
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


orders = []


for id, row in orig_df.iterrows():
    if row['Realized Profit'] != 0:
        orders.append({"id": id, "coin": f"{row['Symbol']}-{row['Side']}", "Order": "Exit", "Exit_obj": ExitOrder(row['Date(UTC)'],
                                                                                               row['Symbol'],
                                                                                               row['Side'],
                                                                                               row['Price'],
                                                                                               row['Quantity'],
                                                                                               (row['Amount'] +
                                                                                               row['Fee']))})
    else:
        orders.append({"id": id, "coin": f"{row['Symbol']}-{row['Side']}", "Order": "Entry", "Entry_obj": EntryOrder(row['Date(UTC)'],
                                                                                                  row['Symbol'],
                                                                                                  row['Side'],
                                                                                                  row['Price'],
                                                                                                  row['Quantity'],
                                                                                                  (row['Amount'] -
                                                                                                   row['Fee']))})

[print(each) for each in orders]

trades = []

exit_quantity = 0
net_return = 0

coin_temporary = ""

for index, each in enumerate(orders):
    if each['Order'] == 'Exit':
        exit_quantity = exit_quantity + each['Exit_obj'].units
        net_return = net_return + each['Exit_obj'].total_proceeds
        coin_temporary = each['coin']
    else:
        exit_quantity = exit_quantity - each['Entry_obj'].units
        if exit_quantity != 0:
            pass


# entry_orders = []
# exit_orders = []

# for each in orders:
#     if each['Order'] == 'Exit':
#         exit_orders.append(each)
#     elif each['Order'] == 'Entry':
#         entry_orders.append(each)
#
# [print(each) for each in exit_orders]
# [print(each) for each in entry_orders]
#
# for exit in exit_orders:
#     exit_quantity = exit['Exit_obj'].units
#     exit_coin = exit['coin']
#     print(exit_coin, exit_quantity)
    # for entry in entry_orders:

