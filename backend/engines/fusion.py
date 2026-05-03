import numpy as np

from ..config import (
    PRIOR_BUY,
    PRIOR_HOLD,
    PRIOR_SELL,
    WEIGHT_PRICE,
    WEIGHT_SENTIMENT,
    WEIGHT_ANOMALY,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
)


LABELS = ["BUY", "HOLD", "SELL"]


def _normalize(probs: dict) -> dict:
    total = sum(probs.values()) + 1e-9
    return {k: float(v / total) for k, v in probs.items()}


def _price_signal(result: dict) -> dict:
    return _normalize({
        "BUY": result.get("buy", 0.33),
        "HOLD": result.get("hold", 0.34),
        "SELL": result.get("sell", 0.33),
    })


def _sentiment_signal(result: dict) -> dict:
    return _normalize({
        "BUY": result.get("positive", 0.33),
        "HOLD": result.get("neutral", 0.34),
        "SELL": result.get("negative", 0.33),
    })


def _anomaly_signal(result: dict) -> dict:
    score = result.get("anomaly_score", 0.0)
    is_anomaly = result.get("is_anomaly", False)

    if is_anomaly or score > 0.70:
        probs = {"BUY": 0.10, "HOLD": 0.80, "SELL": 0.10}
    elif score > 0.40:
        probs = {"BUY": 0.20, "HOLD": 0.60, "SELL": 0.20}
    else:
        probs = {"BUY": 0.33, "HOLD": 0.34, "SELL": 0.33}

    return _normalize(probs)


def _bayesian_fusion(price_sig: dict, sent_sig: dict, anom_sig: dict) -> dict:
    prior = np.array([PRIOR_BUY, PRIOR_HOLD, PRIOR_SELL], dtype=float)

    p = np.array([price_sig[x] for x in LABELS], dtype=float)
    s = np.array([sent_sig[x] for x in LABELS], dtype=float)
    a = np.array([anom_sig[x] for x in LABELS], dtype=float)

    log_scores = (
        np.log(prior + 1e-9)
        + WEIGHT_PRICE * np.log(p + 1e-9)
        + WEIGHT_SENTIMENT * np.log(s + 1e-9)
        + WEIGHT_ANOMALY * np.log(a + 1e-9)
    )

    log_scores -= np.max(log_scores)

    probs = np.exp(log_scores)
    probs /= probs.sum()

    return {k: round(float(v), 4) for k, v in zip(LABELS, probs)}


def _market_state(price: dict, sentiment: dict, anomaly: dict) -> str:
    if anomaly["HOLD"] > 0.60:
        return "volatile"

    if price["BUY"] > 0.55 and sentiment["BUY"] > 0.50:
        return "bullish"

    if price["SELL"] > 0.55 and sentiment["SELL"] > 0.50:
        return "bearish"

    return "sideways"


def _agreement(price: dict, sentiment: dict, anomaly: dict) -> float:
    votes = [
        max(price, key=price.get),
        max(sentiment, key=sentiment.get),
        max(anomaly, key=anomaly.get),
    ]

    top_vote = max(set(votes), key=votes.count)
    return round(votes.count(top_vote) / 3, 2)


def _reason(action: str, price: dict, sentiment: dict, anomaly: dict, market_state: str) -> str:
    if action == "BUY":
        if market_state == "volatile":
            return "BUY signal detected, but market risk is elevated."
        return "Price model and sentiment support a bullish decision."

    if action == "SELL":
        if market_state == "volatile":
            return "SELL signal detected with elevated market uncertainty."
        return "Price model and sentiment indicate bearish pressure."

    if anomaly["HOLD"] > 0.60:
        return "Market anomaly risk is high, so the system prefers HOLD."

    return "Signals are mixed or confidence is not strong enough."


def fuse(price_result: dict, sentiment_result: dict, anomaly_result: dict) -> dict:
    price_sig = _price_signal(price_result)
    sent_sig = _sentiment_signal(sentiment_result)
    anom_sig = _anomaly_signal(anomaly_result)

    posterior = _bayesian_fusion(price_sig, sent_sig, anom_sig)

    action = max(posterior, key=posterior.get)
    confidence = posterior[action]

    if confidence < CONFIDENCE_MEDIUM:
        action = "HOLD"

    if confidence >= CONFIDENCE_HIGH:
        confidence_label = "HIGH"
    elif confidence >= CONFIDENCE_MEDIUM:
        confidence_label = "MEDIUM"
    else:
        confidence_label = "LOW"

    market_state = _market_state(price_sig, sent_sig, anom_sig)
    agreement_score = _agreement(price_sig, sent_sig, anom_sig)
    reason = _reason(action, price_sig, sent_sig, anom_sig, market_state)

    return {
        "action": action,
        "confidence": round(float(confidence), 4),
        "confidence_label": confidence_label,
        "reason": reason,
        "agreement_score": agreement_score,
        "market_state": market_state,
        "posterior": posterior,
        "signals": {
            "price": price_sig,
            "sentiment": sent_sig,
            "anomaly": anom_sig,
        },
        "model_used": "bayesian_fusion",
    }