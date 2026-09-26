import pandas as pd
import glob

files = glob.glob(r'D:\f1-research\data\labels_*.csv')
print(f"Found {len(files)} label files:\n")

all_dfs = []
for f in files:
    df = pd.read_csv(f)
    print(f"{f}: {len(df)} rows")
    all_dfs.append(df)

combined = pd.concat(all_dfs, ignore_index=True)
combined.to_csv(r'D:\f1-research\data\labels_combined.csv', index=False)

print(f"\n=== TOTAL: {len(combined)} rows ===")
print("\nLabel breakdown:")
print(combined['label'].value_counts())
print("\nBreakdown by year:")
print(combined.groupby(['year', 'label']).size())