import pandas as pd

df = pd.read_csv(r'D:\f1-research\data\phase3_features.csv')

session_peak = df.groupby(['year', 'race', 'session'])['max_speed'].transform('max')
session_avg = df.groupby(['year', 'race', 'session'])['avg_speed'].transform('mean')

df['speed_ratio'] = df['max_speed'] / session_peak
df['avg_speed_ratio'] = df['avg_speed'] / session_avg

df.to_csv(r'D:\f1-research\data\phase3_features_fixed.csv', index=False)
print(df[['speed_ratio', 'avg_speed_ratio']].describe())