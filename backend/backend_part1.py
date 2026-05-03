import os
from pathlib import Path

# ── Project Paths ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent          # backend/ directory
DATA_DIR = BASE_DIR / "data"                        # where CSV files live
DATA_DIR.mkdir(exist_ok=True)                       # auto-create if missing

# ── CORS ─────────────────────────────────────────────────────────────────────
# Add your frontend's origin here. "*" allows all origins (fine for dev).
CORS_ORIGINS = [
    "*",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]

# ── Price Model Settings ─────────────────────────────────────────────────────
PRICE_LOOKBACK_WINDOW = 20          # number of OHLCV candles fed to the model
PRICE_LSTM_HIDDEN     = 64          # LSTM hidden units (used in real mode)
PRICE_LSTM_LAYERS     = 2           # LSTM stacked layers

# ── Anomaly Model Settings ───────────────────────────────────────────────────
ANOMALY_CONTAMINATION = 0.05        # expected fraction of anomalies (0–0.5)
ANOMALY_N_ESTIMATORS  = 100         # Isolation Forest trees

# ── Fusion / Bayesian Settings ───────────────────────────────────────────────
# Prior probabilities for BUY / HOLD / SELL before any model runs
PRIOR_BUY  = 0.33
PRIOR_HOLD = 0.34
PRIOR_SELL = 0.33

# Model weights — how much each model influences the final decision
WEIGHT_PRICE     = 0.45
WEIGHT_SENTIMENT = 0.35
WEIGHT_ANOMALY   = 0.20

# ── Confidence Thresholds ────────────────────────────────────────────────────
CONFIDENCE_HIGH   = 0.70            # ≥ 70%  → high conviction
CONFIDENCE_MEDIUM = 0.50            # ≥ 50%  → medium conviction
# below CONFIDENCE_MEDIUM            → low conviction → HOLD

# ── Dummy Data Seeds ─────────────────────────────────────────────────────────
# When no real CSV is available the models generate synthetic OHLCV data.
# Change this seed to get different but reproducible dummy results.
DUMMY_SEED = 42
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: utils/__init__.py
# ════════════════════════════════════════════════════════════════════════════
UTILS_INIT_PY = '''
"""
utils/__init__.py — Shared helper utilities for DATIS backend.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from config import DATA_DIR, DUMMY_SEED


def load_ohlcv(symbol: str, rows: int = 100) -> pd.DataFrame:
    """
    Load OHLCV data for a given symbol.

    Tries to read  data/<SYMBOL>.csv  first.
    Falls back to a fully synthetic DataFrame so the API never crashes
    even when no real data file exists.

    Expected CSV columns (case-insensitive):
        open, high, low, close, volume

    Args:
        symbol: Ticker string, e.g. "AAPL", "BTC"
        rows:   How many candles to return (most recent)

    Returns:
        pd.DataFrame with columns [open, high, low, close, volume]
    """
    csv_path = DATA_DIR / f"{symbol.upper()}.csv"

    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            # Normalise column names to lowercase
            df.columns = [c.lower().strip() for c in df.columns]
            required = {"open", "high", "low", "close", "volume"}
            if required.issubset(set(df.columns)):
                return df[list(required)].tail(rows).reset_index(drop=True)
        except Exception as e:
            print(f"[utils] Warning: could not read {csv_path}: {e}")

    # ── Synthetic fallback ────────────────────────────────────────────────
    rng   = np.random.default_rng(DUMMY_SEED + hash(symbol) % 10_000)
    close = 100.0 + np.cumsum(rng.normal(0, 1, rows))
    close = np.clip(close, 1, None)          # prices stay positive

    noise = rng.uniform(0.5, 2.5, rows)
    high  = close + noise
    low   = close - noise
    open_ = close + rng.uniform(-1, 1, rows)
    vol   = rng.integers(500_000, 5_000_000, rows).astype(float)

    return pd.DataFrame({
        "open":   open_,
        "high":   high,
        "low":    low,
        "close":  close,
        "volume": vol,
    })


def normalize_series(series: np.ndarray) -> np.ndarray:
    """
    Min-max normalize a 1-D numpy array to [0, 1].
    Safe: if std == 0 returns zeros instead of NaN.
    """
    mn, mx = series.min(), series.max()
    if mx == mn:
        return np.zeros_like(series, dtype=float)
    return (series - mn) / (mx - mn)


def softmax(scores: dict) -> dict:
    """
    Apply softmax to a dict of {label: raw_score}.
    Returns {label: probability} that sums to 1.
    """
    vals  = np.array(list(scores.values()), dtype=float)
    exps  = np.exp(vals - vals.max())        # numerical stability
    probs = exps / exps.sum()
    return {k: float(round(p, 4)) for k, p in zip(scores.keys(), probs)}
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: models/__init__.py
# ════════════════════════════════════════════════════════════════════════════
MODELS_INIT_PY = '# models package\n'

# ════════════════════════════════════════════════════════════════════════════
# FILE: models/price_model.py
# ════════════════════════════════════════════════════════════════════════════
PRICE_MODEL_PY = '''
"""
models/price_model.py — Price Trend Model for DATIS.

Architecture choice:
  • In PRODUCTION  → uses a real PyTorch LSTM trained on OHLCV data.
  • In DEMO / DEV  → uses a lightweight heuristic (moving-average crossover +
    momentum) that behaves realistically without requiring a trained checkpoint.

The public interface is always the same:
    predict(df: pd.DataFrame) -> dict
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from config import (
    PRICE_LOOKBACK_WINDOW,
    PRICE_LSTM_HIDDEN,
    PRICE_LSTM_LAYERS,
    DUMMY_SEED,
)


# ── PyTorch LSTM definition (used when a checkpoint is available) ─────────────

class LSTMPriceModel(nn.Module):
    """
    Stacked LSTM → fully-connected classifier.
    Input shape : (batch, seq_len, n_features=5)  → OHLCV
    Output shape: (batch, 3)                       → [up, neutral, down]
    """

    def __init__(self, input_size: int = 5, hidden: int = PRICE_LSTM_HIDDEN,
                 layers: int = PRICE_LSTM_LAYERS, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden,
            num_layers=layers,
            batch_first=True,
            dropout=dropout if layers > 1 else 0.0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 3),          # 3 classes: up / neutral / down
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        last    = out[:, -1, :]        # take the last time-step
        return self.fc(last)


# ── Heuristic fallback (no checkpoint needed) ─────────────────────────────────

def _heuristic_predict(df: pd.DataFrame) -> dict:
    """
    Moving-average crossover + RSI-style momentum.

    Logic:
      - Fast MA (5) crossing above Slow MA (20) → bullish signal
      - Momentum (close[-1] / close[-lookback] - 1) → magnitude
      - Combine to vote on up / neutral / down

    Returns a dict matching the standard interface.
    """
    close  = df["close"].values.astype(float)
    window = min(PRICE_LOOKBACK_WINDOW, len(close))

    if window < 5:
        # Not enough data — return neutral
        return {
            "trend":        "neutral",
            "up_prob":      0.33,
            "neutral_prob": 0.34,
            "down_prob":    0.33,
            "raw_signal":   0.0,
        }

    fast_ma  = float(np.mean(close[-5:]))
    slow_ma  = float(np.mean(close[-window:]))
    momentum = float((close[-1] / close[-window]) - 1.0)   # e.g. +0.03 = +3%

    # Cross-over signal: positive means fast > slow (bullish)
    cross_signal = (fast_ma - slow_ma) / (slow_ma + 1e-9)

    # Combined raw score in (-1, +1) range
    raw = 0.6 * np.tanh(cross_signal * 10) + 0.4 * np.tanh(momentum * 20)

    # Convert raw score → probabilities
    if raw > 0.15:
        trend = "up"
        p_up, p_neutral, p_down = 0.65 + raw * 0.2, 0.20, 0.15 - raw * 0.1
    elif raw < -0.15:
        trend = "down"
        p_up, p_neutral, p_down = 0.15 + raw * 0.1, 0.20, 0.65 - raw * 0.2
    else:
        trend = "neutral"
        p_up, p_neutral, p_down = 0.25, 0.50, 0.25

    # Clamp and renormalize
    probs = np.array([p_up, p_neutral, p_down], dtype=float)
    probs = np.clip(probs, 0.01, 0.98)
    probs /= probs.sum()

    return {
        "trend":        trend,
        "up_prob":      round(float(probs[0]), 4),
        "neutral_prob": round(float(probs[1]), 4),
        "down_prob":    round(float(probs[2]), 4),
        "raw_signal":   round(float(raw), 4),
    }


# ── Public API ────────────────────────────────────────────────────────────────

def predict(df: pd.DataFrame) -> dict:
    """
    Run price trend prediction on an OHLCV DataFrame.

    Tries the PyTorch LSTM first (requires a saved checkpoint at
    models/checkpoints/price_lstm.pt).  Falls back to the heuristic
    automatically if no checkpoint is found or CUDA/CPU errors occur.

    Args:
        df: DataFrame with columns [open, high, low, close, volume]

    Returns:
        {
            "trend":        "up" | "down" | "neutral",
            "up_prob":      float,
            "neutral_prob": float,
            "down_prob":    float,
            "raw_signal":   float,
            "model_used":   "lstm" | "heuristic"
        }
    """
    import os
    checkpoint = os.path.join(
        os.path.dirname(__file__), "checkpoints", "price_lstm.pt"
    )

    # ── Try LSTM path ────────────────────────────────────────────────────────
    if os.path.exists(checkpoint):
        try:
            model = LSTMPriceModel()
            model.load_state_dict(torch.load(checkpoint, map_location="cpu"))
            model.eval()

            # Prepare tensor: shape (1, seq_len, 5)
            cols  = ["open", "high", "low", "close", "volume"]
            seq   = df[cols].tail(PRICE_LOOKBACK_WINDOW).values.astype(np.float32)
            seq   = (seq - seq.mean(axis=0)) / (seq.std(axis=0) + 1e-9)  # z-score
            x     = torch.tensor(seq[np.newaxis, ...])   # add batch dim

            with torch.no_grad():
                logits = model(x)[0]                      # shape (3,)
                probs  = torch.softmax(logits, dim=0).numpy()

            labels = ["up", "neutral", "down"]
            trend  = labels[int(np.argmax(probs))]
            return {
                "trend":        trend,
                "up_prob":      round(float(probs[0]), 4),
                "neutral_prob": round(float(probs[1]), 4),
                "down_prob":    round(float(probs[2]), 4),
                "raw_signal":   round(float(probs[0] - probs[2]), 4),
                "model_used":   "lstm",
            }
        except Exception as e:
            print(f"[price_model] LSTM failed ({e}), falling back to heuristic.")

    # ── Heuristic fallback ───────────────────────────────────────────────────
    result = _heuristic_predict(df)
    result["model_used"] = "heuristic"
    return result
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: models/sentiment_model.py
# ════════════════════════════════════════════════════════════════════════════
SENTIMENT_MODEL_PY = '''
"""
models/sentiment_model.py — Sentiment Analysis Model for DATIS.

Architecture choice:
  • PRODUCTION → FinBERT (ProsusAI/finbert) via HuggingFace Transformers.
  • DEMO / DEV  → Lexicon-based scorer using a built-in financial word list.

The heuristic still produces realistic, symbol-dependent results by seeding
the random component with the symbol string so the same symbol always returns
the same sentiment (deterministic behaviour across API calls).
"""

import re
import hashlib
import numpy as np
from config import DUMMY_SEED


# ── Financial sentiment lexicon (built-in, no external files needed) ──────────

POSITIVE_WORDS = {
    "bullish", "surge", "rally", "growth", "profit", "beat", "record",
    "outperform", "upgrade", "buy", "strong", "gain", "revenue", "exceed",
    "innovation", "partnership", "dividend", "recovery", "momentum", "breakout",
    "upside", "optimistic", "robust", "expansion", "milestone",
}

NEGATIVE_WORDS = {
    "bearish", "crash", "plunge", "loss", "miss", "downgrade", "sell",
    "weak", "decline", "debt", "lawsuit", "fraud", "recall", "layoff",
    "downside", "pessimistic", "contraction", "default", "investigation",
    "warning", "risk", "volatile", "concern", "pressure", "cut",
}


def _lexicon_sentiment(text: str) -> dict:
    """
    Score text using the built-in financial lexicon.
    Returns normalised probabilities for positive / neutral / negative.
    """
    words  = set(re.findall(r"\\b[a-z]+\\b", text.lower()))
    pos    = len(words & POSITIVE_WORDS)
    neg    = len(words & NEGATIVE_WORDS)
    total  = pos + neg

    if total == 0:
        return {"positive": 0.20, "neutral": 0.60, "negative": 0.20}

    p_pos  = pos / total
    p_neg  = neg / total
    p_neu  = 1.0 - abs(p_pos - p_neg)

    probs  = np.array([p_pos, p_neu, p_neg], dtype=float)
    probs  = np.clip(probs, 0.05, 0.95)
    probs /= probs.sum()

    return {
        "positive": round(float(probs[0]), 4),
        "neutral":  round(float(probs[1]), 4),
        "negative": round(float(probs[2]), 4),
    }


def _symbol_seed_sentiment(symbol: str) -> dict:
    """
    Produce deterministic, symbol-specific sentiment when no real news text
    is available.  Uses MD5 hash of the symbol so every unique symbol gets
    a unique-but-stable result.
    """
    digest = int(hashlib.md5(symbol.upper().encode()).hexdigest(), 16)
    rng    = np.random.default_rng(digest % (2**32))

    raw = rng.dirichlet(alpha=[3, 2, 1.5])          # slight positive bias
    labels = ["positive", "neutral", "negative"]
    return {l: round(float(v), 4) for l, v in zip(labels, raw)}


# ── FinBERT wrapper (only used if transformers is installed) ──────────────────

def _finbert_sentiment(text: str) -> dict:
    """
    Run FinBERT (ProsusAI/finbert) inference.
    Returns the same format as the lexicon scorer.
    Raises ImportError if transformers is not installed.
    """
    from transformers import pipeline  # type: ignore

    pipe   = pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        return_all_scores=True,
    )
    scores = pipe(text[:512])[0]       # FinBERT max 512 tokens
    mapping = {"positive": "positive", "negative": "negative", "neutral": "neutral"}
    result  = {}
    for item in scores:
        key = mapping.get(item["label"].lower(), item["label"].lower())
        result[key] = round(float(item["score"]), 4)

    # Ensure all three keys exist
    for k in ["positive", "neutral", "negative"]:
        result.setdefault(k, 0.0)
    return result


# ── Public API ────────────────────────────────────────────────────────────────

def analyze(symbol: str, text: str | None = None) -> dict:
    """
    Analyse sentiment for a symbol / news text.

    Priority order:
      1. FinBERT  — if `transformers` is installed AND text is provided
      2. Lexicon  — if text is provided but transformers is not available
      3. Symbol seed — deterministic fallback when no text is given

    Args:
        symbol: Ticker string used for fallback seeding, e.g. "AAPL"
        text:   Optional news headline / paragraph to analyse

    Returns:
        {
            "label":     "positive" | "neutral" | "negative",
            "positive":  float,
            "neutral":   float,
            "negative":  float,
            "model_used": "finbert" | "lexicon" | "seed"
        }
    """
    probs      = {}
    model_used = "seed"

    if text:
        # Try FinBERT first
        try:
            probs      = _finbert_sentiment(text)
            model_used = "finbert"
        except (ImportError, Exception) as e:
            print(f"[sentiment_model] FinBERT unavailable ({e}), using lexicon.")
            probs      = _lexicon_sentiment(text)
            model_used = "lexicon"
    else:
        probs      = _symbol_seed_sentiment(symbol)
        model_used = "seed"

    # Determine dominant label
    label = max(probs, key=lambda k: probs[k])

    return {
        "label":      label,
        "positive":   probs.get("positive", 0.0),
        "neutral":    probs.get("neutral",  0.0),
        "negative":   probs.get("negative", 0.0),
        "model_used": model_used,
    }
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: models/anomaly_model.py
# ════════════════════════════════════════════════════════════════════════════
ANOMALY_MODEL_PY = '''
"""
models/anomaly_model.py — Anomaly Detection Model for DATIS.

Uses scikit-learn's Isolation Forest to detect unusual price/volume patterns.
The model is re-fit on-the-fly from the OHLCV data (no pre-training needed).
Anomalies indicate unusual market conditions: sudden volume spikes,
gap-up/down opens, or extreme intraday ranges.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from config import ANOMALY_CONTAMINATION, ANOMALY_N_ESTIMATORS, DUMMY_SEED


def _engineer_features(df: pd.DataFrame) -> np.ndarray:
    """
    Extract anomaly-detection features from raw OHLCV data.

    Features (all normalised to reduce scale effects):
      - intraday_range : (high - low) / close          → volatility proxy
      - gap            : (open - prev_close) / prev_close → overnight gap
      - volume_z       : z-score of volume             → volume spike
      - body_ratio     : |close - open| / (high - low) → candle body size
      - upper_shadow   : (high - max(open,close)) / close
      - lower_shadow   : (min(open,close) - low) / close

    Returns:
        numpy array of shape (n_samples, n_features)
    """
    df = df.copy().reset_index(drop=True)

    intraday  = (df["high"] - df["low"]) / (df["close"] + 1e-9)
    gap       = (df["open"] - df["close"].shift(1)) / (df["close"].shift(1) + 1e-9)
    gap       = gap.fillna(0)

    vol_mean  = df["volume"].mean()
    vol_std   = df["volume"].std() + 1e-9
    vol_z     = (df["volume"] - vol_mean) / vol_std

    hl_range  = (df["high"] - df["low"]).replace(0, 1e-9)
    body      = np.abs(df["close"] - df["open"]) / hl_range
    upper_sh  = (df["high"] - np.maximum(df["open"], df["close"])) / (df["close"] + 1e-9)
    lower_sh  = (np.minimum(df["open"], df["close"]) - df["low"])   / (df["close"] + 1e-9)

    features = np.column_stack([
        intraday.values,
        gap.values,
        vol_z.values,
        body.values,
        upper_sh.values,
        lower_sh.values,
    ])
    return np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)


def detect(df: pd.DataFrame) -> dict:
    """
    Run Isolation Forest anomaly detection on OHLCV data.

    The model is trained on the entire history and the anomaly score
    for the LATEST candle is returned.

    Args:
        df: DataFrame with columns [open, high, low, close, volume]

    Returns:
        {
            "anomaly_score":   float in [0, 1]  (1 = most anomalous),
            "is_anomaly":      bool,
            "anomaly_type":    str,              (description of what triggered it)
            "affected_candles": int              (how many recent candles are anomalous)
        }
    """
    if len(df) < 10:
        # Not enough data to train Isolation Forest
        return {
            "anomaly_score":    0.0,
            "is_anomaly":       False,
            "anomaly_type":     "insufficient_data",
            "affected_candles": 0,
        }

    features = _engineer_features(df)

    iso_forest = IsolationForest(
        n_estimators=ANOMALY_N_ESTIMATORS,
        contamination=ANOMALY_CONTAMINATION,
        random_state=DUMMY_SEED,
    )
    iso_forest.fit(features)

    # decision_function: negative = more anomalous, positive = more normal
    raw_scores = iso_forest.decision_function(features)   # shape (n,)
    predictions = iso_forest.predict(features)            # +1 normal, -1 anomaly

    # Convert decision function to [0,1] score (higher = more anomalous)
    # Raw scores typically in [-0.5, +0.5]; we map to [0, 1]
    normalized = 1.0 - (raw_scores - raw_scores.min()) / (
        raw_scores.max() - raw_scores.min() + 1e-9
    )

    latest_score   = float(normalized[-1])
    latest_pred    = int(predictions[-1])
    is_anomaly     = latest_pred == -1

    # Count how many of the last 5 candles are anomalous
    affected = int(np.sum(predictions[-5:] == -1))

    # ── Describe the anomaly type ─────────────────────────────────────────
    anomaly_type = "none"
    if is_anomaly:
        # Look at which feature drove the detection
        last_feat = features[-1]
        if abs(last_feat[2]) > 2.0:                     # volume_z
            anomaly_type = "volume_spike"
        elif abs(last_feat[1]) > 0.03:                  # gap
            anomaly_type = "price_gap"
        elif last_feat[0] > np.percentile(features[:, 0], 95):
            anomaly_type = "high_volatility"
        else:
            anomaly_type = "pattern_anomaly"

    return {
        "anomaly_score":    round(latest_score, 4),
        "is_anomaly":       is_anomaly,
        "anomaly_type":     anomaly_type,
        "affected_candles": affected,
    }
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: engines/__init__.py
# ════════════════════════════════════════════════════════════════════════════
ENGINES_INIT_PY = '# engines package\n'

# ════════════════════════════════════════════════════════════════════════════
# FILE: engines/fusion.py
# ════════════════════════════════════════════════════════════════════════════
FUSION_PY = '''
"""
engines/fusion.py — Bayesian Fusion Engine for DATIS.

Combines outputs from all three models (price, sentiment, anomaly) using a
weighted Bayesian approach to produce a single BUY / SELL / HOLD decision
with a calibrated confidence percentage.

Math overview:
  1. Each model votes for BUY, HOLD, SELL with a probability.
  2. Votes are multiplied by the model's weight (price 45%, sentiment 35%, anomaly 20%).
  3. A prior (uniform 33/33/33) is updated with the weighted likelihoods.
  4. The highest posterior probability wins. If < confidence threshold → HOLD.
"""

import numpy as np
from config import (
    PRIOR_BUY, PRIOR_HOLD, PRIOR_SELL,
    WEIGHT_PRICE, WEIGHT_SENTIMENT, WEIGHT_ANOMALY,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM,
)


def _price_to_signal(price_result: dict) -> dict:
    """
    Map price model output → {BUY, HOLD, SELL} probabilities.
    """
    return {
        "BUY":  price_result.get("up_prob",      0.33),
        "HOLD": price_result.get("neutral_prob",  0.34),
        "SELL": price_result.get("down_prob",     0.33),
    }


def _sentiment_to_signal(sentiment_result: dict) -> dict:
    """
    Map sentiment model output → {BUY, HOLD, SELL} probabilities.
    positive → BUY leaning, negative → SELL leaning
    """
    return {
        "BUY":  sentiment_result.get("positive", 0.33),
        "HOLD": sentiment_result.get("neutral",  0.34),
        "SELL": sentiment_result.get("negative", 0.33),
    }


def _anomaly_to_signal(anomaly_result: dict) -> dict:
    """
    Map anomaly model output → {BUY, HOLD, SELL} probabilities.

    Logic:
      - High anomaly score → uncertainty → push towards HOLD
      - Low anomaly score  → markets are calm → trust other signals
    """
    score     = anomaly_result.get("anomaly_score", 0.0)
    is_anom   = anomaly_result.get("is_anomaly", False)

    if is_anom or score > 0.65:
        # Anomaly detected: uncertainty dominates → strong HOLD signal
        return {"BUY": 0.15, "HOLD": 0.70, "SELL": 0.15}
    elif score > 0.35:
        # Mild anomaly: slight HOLD bias
        return {"BUY": 0.25, "HOLD": 0.50, "SELL": 0.25}
    else:
        # Normal conditions: neutral contribution
        return {"BUY": 0.33, "HOLD": 0.34, "SELL": 0.33}


def fuse(
    price_result: dict,
    sentiment_result: dict,
    anomaly_result: dict,
) -> dict:
    """
    Perform Bayesian fusion of all three model outputs.

    Args:
        price_result:     Output from models.price_model.predict()
        sentiment_result: Output from models.sentiment_model.analyze()
        anomaly_result:   Output from models.anomaly_model.detect()

    Returns:
        {
            "action":             "BUY" | "SELL" | "HOLD",
            "confidence":         float  (0–1),
            "confidence_label":   "HIGH" | "MEDIUM" | "LOW",
            "posterior": {
                "BUY":  float,
                "HOLD": float,
                "SELL": float,
            },
            "model_contributions": {
                "price":     {"weight": float, "vote": str, "signal": dict},
                "sentiment": {"weight": float, "vote": str, "signal": dict},
                "anomaly":   {"weight": float, "vote": str, "signal": dict},
            }
        }
    """
    # Convert model outputs to BUY/HOLD/SELL probability dicts
    p_sig = _price_to_signal(price_result)
    s_sig = _sentiment_to_signal(sentiment_result)
    a_sig = _anomaly_to_signal(anomaly_result)

    # Prior
    prior = np.array([PRIOR_BUY, PRIOR_HOLD, PRIOR_SELL])
    labels = ["BUY", "HOLD", "SELL"]

    # Weighted likelihood from each model
    lh_price     = np.array([p_sig[l] for l in labels])
    lh_sentiment = np.array([s_sig[l] for l in labels])
    lh_anomaly   = np.array([a_sig[l] for l in labels])

    # Bayesian update (log space for numerical stability)
    log_posterior = (
        np.log(prior + 1e-9)
        + WEIGHT_PRICE     * np.log(lh_price     + 1e-9)
        + WEIGHT_SENTIMENT * np.log(lh_sentiment + 1e-9)
        + WEIGHT_ANOMALY   * np.log(lh_anomaly   + 1e-9)
    )

    # Convert back to probabilities via softmax
    log_posterior -= log_posterior.max()           # numerical stability
    posterior      = np.exp(log_posterior)
    posterior     /= posterior.sum()

    posterior_dict = {l: round(float(v), 4) for l, v in zip(labels, posterior)}
    best_idx       = int(np.argmax(posterior))
    action         = labels[best_idx]
    confidence     = float(posterior[best_idx])

    # Override to HOLD if confidence is too low
    if confidence < CONFIDENCE_MEDIUM:
        action = "HOLD"

    # Confidence label
    if confidence >= CONFIDENCE_HIGH:
        confidence_label = "HIGH"
    elif confidence >= CONFIDENCE_MEDIUM:
        confidence_label = "MEDIUM"
    else:
        confidence_label = "LOW"

    return {
        "action":           action,
        "confidence":       round(confidence, 4),
        "confidence_label": confidence_label,
        "posterior":        posterior_dict,
        "model_contributions": {
            "price": {
                "weight": WEIGHT_PRICE,
                "vote":   max(p_sig, key=lambda k: p_sig[k]),
                "signal": {k: round(v, 4) for k, v in p_sig.items()},
            },
            "sentiment": {
                "weight": WEIGHT_SENTIMENT,
                "vote":   max(s_sig, key=lambda k: s_sig[k]),
                "signal": {k: round(v, 4) for k, v in s_sig.items()},
            },
            "anomaly": {
                "weight": WEIGHT_ANOMALY,
                "vote":   max(a_sig, key=lambda k: a_sig[k]),
                "signal": {k: round(v, 4) for k, v in a_sig.items()},
            },
        },
    }
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: engines/contradiction.py
# ════════════════════════════════════════════════════════════════════════════
CONTRADICTION_PY = '''
"""
engines/contradiction.py — Contradiction Detection Engine for DATIS.

Detects disagreements between model outputs that might indicate:
  • Mixed signals the trader should be aware of
  • Higher uncertainty in the final recommendation
  • Specific market patterns (e.g. distribution phase, bear-trap)

Each contradiction rule returns a warning dict if triggered.
"""

from typing import List


# ── Rule definitions ──────────────────────────────────────────────────────────

def _rule_positive_sentiment_falling_price(
    price_result: dict, sentiment_result: dict
) -> dict | None:
    """
    Positive sentiment + falling price trend → possible distribution phase.
    Smart money may be selling while news is still positive.
    """
    if (
        sentiment_result.get("label") == "positive"
        and price_result.get("trend") == "down"
        and sentiment_result.get("positive", 0) > 0.55
        and price_result.get("down_prob", 0) > 0.50
    ):
        return {
            "code":        "POS_SENTIMENT_FALLING_PRICE",
            "severity":    "HIGH",
            "description": (
                "Positive news sentiment conflicts with a falling price trend. "
                "This pattern often indicates a distribution phase where informed "
                "participants are selling into positive news flow."
            ),
            "affected_models": ["price", "sentiment"],
        }
    return None


def _rule_bullish_trend_anomaly(
    price_result: dict, anomaly_result: dict
) -> dict | None:
    """
    Bullish trend + anomaly detected → possible manipulated pump.
    Unusual volume or pattern during a rally can precede sharp reversals.
    """
    if (
        price_result.get("trend") == "up"
        and anomaly_result.get("is_anomaly") is True
        and price_result.get("up_prob", 0) > 0.55
        and anomaly_result.get("anomaly_score", 0) > 0.60
    ):
        atype = anomaly_result.get("anomaly_type", "unknown")
        return {
            "code":        "BULLISH_TREND_WITH_ANOMALY",
            "severity":    "HIGH",
            "description": (
                f"A strong bullish trend coincides with a detected anomaly "
                f"({atype}). This may indicate a manufactured pump, stop-hunt, "
                f"or news-driven spike that could reverse quickly."
            ),
            "affected_models": ["price", "anomaly"],
        }
    return None


def _rule_negative_sentiment_rising_price(
    price_result: dict, sentiment_result: dict
) -> dict | None:
    """
    Negative sentiment + rising price → possible short squeeze or bear trap.
    Price moving against negative news may indicate contrarian opportunity
    but also extreme short-term volatility risk.
    """
    if (
        sentiment_result.get("label") == "negative"
        and price_result.get("trend") == "up"
        and sentiment_result.get("negative", 0) > 0.55
        and price_result.get("up_prob", 0) > 0.50
    ):
        return {
            "code":        "NEG_SENTIMENT_RISING_PRICE",
            "severity":    "MEDIUM",
            "description": (
                "Negative sentiment is in direct conflict with a rising price "
                "trend. This may be a short squeeze (trapped shorts forced to "
                "cover) or a bear trap. Proceed with caution."
            ),
            "affected_models": ["price", "sentiment"],
        }
    return None


def _rule_model_disagreement(
    price_result: dict, sentiment_result: dict, anomaly_result: dict
) -> dict | None:
    """
    All three models disagree — no consensus exists.
    When each model points in a different direction confidence collapses.
    """
    price_vote     = price_result.get("trend", "neutral")
    sentiment_vote = sentiment_result.get("label", "neutral")
    anomaly_vote   = "anomaly" if anomaly_result.get("is_anomaly") else "normal"

    # Map to a common scale: bullish / bearish / neutral
    def to_direction(v: str) -> str:
        if v in ("up", "positive"):         return "bullish"
        if v in ("down", "negative"):       return "bearish"
        if v in ("anomaly",):               return "uncertain"
        return "neutral"

    dirs = {
        to_direction(price_vote),
        to_direction(sentiment_vote),
        to_direction(anomaly_vote),
    }

    if len(dirs) == 3:            # all three different
        return {
            "code":        "FULL_MODEL_DISAGREEMENT",
            "severity":    "MEDIUM",
            "description": (
                "All three models (price, sentiment, anomaly) are pointing in "
                "different directions. Confidence is unreliable — consider "
                "waiting for convergence before acting."
            ),
            "affected_models": ["price", "sentiment", "anomaly"],
        }
    return None


def _rule_volume_anomaly_no_price_move(
    price_result: dict, anomaly_result: dict
) -> dict | None:
    """
    High volume anomaly + neutral price trend → possible accumulation.
    Smart money accumulating quietly before a big move.
    """
    if (
        anomaly_result.get("anomaly_type") == "volume_spike"
        and price_result.get("trend") == "neutral"
        and anomaly_result.get("anomaly_score", 0) > 0.65
    ):
        return {
            "code":        "VOLUME_SPIKE_NEUTRAL_PRICE",
            "severity":    "LOW",
            "description": (
                "An unusual volume spike was detected while price remains "
                "neutral. This often precedes a breakout — large participants "
                "may be quietly accumulating or distributing."
            ),
            "affected_models": ["price", "anomaly"],
        }
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def check(
    price_result: dict,
    sentiment_result: dict,
    anomaly_result: dict,
) -> List[dict]:
    """
    Run all contradiction rules and return triggered warnings.

    Args:
        price_result:     Output from models.price_model.predict()
        sentiment_result: Output from models.sentiment_model.analyze()
        anomaly_result:   Output from models.anomaly_model.detect()

    Returns:
        List of warning dicts. Empty list = no contradictions detected.
        Each dict has: {code, severity, description, affected_models}
    """
    rules = [
        _rule_positive_sentiment_falling_price(price_result, sentiment_result),
        _rule_bullish_trend_anomaly(price_result, anomaly_result),
        _rule_negative_sentiment_rising_price(price_result, sentiment_result),
        _rule_model_disagreement(price_result, sentiment_result, anomaly_result),
        _rule_volume_anomaly_no_price_move(price_result, anomaly_result),
    ]

    # Filter None values (rules that didn't trigger)
    return [r for r in rules if r is not None]
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: engines/strategy.py
# ════════════════════════════════════════════════════════════════════════════
STRATEGY_PY = '''
"""
engines/strategy.py — Strategy Generator for DATIS.

Takes the fused decision, contradiction warnings, and individual model outputs
and packages everything into a human-readable trading strategy object.

Output is designed to be consumed directly by the frontend without further
processing.
"""

from typing import List
from config import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


# ── Risk level lookup ─────────────────────────────────────────────────────────

def _compute_risk(
    fusion_result: dict,
    anomaly_result: dict,
    contradictions: List[dict],
) -> str:
    """
    Derive a risk level string from combined signals.

    Rules:
      HIGH   → anomaly detected OR any HIGH severity contradiction
      MEDIUM → confidence < CONFIDENCE_HIGH OR any contradiction exists
      LOW    → no anomaly, no contradictions, high confidence
    """
    is_anomaly  = anomaly_result.get("is_anomaly", False)
    confidence  = fusion_result.get("confidence", 0.0)
    high_warns  = [c for c in contradictions if c.get("severity") == "HIGH"]

    if is_anomaly or high_warns:
        return "HIGH"
    elif contradictions or confidence < CONFIDENCE_HIGH:
        return "MEDIUM"
    else:
        return "LOW"


# ── Explanation builder ───────────────────────────────────────────────────────

def _build_explanation(
    action: str,
    confidence: float,
    price_result: dict,
    sentiment_result: dict,
    anomaly_result: dict,
    contradictions: List[dict],
) -> str:
    """
    Produce a clear natural-language explanation of the strategy.
    """
    parts = []

    # Price trend
    trend     = price_result.get("trend", "neutral")
    trend_str = {"up": "bullish", "down": "bearish", "neutral": "neutral"}
    parts.append(
        f"The price model signals a {trend_str.get(trend, trend)} trend "
        f"(up {price_result.get('up_prob', 0)*100:.1f}% | "
        f"down {price_result.get('down_prob', 0)*100:.1f}%)."
    )

    # Sentiment
    sent_label = sentiment_result.get("label", "neutral")
    parts.append(
        f"Market sentiment is {sent_label} "
        f"(positive {sentiment_result.get('positive', 0)*100:.1f}% | "
        f"negative {sentiment_result.get('negative', 0)*100:.1f}%)."
    )

    # Anomaly
    if anomaly_result.get("is_anomaly"):
        atype = anomaly_result.get("anomaly_type", "unknown")
        parts.append(
            f"⚠ An anomaly was detected ({atype}), suggesting unusual "
            f"market conditions. Exercise caution."
        )
    else:
        parts.append("No market anomalies detected — conditions appear normal.")

    # Contradictions
    if contradictions:
        codes = [c["code"] for c in contradictions]
        parts.append(
            f"Contradiction alert(s): {', '.join(codes)}. "
            f"See warnings for details."
        )

    # Final decision rationale
    conf_pct = confidence * 100
    if action == "BUY":
        parts.append(
            f"Based on converging signals, a BUY is recommended with "
            f"{conf_pct:.1f}% confidence."
        )
    elif action == "SELL":
        parts.append(
            f"Based on converging signals, a SELL is recommended with "
            f"{conf_pct:.1f}% confidence."
        )
    else:
        parts.append(
            f"Signals are mixed or weak (confidence: {conf_pct:.1f}%). "
            f"HOLD and await clearer market direction."
        )

    return " ".join(parts)


# ── Public API ────────────────────────────────────────────────────────────────

def generate(
    price_result: dict,
    sentiment_result: dict,
    anomaly_result: dict,
    fusion_result: dict,
    contradictions: List[dict],
) -> dict:
    """
    Generate a complete trading strategy from all engine outputs.

    Args:
        price_result:     Output from models.price_model.predict()
        sentiment_result: Output from models.sentiment_model.analyze()
        anomaly_result:   Output from models.anomaly_model.detect()
        fusion_result:    Output from engines.fusion.fuse()
        contradictions:   Output from engines.contradiction.check()

    Returns:
        {
            "action":             "BUY" | "SELL" | "HOLD",
            "confidence":         float (0–1),
            "confidence_pct":     str   e.g. "72.3%",
            "confidence_label":   "HIGH" | "MEDIUM" | "LOW",
            "risk_level":         "HIGH" | "MEDIUM" | "LOW",
            "explanation":        str,
            "warnings":           List[dict],
            "model_summary": {
                "price":     {"trend": str, "up": float, "down": float},
                "sentiment": {"label": str, "score": float},
                "anomaly":   {"is_anomaly": bool, "score": float, "type": str},
            },
            "posterior":          dict,
            "model_contributions": dict,
        }
    """
    action     = fusion_result["action"]
    confidence = fusion_result["confidence"]
    risk       = _compute_risk(fusion_result, anomaly_result, contradictions)
    explanation = _build_explanation(
        action, confidence,
        price_result, sentiment_result, anomaly_result,
        contradictions,
    )

    return {
        "action":             action,
        "confidence":         confidence,
        "confidence_pct":     f"{confidence * 100:.1f}%",
        "confidence_label":   fusion_result.get("confidence_label", "MEDIUM"),
        "risk_level":         risk,
        "explanation":        explanation,
        "warnings":           contradictions,
        "model_summary": {
            "price": {
                "trend": price_result.get("trend", "neutral"),
                "up":    price_result.get("up_prob", 0.33),
                "down":  price_result.get("down_prob", 0.33),
            },
            "sentiment": {
                "label": sentiment_result.get("label", "neutral"),
                "score": max(
                    sentiment_result.get("positive", 0),
                    sentiment_result.get("negative", 0),
                    sentiment_result.get("neutral",  0),
                ),
            },
            "anomaly": {
                "is_anomaly": anomaly_result.get("is_anomaly", False),
                "score":      anomaly_result.get("anomaly_score", 0.0),
                "type":       anomaly_result.get("anomaly_type", "none"),
            },
        },
        "posterior":           fusion_result.get("posterior", {}),
        "model_contributions": fusion_result.get("model_contributions", {}),
    }
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: routes/__init__.py
# ════════════════════════════════════════════════════════════════════════════
ROUTES_INIT_PY = '# routes package\n'

# ════════════════════════════════════════════════════════════════════════════
# FILE: routes/health.py
# ════════════════════════════════════════════════════════════════════════════
HEALTH_PY = '''
"""
routes/health.py — Health check endpoint for DATIS.

GET /health
  Returns API status, version, and a list of available model components.
  Frontend and monitoring tools can poll this to verify the backend is alive.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import sys
import torch
import sklearn
import numpy
import pandas

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="API Health Check",
    description="Returns the operational status and dependency versions of the DATIS backend.",
)
def health_check() -> dict:
    """
    Check that the API and its core dependencies are operational.

    Returns:
        JSON object with status, timestamp, versions, and available components.
    """
    return {
        "status":    "ok",
        "service":   "DATIS Backend",
        "version":   "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python":    sys.version,
        "dependencies": {
            "torch":        torch.__version__,
            "sklearn":      sklearn.__version__,
            "numpy":        numpy.__version__,
            "pandas":       pandas.__version__,
        },
        "components": {
            "price_model":      "ready",
            "sentiment_model":  "ready",
            "anomaly_model":    "ready",
            "fusion_engine":    "ready",
            "contradiction_engine": "ready",
            "strategy_generator":   "ready",
        },
        "endpoints": [
            "GET /health",
            "GET /predict/{symbol}",
            "GET /sentiment/{symbol}",
        ],
    }
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: routes/predict.py
# ════════════════════════════════════════════════════════════════════════════
PREDICT_PY = '''
"""
routes/predict.py — Prediction endpoint for DATIS.

GET /predict/{symbol}
  Runs all three models + fusion + contradiction + strategy for a given ticker.
  This is the main endpoint that your frontend should call for full analysis.

Query parameters:
  - symbol (path)     : Ticker symbol, e.g. BTC, AAPL, ETH
  - text   (optional) : News headline or paragraph for sentiment analysis
  - rows   (optional) : How many OHLCV candles to load (default 100)
"""

from fastapi import APIRouter, Query, HTTPException
from utils import load_ohlcv
from models import price_model, sentiment_model, anomaly_model
from engines import fusion, contradiction, strategy

router = APIRouter(tags=["Prediction"])


@router.get(
    "/predict/{symbol}",
    summary="Full AI Trading Analysis",
    description=(
        "Run the complete DATIS multi-model analysis pipeline for a symbol. "
        "Returns price trend, sentiment, anomaly detection, Bayesian fusion, "
        "contradiction warnings, and a final trading strategy."
    ),
)
def predict(
    symbol: str,
    text: str | None = Query(
        default=None,
        description="Optional news text to use for sentiment analysis.",
    ),
    rows: int = Query(
        default=100,
        ge=10,
        le=500,
        description="Number of OHLCV candles to load (10–500).",
    ),
) -> dict:
    """
    Full DATIS analysis pipeline for the given symbol.

    Steps:
      1. Load OHLCV data (from CSV or synthetic fallback)
      2. Run price trend model
      3. Run sentiment model
      4. Run anomaly detector
      5. Fuse via Bayesian engine
      6. Check for contradictions
      7. Generate strategy

    Args:
        symbol: Ticker, e.g. "BTC"
        text:   Optional news text for real sentiment analysis
        rows:   How many candles to use

    Returns:
        Complete strategy dict from engines.strategy.generate()
    """
    symbol = symbol.upper().strip()

    if not symbol.isalnum():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid symbol '{symbol}'. Use alphanumeric tickers only.",
        )

    # ── 1. Load data ─────────────────────────────────────────────────────────
    try:
        df = load_ohlcv(symbol, rows=rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data load failed: {e}")

    # ── 2–4. Run models ───────────────────────────────────────────────────────
    try:
        price_result     = price_model.predict(df)
        sentiment_result = sentiment_model.analyze(symbol, text=text)
        anomaly_result   = anomaly_model.detect(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    # ── 5. Bayesian Fusion ────────────────────────────────────────────────────
    try:
        fusion_result = fusion.fuse(price_result, sentiment_result, anomaly_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fusion engine failed: {e}")

    # ── 6. Contradiction Detection ────────────────────────────────────────────
    try:
        contradictions = contradiction.check(price_result, sentiment_result, anomaly_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contradiction engine failed: {e}")

    # ── 7. Strategy Generation ────────────────────────────────────────────────
    try:
        result = strategy.generate(
            price_result     = price_result,
            sentiment_result = sentiment_result,
            anomaly_result   = anomaly_result,
            fusion_result    = fusion_result,
            contradictions   = contradictions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {e}")

    # Attach metadata for the frontend
    result["symbol"]      = symbol
    result["candles_used"] = len(df)
    result["data_source"]  = "file" if (
        __import__("pathlib").Path(
            __import__("config").DATA_DIR / f"{symbol}.csv"
        ).exists()
    ) else "synthetic"

    return result
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: routes/sentiment.py
# ════════════════════════════════════════════════════════════════════════════
SENTIMENT_PY = '''
"""
routes/sentiment.py — Sentiment-only endpoint for DATIS.

GET /sentiment/{symbol}
  Runs only the sentiment model for a given symbol.
  Useful when the frontend wants to display a quick sentiment badge
  without triggering the full prediction pipeline.

Query parameters:
  - symbol (path)     : Ticker symbol
  - text   (optional) : News headline or article text
"""

from fastapi import APIRouter, Query, HTTPException
from models import sentiment_model

router = APIRouter(tags=["Sentiment"])


@router.get(
    "/sentiment/{symbol}",
    summary="Sentiment Analysis",
    description=(
        "Run sentiment analysis for a ticker symbol. "
        "Pass optional news text for real analysis, or let the model "
        "produce a deterministic symbol-based sentiment estimate."
    ),
)
def get_sentiment(
    symbol: str,
    text: str | None = Query(
        default=None,
        description="Optional news headline or paragraph to analyse.",
    ),
) -> dict:
    """
    Return sentiment analysis for the given symbol.

    Args:
        symbol: Ticker string
        text:   Optional news text

    Returns:
        {
            "symbol":     str,
            "label":      "positive" | "neutral" | "negative",
            "positive":   float,
            "neutral":    float,
            "negative":   float,
            "model_used": "finbert" | "lexicon" | "seed"
        }
    """
    symbol = symbol.upper().strip()

    if not symbol.isalnum():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid symbol '{symbol}'.",
        )

    try:
        result = sentiment_model.analyze(symbol, text=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {e}")

    result["symbol"] = symbol
    return result
'''

# ════════════════════════════════════════════════════════════════════════════
# FILE: main.py
# ════════════════════════════════════════════════════════════════════════════
MAIN_PY = '''
"""
main.py — DATIS FastAPI Application Entry Point

Run with:
    uvicorn main:app --reload --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import APP_TITLE, APP_VERSION, APP_DESCRIPTION, CORS_ORIGINS

# ── Import route modules ──────────────────────────────────────────────────────
from routes.health    import router as health_router
from routes.predict   import router as predict_router
from routes.sentiment import router as sentiment_router

# ── Create FastAPI app ────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allows your frontend (React/Vue/etc.) to call this API from a browser.
# In production, replace "*" with your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, OPTIONS, etc.
    allow_headers=["*"],        # Content-Type, Authorization, etc.
)

# ── Register routes ───────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(predict_router)
app.include_router(sentiment_router)


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    """Redirect root to API docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# ── Startup event ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """
    Runs once when the server starts.
    Good place to pre-load models, warm up caches, etc.
    """
    print("=" * 60)
    print("  DATIS Backend — Part 1")
    print(f"  Version : {APP_VERSION}")
    print("  Status  : All systems operational")
    print("  Docs    : http://localhost:8000/docs")
    print("=" * 60)


# ── Dev entrypoint ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''

# ════════════════════════════════════════════════════════════════════════════
# PRINT ALL FILES
# ════════════════════════════════════════════════════════════════════════════

FILE_MAP = {
    "requirements.txt":          REQUIREMENTS_TXT,
    "config.py":                 CONFIG_PY,
    "utils/__init__.py":         UTILS_INIT_PY,
    "models/__init__.py":        MODELS_INIT_PY,
    "models/price_model.py":     PRICE_MODEL_PY,
    "models/sentiment_model.py": SENTIMENT_MODEL_PY,
    "models/anomaly_model.py":   ANOMALY_MODEL_PY,
    "engines/__init__.py":       ENGINES_INIT_PY,
    "engines/fusion.py":         FUSION_PY,
    "engines/contradiction.py":  CONTRADICTION_PY,
    "engines/strategy.py":       STRATEGY_PY,
    "routes/__init__.py":        ROUTES_INIT_PY,
    "routes/health.py":          HEALTH_PY,
    "routes/predict.py":         PREDICT_PY,
    "routes/sentiment.py":       SENTIMENT_PY,
    "main.py":                   MAIN_PY,
}

if __name__ == "__main__":
    import os

    print("\n🚀  DATIS Backend Part 1 — File Generator")
    print("=" * 60)

    base = os.path.join(os.path.dirname(__file__), "backend")

    for rel_path, content in FILE_MAP.items():
        full_path = os.path.join(base, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.lstrip("\n"))
        print(f"  ✓  Created  backend/{rel_path}")

    # Create empty placeholder dirs
    for d in ["data"]:
        os.makedirs(os.path.join(base, d), exist_ok=True)
        print(f"  ✓  Created  backend/{d}/  (placeholder)")

    print("\n✅  All files generated inside ./backend/")
    print("\nNext steps:")
    print("  cd backend")
    print("  pip install -r requirements.txt")
    print("  uvicorn main:app --reload --port 8000")
    print("  # Visit http://localhost:8000/docs")
   