import pandas as pd

df = pd.read_csv(r'D:\f1-research\data\labels_final.csv')
recovered = pd.read_csv(r'D:\f1-research\data\no_advantage_with_laps.csv')

recovered = recovered[recovered['lap'].notna()]

violations = df[df['label'] == 'clear_violation'].copy()

final = pd.concat([violations, recovered], ignore_index=True)
final = final.drop_duplicates()

final.to_csv(r'D:\f1-research\data\dataset_phase1_complete.csv', index=False)

print(f"Total: {len(final)} rows")
print(final['label'].value_counts())
print("\nAll rows have lap numbers:", final['lap'].notna().all())