import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.preprocessing import StandardScaler

import joblib

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "DATIS_full_dataset_10000.csv"
MODEL_PATH = Path(__file__).resolve().parent / "price_ml_model.joblib"

# -------------------------------
# Load Dataset
# -------------------------------
df = pd.read_csv(DATA_PATH)
df.columns = [c.lower().strip() for c in df.columns]

print("Initial shape:", df.shape)

# -------------------------------
# Feature Engineering Safety
# -------------------------------
features = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "rsi",
    "macd",
    "ma20",
    "volatility",
    "sentimentscore",
    "anomalyflag",
]

target = "label"

# Convert numeric columns safely
for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Clean target
df[target] = df[target].astype(str).str.upper().str.strip()

# Remove invalid rows
df = df.dropna(subset=features + [target])

# Remove duplicates
df = df.drop_duplicates()

print("After cleaning:", df.shape)

# -------------------------------
# Split Data
# -------------------------------
X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# -------------------------------
# Scaling (optional but good)
# -------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------------------
# Train Model
# -------------------------------
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=15,
    min_samples_split=5,
    random_state=42,
    class_weight="balanced",
)

model.fit(X_train_scaled, y_train)

# -------------------------------
# Evaluation
# -------------------------------
pred = model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, pred)
print("\n✅ Accuracy:", accuracy)

print("\n📊 Classification Report:")
print(classification_report(y_test, pred))

# -------------------------------
# Confusion Matrix
# -------------------------------
cm = confusion_matrix(y_test, pred)
labels = sorted(y.unique())

print("\n📉 Confusion Matrix:")
print("Labels:", labels)
print(cm)

# -------------------------------
# Feature Importance
# -------------------------------
importance = model.feature_importances_

print("\n🔥 Feature Importance:")
for f, imp in zip(features, importance):
    print(f"{f}: {round(imp, 4)}")

# -------------------------------
# Save Model
# -------------------------------
joblib.dump(
    {
        "model": model,
        "scaler": scaler,
        "features": features,
    },
    MODEL_PATH,
)

print("\n✅ Model saved at:", MODEL_PATH)