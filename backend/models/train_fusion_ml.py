import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# =========================
# PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "DATIS_full_dataset_10000.csv"
MODEL_PATH = Path(__file__).resolve().parent / "fusion_ml_model.joblib"

# =========================
# LOAD DATA
# =========================

df = pd.read_csv(DATA_PATH)
df.columns = [c.lower().strip() for c in df.columns]

print("Initial shape:", df.shape)

# =========================
# FEATURES (FUSION)
# =========================

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

# =========================
# CLEAN DATA
# =========================

for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df[target] = df[target].astype(str).str.upper().str.strip()

df = df.dropna(subset=features + [target])
df = df.drop_duplicates()

print("After cleaning:", df.shape)

# =========================
# SPLIT
# =========================

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# =========================
# MODEL
# =========================

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=15,
    min_samples_split=5,
    random_state=42,
    class_weight="balanced",
)

model.fit(X_train, y_train)

# =========================
# EVALUATION
# =========================

pred = model.predict(X_test)

print("\n✅ Accuracy:", accuracy_score(y_test, pred))

print("\n📊 Classification Report:\n", classification_report(y_test, pred))

print("\n📉 Confusion Matrix:")
print(confusion_matrix(y_test, pred, labels=["BUY", "HOLD", "SELL"]))

# =========================
# FEATURE IMPORTANCE
# =========================

importances = model.feature_importances_
print("\n🔥 Feature Importance:")

for f, imp in zip(features, importances):
    print(f"{f}: {round(float(imp), 4)}")

# =========================
# SAVE MODEL
# =========================

joblib.dump(
    {
        "model": model,
        "features": features,
        "labels": ["BUY", "HOLD", "SELL"],
    },
    MODEL_PATH,
)

print("\n✅ Model saved at:", MODEL_PATH)