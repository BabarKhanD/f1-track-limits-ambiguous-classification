import pandas as pd

df = pd.read_csv(r'D:\f1-research\data\telemetry_features.csv')
before = len(df)

df = df[(df['num_points'] <= 2000) & (df['avg_speed'] >= 50)]
after = len(df)

print(f"Removed {before - after} rows (bloated telemetry or near-zero speed), {after} remain")
print(df['label'].value_counts())

df.to_csv(r'D:\f1-research\data\telemetry_features_clean.csv', index=False)
print("Saved to telemetry_features_clean.csv")