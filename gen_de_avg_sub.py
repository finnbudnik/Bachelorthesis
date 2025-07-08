import pandas as pd

df_de_avg = pd.read_csv("transdata_de_avg.csv")
df_merged = pd.read_csv("rawdata_merged.csv")

df_combined = pd.merge(df_de_avg, df_merged[['user_id', 'experience']], on='user_id')

#df_young = df_combined[df_combined['gender'].str.lower() == 'male']
#df_young = df_combined[df_combined['age'] <=22]
df_young = df_combined[df_combined['experience'] <=4] #DEPENDS ON INVESTIGATED SUBGROUP

columns_to_keep = df_de_avg.columns
df_young_filtered = df_young[columns_to_keep]

target_size = 79

df_bootstrap_sample = df_young_filtered.sample(n=target_size, replace=True, random_state=7)

df_bootstrap_sample.to_csv("transdata_de_avg_amateur.csv", index=False) #INSERT NAME

