from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from ..config import (
    ANOMALY_CONTAMINATION,
    ANOMALY_N_ESTIMATORS,
    DUMMY_SEED,
)


def _engineer_features(df: pd.DataFrame) -> np.ndarray:
    df = df.copy().reset_index(drop=True)

    intraday = (df["high"] - df["low"]) / (df["close"] + 1e-9)

    prev_close = df["close"].shift(1)
    gap = (df["open"] - prev_close) / (prev_close + 1e-9)
    gap = gap.fillna(0)

    vol_mean = df["volume"].mean()
    vol_std = df["volume"].std() + 1e-9
    vol_z = (df["volume"] - vol_mean) / vol_std

    candle_range = (df["high"] - df["low"]).replace(0, 1e-9)
    body_ratio = np.abs(df["close"] - df["open"]) / candle_range

    upper_shadow = (
        df["high"] - np.maximum(df["open"], df["close"])
    ) / (df["close"] + 1e-9)

    lower_shadow = (
        np.minimum(df["open"], df["close"]) - df["low"]
    ) / (df["close"] + 1e-9)

    features = np.column_stack(
        [
            intraday.values,
            gap.values,
            vol_z.values,
            body_ratio.values,
            upper_shadow.values,
            lower_shadow.values,
        ]
    )

    return np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)


def detect(df: pd.DataFrame) -> dict:
    if len(df) < 10:
        return {
            "anomaly_score": 0.0,
            "is_anomaly": False,
            "anomaly_type": "insufficient_data",
            "affected_candles": 0,
            "risk_level": "low",
            "model_used": "isolation_forest",
        }

    X = _engineer_features(df)

    model = IsolationForest(
        n_estimators=ANOMALY_N_ESTIMATORS,
        contamination=ANOMALY_CONTAMINATION,
        random_state=DUMMY_SEED,
    )

    model.fit(X)

    raw_scores = model.decision_function(X)
    preds = model.predict(X)

    normalized = 1.0 - (
        (raw_scores - raw_scores.min()) /
        (raw_scores.max() - raw_scores.min() + 1e-9)
    )

    latest_score = float(normalized[-1])
    latest_pred = int(preds[-1])
    is_anomaly = latest_pred == -1

    affected = int(np.sum(preds[-5:] == -1))

    anomaly_type = "none"

    if is_anomaly:
        last = X[-1]

        if abs(last[2]) > 2.0:
            anomaly_type = "volume_spike"
        elif abs(last[1]) > 0.03:
            anomaly_type = "price_gap"
        elif last[0] > np.percentile(X[:, 0], 95):
            anomaly_type = "high_volatility"
        elif last[3] > 0.8:
            anomaly_type = "strong_candle_move"
        else:
            anomaly_type = "pattern_anomaly"

    if latest_score >= 0.75:
        risk_level = "high"
    elif latest_score >= 0.45:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "anomaly_score": round(latest_score, 4),
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type,
        "affected_candles": affected,
        "risk_level": risk_level,
        "model_used": "isolation_forest",
    }