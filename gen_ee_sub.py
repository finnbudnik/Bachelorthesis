import pandas as pd
import numpy as np

df = pd.read_csv("rawdata_action_rows_wotreat.csv")
users = pd.read_csv("rawdata_merged.csv")

df = df.merge(users[["user_id", "gender"]], on="user_id", how="left")
df = df[df["gender"].str.lower() == 'female']

np.random.seed(7)  
user_ids = df["user_id"].unique()
sampled_users = np.random.choice(user_ids, size=79, replace=True)

df_bootstrap = df[df["user_id"].isin(sampled_users)].copy()

df_bootstrap["action"] = df_bootstrap["action"].str.capitalize()

stocks = df_bootstrap["stock_name"].unique()
pivot = df_bootstrap.pivot_table(
    index=["user_id", "group"],
    columns=["stock_name", "action"],
    values="price",
    aggfunc="mean"
)
pivot.columns = [f"{stock}_{action.upper()}" for stock, action in pivot.columns]
result = pivot.reset_index()

if len(result) < 79:
    user_counts = pd.Series(sampled_users).value_counts()
    rows = []
    for user_id, count in user_counts.items():
        row = result[result["user_id"] == user_id]
        rows.extend([row.copy() for _ in range(count)])
    result = pd.concat(rows, ignore_index=True)
    result = result.head(79)

result.to_csv("transdata_ee_female.csv", index=False, float_format="%.2f", encoding="utf-8-sig")
