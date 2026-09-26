import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve

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
X_test_s = scaler.transform(X_test)

preds = model.predict(X_test_s)
probs = model.predict_proba(X_test_s)[:, 1]

# 1. Confusion Matrix
cm = confusion_matrix(y_test, preds)
plt.figure(figsize=(5,4))
plt.imshow(cm, cmap='Blues')
plt.colorbar()
plt.xticks([0,1], ['no_advantage','clear_violation'])
plt.yticks([0,1], ['no_advantage','clear_violation'])
plt.xlabel('Predicted'); plt.ylabel('Actual')
for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i,j], ha='center', va='center')
plt.title('Confusion Matrix - Test Set')
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\confusion_matrix.png', dpi=150)
plt.close()
print("Saved confusion_matrix.png")

# 2 & 3. SHAP plots
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test_s)
if isinstance(shap_values, list):
    vals = shap_values[1]
else:
    vals = shap_values[:, :, 1] if shap_values.ndim == 3 else shap_values

plt.figure()
shap.summary_plot(vals, X_test_s, feature_names=feature_cols, show=False, max_display=15)
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\shap_summary.png', dpi=150)
plt.close()
print("Saved shap_summary.png")

plt.figure()
shap.summary_plot(vals, X_test_s, feature_names=feature_cols, show=False, max_display=15, plot_type='bar')
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\shap_bar.png', dpi=150)
plt.close()
print("Saved shap_bar.png")

# 4. ROC Curve
fpr, tpr, _ = roc_curve(y_test, probs)
roc_auc = auc(fpr, tpr)
plt.figure(figsize=(5,5))
plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.3f}')
plt.plot([0,1],[0,1],'--',color='gray')
plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate')
plt.title('ROC Curve'); plt.legend()
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\roc_curve.png', dpi=150)
plt.close()
print(f"Saved roc_curve.png (AUC={roc_auc:.3f})")

# 5. Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, probs)
plt.figure(figsize=(5,5))
plt.plot(recall, precision)
plt.xlabel('Recall'); plt.ylabel('Precision')
plt.title('Precision-Recall Curve (clear_violation)')
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\pr_curve.png', dpi=150)
plt.close()
print("Saved pr_curve.png")

# 6. Model comparison bar chart
comp = pd.read_csv(r'D:\f1-research\results\phase4_model_comparison.csv')
plt.figure(figsize=(7,5))
x = np.arange(len(comp))
plt.bar(x-0.2, comp['val_accuracy'], width=0.2, label='Accuracy')
plt.bar(x, comp['val_f1'], width=0.2, label='F1')
plt.bar(x+0.2, comp['val_f1_macro'], width=0.2, label='F1 macro')
plt.xticks(x, comp['model'], rotation=30, ha='right')
plt.ylabel('Score'); plt.title('Model Comparison (Validation Set)')
plt.legend()
plt.tight_layout()
plt.savefig(r'D:\f1-research\results\model_comparison.png', dpi=150)
plt.close()
print("Saved model_comparison.png")

# 7. Dataset distribution by year
year_counts = df.groupby(['year','label']).size().unstack(fill_value=0)
year_counts.plot(kind='bar', stacked=True, figsize=(8,5))
plt.ylabel('Count'); plt.title('Dataset Distribution by Year')
plt.xlabel('Year'); plt.tight_layout()
plt.savefig(r'D:\f1-research\results\dataset_by_year.png', dpi=150)
plt.close()
print("Saved dataset_by_year.png")

print("\nALL GRAPHS SAVED to results/")