import random
import numpy as np
from datetime import datetime
from typing import Any, Dict

FEATURE_NAMES = ["sentiment", "trend", "volume", "anomaly_score"]

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

def _now() -> str:
    return datetime.utcnow().isoformat()

def _mock_feature_vector(symbol: str) -> Dict[str, float]:
    rng = random.Random(hash(symbol) % (2**31))
    return {
        "sentiment":     round(rng.uniform(-1, 1), 4),
        "trend":         round(rng.uniform(-1, 1), 4),
        "volume":        round(rng.uniform(0, 1), 4),
        "anomaly_score": round(rng.uniform(0, 1), 4),
    }

def _decision_from_features(features: Dict[str, float]) -> Dict[str, Any]:
    s = features["sentiment"]
    t = features["trend"]
    v = features["volume"]
    a = features["anomaly_score"]
    score = (s * 0.35) + (t * 0.30) + (v * 0.20) - (a * 0.15)
    confidence = round(min(abs(score) * 1.2 + 0.4, 1.0), 4)
    if score > 0.15:
        decision = "BUY"
    elif score < -0.15:
        decision = "SELL"
    else:
        decision = "HOLD"
    return {"decision": decision, "confidence": confidence, "raw_score": round(score, 4)}

def _feature_importance_shap(features: Dict[str, float]) -> Dict[str, float]:
    weights = {"sentiment": 0.35, "trend": 0.30, "volume": 0.20, "anomaly_score": -0.15}
    return {k: round(features[k] * weights[k], 5) for k in features}

def _feature_importance_lime(features: Dict[str, float]) -> Dict[str, float]:
    base = _decision_from_features(features)["raw_score"]
    importance = {}
    for key in features:
        perturbed = dict(features)
        perturbed[key] = features[key] + 0.1
        delta = _decision_from_features(perturbed)["raw_score"] - base
        importance[key] = round(delta, 5)
    return importance
