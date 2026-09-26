import pandas as pd
import glob

files = sorted(glob.glob(r'D:\f1-research\data\labels_20*.csv'))
print(f"Found {len(files)} files\n")

all_dfs = []
for f in files:
    df = pd.read_csv(f)
    print(f"{f}: {len(df)} rows, labels: {df['label'].unique().tolist()}")
    all_dfs.append(df)

combined = pd.concat(all_dfs, ignore_index=True)

# safety check - keep only the two valid labels
before = len(combined)
combined = combined[combined['label'].isin(['clear_violation', 'no_advantage'])]
after = len(combined)
print(f"\nRemoved {before - after} rows with unexpected labels (should be 0)")

# drop exact duplicates if any
combined = combined.drop_duplicates()

combined.to_csv(r'D:\f1-research\data\labels_final.csv', index=False)
print(f"\n=== FINAL: {len(combined)} rows ===")
print(combined['label'].value_counts())
print("\nBy year:")
print(combined.groupby(['year', 'label']).size())