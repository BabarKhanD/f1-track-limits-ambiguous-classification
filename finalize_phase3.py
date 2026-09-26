import pandas as pd

df = pd.read_csv(r'D:\f1-research\data\phase3_features_fixed.csv')

feature_cols = [
    'max_speed', 'min_speed', 'avg_speed', 'max_throttle', 'avg_brake',
    'brake_points', 'speed_ratio', 'avg_speed_ratio',
    'is_sprint', 'is_qualifying', 'is_race', 'is_practice', 'post_2022_regs'
]

meta_cols = ['year', 'race', 'session', 'driver', 'lap', 'turn', 'label']

final_df = df[meta_cols + feature_cols].copy()

circuit_dummies = pd.get_dummies(final_df['race'], prefix='circuit')
final_df = pd.concat([final_df, circuit_dummies], axis=1)

final_df.to_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv', index=False)

print(f"Final shape: {final_df.shape}")
print(f"Total columns: {list(final_df.columns)}")
print(f"\nLabel distribution:\n{final_df['label'].value_counts()}")
print(f"\nMissing values per column:\n{final_df[feature_cols].isna().sum()}")