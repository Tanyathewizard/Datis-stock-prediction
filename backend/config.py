"""
config.py — Central configuration for DATIS backend.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

load_dotenv(PROJECT_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATASET_DIR = PROJECT_DIR / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

APP_TITLE = "DATIS — AI Trading Intelligence API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "Decentralized AI Trading Intelligence System. Provides fusion-based "
    "machine learning prediction, FinBERT sentiment analysis, anomaly detection, "
    "Bayesian fusion, explainability, portfolio simulation, and trust scoring."
)

CORS_ORIGINS = [
    "*",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
NEWS_API_URL = "https://newsapi.org/v2/everything"

PRICE_LOOKBACK_WINDOW = 60
PRICE_LSTM_HIDDEN = 64
PRICE_LSTM_LAYERS = 2

ANOMALY_CONTAMINATION = 0.05
ANOMALY_N_ESTIMATORS = 100

PRIOR_BUY = 0.33
PRIOR_HOLD = 0.34
PRIOR_SELL = 0.33

WEIGHT_PRICE = 0.45
WEIGHT_SENTIMENT = 0.35
WEIGHT_ANOMALY = 0.20

CONFIDENCE_HIGH = 0.70
CONFIDENCE_MEDIUM = 0.50

DUMMY_SEED = 42