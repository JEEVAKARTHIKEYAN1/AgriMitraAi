import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# 1. Load Data
DATA_PATH = r"E:\SRI PROJECT\AgriMitraAI\SoilTesting\data\dataset1.csv"
print(f"Loading data from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print("Dataset Loaded Successfully!")

# 2. Define Features and Targets
# Inputs available from user
feature_cols = [
    'N', 'P', 'K', 'pH', 'EC', 'OC', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'B',
    'Moisture', 'Annual_Rainfall', 'Temperature'
]

X = df[feature_cols]
y_output = df['Output']        # Target 1
y_soil_type = df['Soil_Type']  # Target 2

print(f"Features: {feature_cols}")

# 3. Preprocessing (Scaling)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Train Model 1: Crop/Output Prediction
print("\nTraining Output Model...")
X_train_out, X_test_out, y_train_out, y_test_out = train_test_split(X_scaled, y_output, test_size=0.2, random_state=42)
model_output = RandomForestClassifier(n_estimators=100, random_state=42)
model_output.fit(X_train_out, y_train_out)

y_pred_out = model_output.predict(X_test_out)
print(f"Output Model Accuracy: {accuracy_score(y_test_out, y_pred_out)}")

# 5. Train Model 2: Soil Type Prediction
print("\nTraining Soil Type Model...")
X_train_type, X_test_type, y_train_type, y_test_type = train_test_split(X_scaled, y_soil_type, test_size=0.2, random_state=42)
model_type = RandomForestClassifier(n_estimators=100, random_state=42)
model_type.fit(X_train_type, y_train_type)

y_pred_type = model_type.predict(X_test_type)
print(f"Soil Type Model Accuracy: {accuracy_score(y_test_type, y_pred_type)}")
print(classification_report(y_test_type, y_pred_type))

# 6. Save Artifacts
SAVE_DIR = r"E:\SRI PROJECT\AgriMitraAI\SoilTesting"
joblib.dump(model_output, f"{SAVE_DIR}\\soil_model.pkl")       # Main Output Model
joblib.dump(model_type, f"{SAVE_DIR}\\type_model.pkl")         # Soil Type Model
joblib.dump(scaler, f"{SAVE_DIR}\\scaler.pkl")                 # Scaler
joblib.dump(feature_cols, f"{SAVE_DIR}\\model_columns.pkl")    # Columns list

print("\nAll models and artifacts saved successfully!")
