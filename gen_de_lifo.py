import pandas as pd
from collections import defaultdict

action_rows = pd.read_csv("rawdata_action_rows.csv")
stock_prices_rows = pd.read_csv("rawdata_stock_prices.csv")

action_rows['period'] = action_rows['period'].astype(int)
action_rows['amount'] = action_rows['amount'].astype(int)
action_rows['price'] = action_rows['price'].astype(float)

stock_prices_rows['period'] = stock_prices_rows['period'].astype(int)
stock_prices_rows['price'] = stock_prices_rows['price'].astype(float)

price_lookup = stock_prices_rows.set_index(['stock_name', 'period'])['price']

start_period = 5
end_period = 14

unique_users = action_rows['user_id'].unique()
results = []

for user in unique_users:
    user_actions = action_rows[action_rows['user_id'] == user]
    portfolio = defaultdict(list) 

    pot_gewinn = 0
    pot_verlust = 0
    real_gewinn = 0
    real_verlust = 0

    for period in range(start_period, end_period + 1):
        period_actions = user_actions[user_actions['period'] == period]

        for _, row in period_actions[period_actions['action'] == 'Buy'].iterrows():
            buy_price = price_lookup.get((row['stock_name'], period - 1), None)
            if buy_price is not None:
                portfolio[row['stock_name']].append([period, row['amount'], buy_price])

        for _, row in period_actions[period_actions['action'] == 'Sell'].iterrows():
            stock = row['stock_name']
            sell_amount = row['amount']
            sell_price = price_lookup.get((stock, period - 1), None)
            if sell_price is None or stock not in portfolio:
                continue

            remaining = sell_amount
            updated_lots = portfolio[stock][:-1]
            lifo_stack = portfolio[stock][::-1] 

            new_lots = []
            for lot in lifo_stack:
                if remaining == 0:
                    new_lots.append(lot)
                    continue

                lot_period, lot_amount, lot_price = lot
                sell_now = min(lot_amount, remaining)
                pnl = (sell_price - lot_price) * sell_now

                if pnl > 0:
                    real_gewinn += 1
                elif pnl < 0:
                    real_verlust += 1

                if lot_amount > sell_now:
                    new_lots.append([lot_period, lot_amount - sell_now, lot_price])
                remaining -= sell_now

            portfolio[stock] = new_lots[::-1]
            if not portfolio[stock]:
                del portfolio[stock]

        for stock in list(portfolio.keys()):
            current_price = price_lookup.get((stock, period), None)
            if current_price is None:
                continue
            for lot_period, lot_amount, lot_price in portfolio[stock]:
                if current_price > lot_price:
                    pot_gewinn += 1
                elif current_price < lot_price:
                    pot_verlust += 1

    results.append({
        'user_id': user,
        'pot_gain': pot_gewinn,
        'pot_loss': pot_verlust,
        'real_gain': real_gewinn,
        'real_loss': real_verlust,
    })

result_df = pd.DataFrame(results)

result_df['PGR'] = result_df['real_gain'] / (result_df['real_gain'] + result_df['pot_gain'])
result_df['PLR'] = result_df['real_loss'] / (result_df['real_loss'] + result_df['pot_loss'])

result_df['PGR'] = result_df['PGR'].fillna(0)
result_df['PLR'] = result_df['PLR'].fillna(0)

result_df.to_csv("transdata_de_lifo.csv", index=False)

