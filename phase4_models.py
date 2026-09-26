import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report
from xgboost import XGBClassifier

df = pd.read_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv')

meta_cols = ['year', 'race', 'session', 'driver', 'lap', 'turn', 'label']
feature_cols = [c for c in df.columns if c not in meta_cols]

X = df[feature_cols].values
y = (df['label'] == 'clear_violation').astype(int).values
groups = df['race'].values

# Split by race: 70% train, 15% val, 15% test
gss1 = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=42)
train_idx, temp_idx = next(gss1.split(X, y, groups))

X_temp, y_temp, groups_temp = X[temp_idx], y[temp_idx], groups[temp_idx]
gss2 = GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=42)
val_idx_rel, test_idx_rel = next(gss2.split(X_temp, y_temp, groups_temp))

X_train, y_train = X[train_idx], y[train_idx]
X_val, y_val = X_temp[val_idx_rel], y_temp[val_idx_rel]
X_test, y_test = X_temp[test_idx_rel], y_temp[test_idx_rel]

print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_val_s = scaler.transform(X_val)
X_test_s = scaler.transform(X_test)

models = {
    'Logistic Regression': LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(class_weight='balanced', n_estimators=200, random_state=42),
    'XGBoost': XGBClassifier(scale_pos_weight=(y_train==0).sum()/(y_train==1).sum(), random_state=42, eval_metric='logloss'),
    'SVM': SVC(class_weight='balanced', kernel='rbf', random_state=42),
    'MLP': MLPClassifier(hidden_layer_sizes=(64,32), max_iter=500, random_state=42),
}

results = []
for name, model in models.items():
    model.fit(X_train_s, y_train)
    preds = model.predict(X_val_s)
    acc = accuracy_score(y_val, preds)
    f1 = f1_score(y_val, preds)
    f1_macro = f1_score(y_val, preds, average='macro')
    results.append({'model': name, 'val_accuracy': acc, 'val_f1': f1, 'val_f1_macro': f1_macro})
    print(f"\n=== {name} ===")
    print(f"Accuracy: {acc:.4f}  F1: {f1:.4f}  F1(macro): {f1_macro:.4f}")
    print(classification_report(y_val, preds, target_names=['no_advantage','clear_violation']))

results_df = pd.DataFrame(results).sort_values('val_f1_macro', ascending=False)
print("\n\n=== MODEL COMPARISON (sorted by F1 macro) ===")
print(results_df.to_string(index=False))
results_df.to_csv(r'D:\f1-research\results\phase4_model_comparison.csv', index=False)

import joblib
joblib.dump(scaler, r'D:\f1-research\results\scaler.pkl')
np.save(r'D:\f1-research\results\test_indices.npy', test_idx_rel)
print("\nSaved comparison results and scaler")