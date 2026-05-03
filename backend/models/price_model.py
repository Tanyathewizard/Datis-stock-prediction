from __future__ import annotations

from pathlib import Path
import joblib
import pandas as pd

from ..config import PRICE_LOOKBACK_WINDOW
from ..utils import load_ohlcv


MODEL_PATH = Path(__file__).resolve().parent / "fusion_ml_model.joblib"
_MODEL_BUNDLE = None


def _load_model_bundle() -> dict:
    global _MODEL_BUNDLE

    if _MODEL_BUNDLE is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "fusion_ml_model.joblib not found. Run: python backend\\models\\train_fusion_ml.py"
            )

        _MODEL_BUNDLE = joblib.load(MODEL_PATH)

    return _MODEL_BUNDLE


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return (100 - (100 / (1 + rs))).fillna(50)


def _macd(close: pd.Series) -> pd.Series:
    return _ema(close, 12) - _ema(close, 26)


def _sentiment_to_score(sentiment: dict | None) -> float:
    if not sentiment:
        return 0.0

    positive = float(sentiment.get("positive", 0.33))
    negative = float(sentiment.get("negative", 0.33))

    return positive - negative


def _anomaly_to_flag(anomaly: dict | None) -> int:
    if not anomaly:
        return 0

    score = float(anomaly.get("anomaly_score", 0.0))
    return 1 if anomaly.get("is_anomaly") or score >= 0.65 else 0


def _extract_features(
    symbol: str,
    rows: int,
    sentiment: dict | None = None,
    anomaly: dict | None = None,
) -> dict:
    df = load_ohlcv(symbol, max(rows, 60))

    if df.empty or len(df) < 10:
        raise ValueError("Not enough OHLCV data for ML prediction")

    close = df["close"].astype(float)

    return {
        "open": float(df["open"].iloc[-1]),
        "high": float(df["high"].iloc[-1]),
        "low": float(df["low"].iloc[-1]),
        "close": float(df["close"].iloc[-1]),
        "volume": float(df["volume"].iloc[-1]),
        "rsi": float(_rsi(close).iloc[-1]),
        "macd": float(_macd(close).iloc[-1]),
        "ma20": float(close.rolling(20).mean().fillna(close.mean()).iloc[-1]),
        "volatility": float(close.pct_change().rolling(10).std().fillna(0).iloc[-1]),
        "sentimentscore": _sentiment_to_score(sentiment),
        "anomalyflag": _anomaly_to_flag(anomaly),
    }


def analyze(
    symbol: str,
    rows: int = PRICE_LOOKBACK_WINDOW,
    sentiment: dict | None = None,
    anomaly: dict | None = None,
) -> dict:
    symbol = symbol.upper().strip()

    bundle = _load_model_bundle()
    model = bundle["model"]
    feature_names = bundle["features"]

    latest = _extract_features(symbol, rows, sentiment, anomaly)

    X = pd.DataFrame([[latest[f] for f in feature_names]], columns=feature_names)

    label = str(model.predict(X)[0]).upper()

    proba = model.predict_proba(X)[0]
    classes = [str(c).upper() for c in model.classes_]

    probs = {"buy": 0.0, "hold": 0.0, "sell": 0.0}

    for cls, p in zip(classes, proba):
        if cls == "BUY":
            probs["buy"] = round(float(p), 4)
        elif cls == "HOLD":
            probs["hold"] = round(float(p), 4)
        elif cls == "SELL":
            probs["sell"] = round(float(p), 4)

    confidence = max(probs.values())
    last_close = latest["close"]

    if label == "BUY":
        predicted_close = last_close * 1.02
    elif label == "SELL":
        predicted_close = last_close * 0.98
    else:
        predicted_close = last_close

    change_pct = ((predicted_close - last_close) / last_close) * 100

    return {
        "symbol": symbol,
        "label": label,
        "buy": probs["buy"],
        "hold": probs["hold"],
        "sell": probs["sell"],
        "confidence": round(float(confidence), 4),
        "predicted_close": round(float(predicted_close), 4),
        "last_close": round(float(last_close), 4),
        "change_pct": round(float(change_pct), 4),
        "rsi": round(float(latest["rsi"]), 2),
        "macd": round(float(latest["macd"]), 4),
        "ma20": round(float(latest["ma20"]), 4),
        "volatility": round(float(latest["volatility"]), 6),
        "sentiment_score_used": round(float(latest["sentimentscore"]), 4),
        "anomaly_flag_used": int(latest["anomalyflag"]),
        "model_used": "random_forest_fusion_ml",
    }


def predict(
    symbol: str,
    rows: int = PRICE_LOOKBACK_WINDOW,
    sentiment: dict | None = None,
    anomaly: dict | None = None,
) -> dict:
    return analyze(symbol, rows, sentiment, anomaly)