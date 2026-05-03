"""
routes/trust.py
───────────────
Trust Score Engine for DATIS.

GET /trustscore          – overall model trust score
GET /trustscore/{symbol} – trust score for a specific ticker

─── How the Trust Score Works ────────────────────────────────────────────────

The score is a composite of three sub-scores (each 0.0 – 1.0):

  1. ACCURACY SCORE (40%)
     Simple hit rate: correct / (correct + incorrect)
     Requires at least 5 resolved predictions to be meaningful.

  2. CONFIDENCE CALIBRATION SCORE (35%)
     Measures whether confidence levels match actual accuracy.
     A perfectly calibrated model that says "80% confidence" should be
     correct 80% of the time. We penalise overconfidence more than under.
     Implemented as 1 – mean_absolute_calibration_error.

  3. RECENCY SCORE (25%)
     Accuracy weighted toward recent predictions.
     The last 10 resolved predictions count for more than older ones.
     This detects model drift – if accuracy is dropping, the score drops fast.

Final trust score = weighted sum, clamped to [0.0, 1.0].
Letter grade:  A (≥0.80) | B (≥0.65) | C (≥0.50) | D (≥0.35) | F (<0.35)

IMPORTANT: With fewer than 5 resolved predictions the scores carry large
uncertainty and should not be used to make financial decisions.
"""

from fastapi import APIRouter, Query
import math
from ..blockchain.database.history_db import fetch_resolved_predictions, fetch_all_history
router = APIRouter(prefix="/trustscore", tags=["Trust Score"])


# ─── Core Computation ────────────────────────────────────────────────────────

def _letter_grade(score: float) -> str:
    if score >= 0.80: return "A"
    if score >= 0.65: return "B"
    if score >= 0.50: return "C"
    if score >= 0.35: return "D"
    return "F"


def _accuracy_score(resolved: list[dict]) -> float:
    """Proportion of resolved predictions that were correct."""
    if not resolved:
        return 0.0
    correct = sum(1 for r in resolved if r["actual_result"] == "CORRECT")
    return correct / len(resolved)


def _calibration_score(resolved: list[dict]) -> float:
    """
    Confidence calibration: how well the model's stated confidence
    matches its actual accuracy.

    We bucket predictions into confidence bands [0-0.5, 0.5-0.6, ..., 0.9-1.0]
    and compute the mean absolute difference between bucket mean confidence
    and bucket accuracy.

    Score = 1 – mean_absolute_calibration_error (clamped to 0)
    """
    if len(resolved) < 3:
        return 0.5   # not enough data; return neutral

    # Define bins
    bins = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)]
    errors = []

    for lo, hi in bins:
        bucket = [r for r in resolved if lo <= r["confidence"] < hi]
        if len(bucket) < 2:
            continue
        avg_conf     = sum(r["confidence"] for r in bucket) / len(bucket)
        bucket_acc   = sum(1 for r in bucket if r["actual_result"] == "CORRECT") / len(bucket)
        # Penalise overconfidence slightly more than under-confidence
        raw_error    = avg_conf - bucket_acc
        penalty      = raw_error * 1.3 if raw_error > 0 else raw_error
        errors.append(abs(penalty))

    if not errors:
        return 0.5

    mean_error = sum(errors) / len(errors)
    return max(0.0, 1.0 - mean_error)


def _recency_score(resolved: list[dict]) -> float:
    """
    Accuracy over the most recent N predictions, with exponential weighting.
    Predictions are assumed to arrive in ascending timestamp order.
    """
    if not resolved:
        return 0.0

    # Sort by timestamp ascending
    recent = sorted(resolved, key=lambda r: r.get("timestamp", 0))
    window = recent[-10:]   # last 10 resolved

    if not window:
        return 0.0

    # Exponential weights: most recent = highest weight
    weights = [math.exp(0.3 * i) for i in range(len(window))]
    total_w = sum(weights)

    weighted_correct = sum(
        w for w, r in zip(weights, window)
        if r["actual_result"] == "CORRECT"
    )
    return weighted_correct / total_w


def compute_trust_score(resolved: list[dict]) -> dict:
    """
    Compute the full trust score dict from a list of resolved predictions.
    """
    n = len(resolved)

    accuracy    = _accuracy_score(resolved)
    calibration = _calibration_score(resolved)
    recency     = _recency_score(resolved)

    # Weighted composite
    composite = (
        0.40 * accuracy
        + 0.35 * calibration
        + 0.25 * recency
    )
    composite = max(0.0, min(1.0, composite))

    reliable = n >= 5
    confidence_label = (
        "HIGH"   if n >= 30 else
        "MEDIUM" if n >= 10 else
        "LOW"    if n >= 5  else
        "INSUFFICIENT DATA"
    )

    return {
        "trust_score":         round(composite, 4),
        "grade":               _letter_grade(composite),
        "confidence_in_score": confidence_label,
        "resolved_count":      n,
        "sub_scores": {
            "accuracy":              round(accuracy,    4),
            "confidence_calibration": round(calibration, 4),
            "recency_performance":   round(recency,     4),
        },
        "weights": {
            "accuracy":    "40%",
            "calibration": "35%",
            "recency":     "25%",
        },
        "reliable":    reliable,
        "disclaimer":  (
            "Trust scores are based on past performance and do not guarantee "
            "future accuracy. This is not financial advice."
            if reliable else
            f"Only {n} resolved predictions found. Score is unreliable until "
            "at least 5 predictions have been resolved."
        ),
    }


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", summary="Overall DATIS model trust score")
def overall_trust_score():
    """
    Returns a composite trust score for the DATIS prediction engine,
    computed from all resolved predictions in the database.

    Sub-scores:
    - **accuracy** (40%) – correct / total resolved
    - **confidence_calibration** (35%) – how well stated confidence matches accuracy
    - **recency_performance** (25%) – accuracy on the most recent predictions
    """
    resolved = fetch_resolved_predictions()
    result   = compute_trust_score(resolved)

    # Add raw stats for transparency
    correct   = sum(1 for r in resolved if r["actual_result"] == "CORRECT")
    incorrect = sum(1 for r in resolved if r["actual_result"] == "INCORRECT")
    all_preds = fetch_all_history()

    result["total_predictions"] = len(all_preds)
    result["correct"]           = correct
    result["incorrect"]         = incorrect
    result["pending"]           = len(all_preds) - len(resolved)

    return result


@router.get("/{symbol}", summary="Trust score for a specific ticker")
def symbol_trust_score(symbol: str):
    """
    Returns the trust score for predictions on a specific ticker (e.g. AAPL).
    Useful for understanding which symbols the model performs best on.
    """
    sym      = symbol.upper()
    resolved = fetch_resolved_predictions(symbol=sym)
    result   = compute_trust_score(resolved)
    result["symbol"] = sym
    return result
