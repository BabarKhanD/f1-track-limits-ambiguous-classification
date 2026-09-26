import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, f1_score

df = pd.read_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv')
meta_cols = ['year', 'race', 'session', 'driver', 'lap', 'turn', 'label']
feature_cols = [c for c in df.columns if c not in meta_cols]

model = joblib.load(r'D:\f1-research\results\final_model_rf.pkl')
scaler = joblib.load(r'D:\f1-research\results\scaler.pkl')

X = df[feature_cols].values
y = (df['label'] == 'clear_violation').astype(int).values
groups = df['race'].values

gss1 = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=42)
train_idx, temp_idx = next(gss1.split(X, y, groups))
X_temp, y_temp, groups_temp = X[temp_idx], y[temp_idx], groups[temp_idx]
gss2 = GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=42)
val_idx_rel, test_idx_rel = next(gss2.split(X_temp, y_temp, groups_temp))

X_test, y_test = X_temp[test_idx_rel], y_temp[test_idx_rel]
test_df = df.iloc[temp_idx].iloc[test_idx_rel].copy()

X_test_s = scaler.transform(X_test)
preds = model.predict(X_test_s)

test_df['pred'] = preds
test_df['actual'] = y_test
test_df['correct'] = (preds == y_test)

print("=== ACCURACY BY REGULATION ERA ===")
for era, label in [(0, 'Pre-2022 (old regs)'), (1, 'Post-2022 (new regs)')]:
    subset = test_df[test_df['post_2022_regs'] == era]
    if len(subset) == 0:
        continue
    acc = accuracy_score(subset['actual'], subset['pred'])
    f1m = f1_score(subset['actual'], subset['pred'], average='macro')
    print(f"{label}: n={len(subset)}, Accuracy={acc:.4f}, F1 macro={f1m:.4f}")

print("\n=== ACCURACY BY YEAR ===")
for yr in sorted(test_df['year'].unique()):
    subset = test_df[test_df['year'] == yr]
    if len(subset) == 0:
        continue
    acc = accuracy_score(subset['actual'], subset['pred'])
    print(f"{yr}: n={len(subset)}, Accuracy={acc:.4f}")