import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report

df = pd.read_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv')

meta_cols = ['year', 'race', 'session', 'driver', 'lap', 'turn', 'label']
session_cols = ['is_sprint', 'is_qualifying', 'is_race', 'is_practice']
feature_cols = [c for c in df.columns if c not in meta_cols and c not in session_cols]

X = df[feature_cols].values
y = (df['label'] == 'clear_violation').astype(int).values
groups = df['race'].values

gss1 = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=42)
train_idx, temp_idx = next(gss1.split(X, y, groups))
X_temp, y_temp, groups_temp = X[temp_idx], y[temp_idx], groups[temp_idx]
gss2 = GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=42)
val_idx_rel, test_idx_rel = next(gss2.split(X_temp, y_temp, groups_temp))

X_train, y_train = X[train_idx], y[train_idx]
X_test, y_test = X_temp[test_idx_rel], y_temp[test_idx_rel]

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

model = RandomForestClassifier(class_weight='balanced', n_estimators=200, random_state=42)
model.fit(X_train_s, y_train)
preds = model.predict(X_test_s)

print("=== ABLATION: NO SESSION-TYPE FEATURES ===")
print(f"Features used: {feature_cols}")
print(f"\nAccuracy: {accuracy_score(y_test, preds):.4f}")
print(f"F1: {f1_score(y_test, preds):.4f}")
print(f"F1 (macro): {f1_score(y_test, preds, average='macro'):.4f}")
print()
print(classification_report(y_test, preds, target_names=['no_advantage','clear_violation']))

print("\n=== COMPARISON ===")
print("With session-type features (original): Accuracy 0.893, F1 macro 0.887")
print(f"Without session-type features (ablation): Accuracy {accuracy_score(y_test, preds):.4f}, F1 macro {f1_score(y_test, preds, average='macro'):.4f}")