import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import joblib


DATASET_PATH = "Crop_recommendation.csv"
FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COL = "label"
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5


def load_dataset(path):
    df = pd.read_csv(path)
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"[WARNING] Found {missing} missing values. Dropping affected rows.")
        df.dropna(inplace=True)
    return df


def preprocess(df):
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    return X, y_encoded, le


def split_data(X, y):
    return train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )


def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler


def build_models():
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=RANDOM_STATE
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=10, random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, random_state=RANDOM_STATE
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100,
            random_state=RANDOM_STATE,
            eval_metric="mlogloss",
            verbosity=0,
        ),
    }


def run_cross_validation(models, X_train, y_train):
    print("\n" + "=" * 60)
    print("5-FOLD CROSS-VALIDATION RESULTS (on training set)")
    print("=" * 60)
    cv_results = {}
    for name, model in models.items():
        scores = cross_val_score(
            model, X_train, y_train, cv=CV_FOLDS, scoring="accuracy"
        )
        cv_results[name] = scores
        print(f"\n{name}")
        print(f"  CV Scores  : {np.round(scores, 4)}")
        print(f"  Mean       : {scores.mean():.4f}")
        print(f"  Std Dev    : {scores.std():.4f}")
    return cv_results


def train_models(models, X_train, y_train):
    trained = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        trained[name] = model
    return trained


def evaluate_models(trained_models, X_train, y_train, X_test, y_test, le):
    print("\n" + "=" * 60)
    print("TRAIN vs TEST SET EVALUATION RESULTS")
    print("=" * 60)
    results = {}
    for name, model in trained_models.items():
        # Predict on train
        y_train_pred = model.predict(X_train)
        train_acc = accuracy_score(y_train, y_train_pred)
        
        # Predict on test
        y_test_pred = model.predict(X_test)
        test_acc = accuracy_score(y_test, y_test_pred)
        
        report = classification_report(y_test, y_test_pred, target_names=le.classes_)
        results[name] = {"train_accuracy": train_acc, "test_accuracy": test_acc, "report": report, "y_pred": y_test_pred}
        print(f"\n--- {name} ---")
        print(f"Train Accuracy : {train_acc:.4f}")
        print(f"Test Accuracy  : {test_acc:.4f}")
        print("Classification Report (Test Set):")
        print(report)
    return results


def identify_best_model(cv_results):
    best_name = max(cv_results, key=lambda n: cv_results[n].mean())
    print("\n" + "=" * 60)
    print(f"BEST MODEL (by CV Mean Accuracy): {best_name}")
    print(f"  Mean CV Accuracy: {cv_results[best_name].mean():.4f}")
    print("=" * 60)
    return best_name


def plot_confusion_matrix(model, X_test, y_test, le, model_name):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(14, 11))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        xticklabels=le.classes_,
        yticklabels=le.classes_,
    )
    plt.title(f"Confusion Matrix — {model_name}", fontsize=14, fontweight="bold")
    plt.xlabel("Predicted Label", fontsize=12)
    plt.ylabel("True Label", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=150)
    print("\nConfusion matrix saved to confusion_matrix.png")


def plot_feature_importance(model, model_name):
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    sorted_features = [FEATURE_COLS[i] for i in indices]
    sorted_importances = importances[indices]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(sorted_features, sorted_importances, color="steelblue")
    plt.title(f"{model_name} — Feature Importances", fontsize=13, fontweight="bold")
    plt.xlabel("Feature", fontsize=11)
    plt.ylabel("Importance Score", fontsize=11)
    for bar, val in zip(bars, sorted_importances):
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.002,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    plt.savefig("feature_importance.png", dpi=150)

    print(f"\nFeature Importances ({model_name}):")
    for feat, imp in zip(sorted_features, sorted_importances):
        print(f"  {feat:<15}: {imp:.4f}")
    print("Feature importance plot saved to feature_importance.png")


def plot_learning_curve(model, X_train, y_train, model_name):
    train_sizes, train_scores, val_scores = learning_curve(
        model,
        X_train,
        y_train,
        cv=CV_FOLDS,
        scoring="accuracy",
        train_sizes=np.linspace(0.1, 1.0, 10),
        random_state=RANDOM_STATE,
    )

    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)

    plt.figure(figsize=(9, 6))
    plt.plot(train_sizes, train_mean, "o-", color="royalblue", label="Training Score")
    plt.fill_between(
        train_sizes,
        train_mean - train_std,
        train_mean + train_std,
        alpha=0.15,
        color="royalblue",
    )
    plt.plot(
        train_sizes, val_mean, "s-", color="tomato", label="Cross-Validation Score"
    )
    plt.fill_between(
        train_sizes,
        val_mean - val_std,
        val_mean + val_std,
        alpha=0.15,
        color="tomato",
    )
    plt.title(
        f"Learning Curve — {model_name}", fontsize=13, fontweight="bold"
    )
    plt.xlabel("Training Set Size", fontsize=11)
    plt.ylabel("Accuracy", fontsize=11)
    plt.legend(loc="lower right", fontsize=10)
    plt.ylim(0.5, 1.05)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("learning_curve.png", dpi=150)
    print("Learning curve plot saved to learning_curve.png")


def save_artifacts(model, scaler, le):
    joblib.dump(model, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(le, 'label_encoder.pkl')
    print("\n[INFO] Best model, scaler, and label encoder successfully saved for the API!")


def main():
    print("Loading dataset...")
    df = load_dataset(DATASET_PATH)
    print(f"Dataset shape: {df.shape}")
    print(f"Classes: {sorted(df[TARGET_COL].unique())}")
    print(f"Class distribution:\n{df[TARGET_COL].value_counts().to_string()}")

    X, y, le = preprocess(df)

    X_train, X_test, y_train, y_test = split_data(X, y)
    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

    X_train_sc, X_test_sc, scaler = scale_features(X_train, X_test)

    models = build_models()

    cv_results = run_cross_validation(models, X_train_sc, y_train)

    best_model_name = identify_best_model(cv_results)

    trained_models = train_models(models, X_train_sc, y_train)

    evaluate_models(trained_models, X_train_sc, y_train, X_test_sc, y_test, le)

    best_model = trained_models[best_model_name]
    plot_confusion_matrix(best_model, X_test_sc, y_test, le, best_model_name)

    # Feature importances are only available for tree-based models
    if best_model_name in ["Random Forest", "Decision Tree", "XGBoost"]:
        print(f"\nGenerating feature importance for the best model ({best_model_name})...")
        plot_feature_importance(best_model, best_model_name)
    else:
        print(f"\nSkipping feature importances because {best_model_name} does not natively support them.")

    print(f"\nGenerating learning curve for the best model ({best_model_name}) (this may take a moment)...")
    plot_learning_curve(best_model, X_train_sc, y_train, best_model_name)
    
    # Save the artifacts for deployment
    save_artifacts(best_model, scaler, le)

    print("\n✅ Pipeline completed.")


if __name__ == "__main__":
    main()
