import pandas as pd

file_path = "rawdata_action_rows_wotreat.csv" 
df = pd.read_csv(file_path)

df["action"] = df["action"].str.capitalize() 

stocks = df["stock_name"].unique()

pivot = df.pivot_table(
    index=["user_id", "group"],
    columns=["stock_name", "action"],
    values="price",
    aggfunc="mean"
)

pivot.columns = [f"{stock}_{action.upper()}" for stock, action in pivot.columns]

result = pivot.reset_index()

result.to_csv("transdata_ee.csv", index=False, float_format="%.2f", encoding="utf-8-sig")

