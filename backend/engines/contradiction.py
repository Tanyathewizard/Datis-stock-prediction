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
