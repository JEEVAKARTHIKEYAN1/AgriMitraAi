import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# 1. Load Data
DATA_PATH = r"E:\SRI PROJECT\AgriMitraAI\SoilTesting\data\dataset1.csv"
print(f"Loading data from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print("Dataset Loaded Successfully!")

# 2. Define Features and Targets
feature_cols = [
    'N', 'P', 'K', 'pH', 'EC', 'OC', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'B',
    'Moisture'
]

X = df[feature_cols]
y_output = df['Output']        # Target 1

print(f"Features: {feature_cols}")

# Compute Medians for Imputation in Production (from raw features, before scaling)
medians = X.median().to_dict()

# 3. Train/Test Split (BEFORE scaling to prevent data leakage)
X_train_raw, X_test_raw, y_train_out, y_test_out = train_test_split(X, y_output, test_size=0.2, random_state=42)

# 4. Preprocessing (Scaling: fit ONLY on train, transform both)
scaler = StandardScaler()
X_train_out = scaler.fit_transform(X_train_raw)
X_test_out = scaler.transform(X_test_raw)

# 5. Train Model
print("\nTraining Output Model...")
model_output = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42
)

# Cross-Validation
cv_scores = cross_val_score(model_output, X_train_out, y_train_out, cv=5)
print(f"5-Fold CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

model_output.fit(X_train_out, y_train_out)

# 6. Evaluation
y_train_pred = model_output.predict(X_train_out)
y_test_pred = model_output.predict(X_test_out)

print("\n--- Evaluation ---")
print(f"Train Accuracy: {accuracy_score(y_train_out, y_train_pred):.4f}")
print(f"Test Accuracy: {accuracy_score(y_test_out, y_test_pred):.4f}")

print("\nClassification Report (Test):")
print(classification_report(y_test_out, y_test_pred))

# 7. Feature Importance
print("\n--- Feature Importance ---")
importances = model_output.feature_importances_
importance_df = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print(importance_df.to_string(index=False))

# 8. Save Artifacts
SAVE_DIR = r"E:\SRI PROJECT\AgriMitraAI\SoilTesting"
joblib.dump(model_output, f"{SAVE_DIR}\\soil_model.pkl")       # Main Output Model
joblib.dump(scaler, f"{SAVE_DIR}\\scaler.pkl")                 # Scaler
joblib.dump(feature_cols, f"{SAVE_DIR}\\model_columns.pkl")    # Columns list
joblib.dump(medians, f"{SAVE_DIR}\\medians.pkl")                # Medians for Imputation

print("\nAll models and artifacts saved successfully!")
