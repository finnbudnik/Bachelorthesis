import pandas as pd

actions_df = pd.read_csv("rawdata_action_rows.csv")
prices_df = pd.read_csv("rawdata_stock_prices.csv")

sell_actions = actions_df[actions_df['action'] == 'Sell'].copy()

sell_actions['ref_period'] = sell_actions['period'] - 1 
sell_actions['prev_period'] = sell_actions['period'] - 2 

sell_actions = sell_actions.merge(
    prices_df.rename(columns={'period': 'ref_period', 'price': 'ref_price'}),
    on=['stock_name', 'ref_period'],
    how='left'
)

sell_actions = sell_actions.merge(
    prices_df.rename(columns={'period': 'prev_period', 'price': 'prev_price'}),
    on=['stock_name', 'prev_period'],
    how='left'
)

sell_actions['S+'] = ((sell_actions['ref_price'] > sell_actions['prev_price']) * sell_actions['amount']).astype(int)
sell_actions['S-'] = ((sell_actions['ref_price'] < sell_actions['prev_price']) * sell_actions['amount']).astype(int)

disposition = sell_actions.groupby('user_id')[['S+', 'S-']].sum().reset_index()

disposition['alpha'] = (disposition['S+'] - disposition['S-']) / (disposition['S+'] + disposition['S-'])

disposition['alpha'] = disposition['alpha'].fillna(0)

disposition.to_csv("transdata_de_alpha.csv", index=False)


