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

start_period = 6
end_period = 14

unique_users = action_rows['user_id'].unique()
results = []

for user in unique_users:
    user_actions = action_rows[action_rows['user_id'] == user]

    portfolio = defaultdict(lambda: {'amount': 0, 'avg_price': 0.0})

    pot_gewinn = 0
    pot_verlust = 0
    real_gewinn = 0
    real_verlust = 0

    for period in range(start_period, end_period + 1):
        period_actions = user_actions[user_actions['period'] == period]

        for _, row in period_actions[period_actions['action'] == 'Buy'].iterrows():
            stock = row['stock_name']
            buy_amount = row['amount']
            buy_price = price_lookup.get((stock, period - 1), None)
            if buy_price is None:
                continue

            existing = portfolio[stock]
            total_cost = existing['amount'] * existing['avg_price'] + buy_amount * buy_price
            total_amount = existing['amount'] + buy_amount
            portfolio[stock]['amount'] = total_amount
            portfolio[stock]['avg_price'] = total_cost / total_amount

        for _, row in period_actions[period_actions['action'] == 'Sell'].iterrows():
            stock = row['stock_name']
            sell_amount = row['amount']
            sell_price = price_lookup.get((stock, period - 1), None)
            if sell_price is None or portfolio[stock]['amount'] == 0:
                continue

            avg_price = portfolio[stock]['avg_price']
            pnl = (sell_price - avg_price) * sell_amount
            if pnl > 0:
                real_gewinn += 1
            elif pnl < 0:
                real_verlust += 1

            portfolio[stock]['amount'] -= sell_amount
            if portfolio[stock]['amount'] <= 0:
                del portfolio[stock]

        for stock in list(portfolio.keys()):
            current_price = price_lookup.get((stock, period), None)
            if current_price is None:
                continue

            avg_price = portfolio[stock]['avg_price']
            if current_price > avg_price:
                pot_gewinn += 1
            elif current_price < avg_price:
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

result_df.to_csv("transdata_de_avg.csv", index=False)

