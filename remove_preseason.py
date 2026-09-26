import pandas as pd

df = pd.read_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv')
before = len(df)

df = df[~df['race'].str.contains('Pre-Season', case=False, na=False)]

after = len(df)
print(f"Removed {before - after} pre-season testing rows, {after} remain")
print(df['label'].value_counts())

df.to_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv', index=False)
print("Overwritten dataset_ready_for_modeling.csv")