import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

df = pd.read_csv(r'D:\f1-research\data\dataset_ready_for_modeling.csv')
X = df.drop(columns=['label']).values
y = (df['label'] == 'clear_violation').astype(int).values
groups = df['race'].values

gss1 = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=42)
train_idx, temp_idx = next(gss1.split(X, y, groups))
X_temp, y_temp, groups_temp = X[temp_idx], y[temp_idx], groups[temp_idx]

gss2 = GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=42)
val_idx_rel, test_idx_rel = next(gss2.split(X_temp, y_temp, groups_temp))

test_df = df.iloc[temp_idx].iloc[test_idx_rel]
print(pd.crosstab(test_df['year'], test_df['label']))