import pandas as pd
import numpy as np
import joblib
import shap
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt

df = pd.read_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv')

meta_cols = ['year', 'race', 'session', 'driver', 'lap', 'turn', 'label']
feature_cols = [c for c in df.columns if c not in meta_cols]

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

scaler = joblib.load(r'D:\f1-research\results\scaler.pkl')
X_train_s = scaler.transform(X_train)
X_test_s = scaler.transform(X_test)

model = RandomForestClassifier(class_weight='balanced', n_estimators=200, random_state=42)
model.fit(X_train_s, y_train)

preds = model.predict(X_test_s)

print("=== FINAL TEST SET RESULTS (Random Forest) ===")
print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
print(f"F1: {f1_score(y_test, preds):.4f}")
print(f"F1 (macro): {f1_score(y_test, preds, average='macro'):.4f}")
print()
print(classification_report(y_test, preds, target_names=['no_advantage','clear_violation']))

cm = confusion_matrix(y_test, preds)
print("Confusion Matrix:")
print(cm)

plt.figure(figsize=(5,4))
plt.imshow(cm, cmap='Blues')
plt.colorbar()
plt.xticks([0,1], ['no_advantage','clear_violation'])
plt.yticks([0,1], ['no_advantage','clear_violation'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i,j], ha='center', va='center')
plt.title('Confusion Matrix - Test Set')
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\confusion_matrix.png')
print("\nSaved confusion_matrix.png")

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test_s)

shap_vals_for_plot = shap_values[1] if isinstance(shap_values, list) else shap_values

plt.figure()
shap.summary_plot(shap_vals_for_plot, X_test_s, feature_names=feature_cols, show=False)
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\shap_summary.png')
print("Saved shap_summary.png")

joblib.dump(model, r'D:\f1-research\results\final_model_rf.pkl')
print("Saved final trained model")