from fastapi import APIRouter, Query
from ..models import price_model, sentiment_model, anomaly_model
from ..engines.fusion import fuse
from ..utils import load_ohlcv

router = APIRouter(prefix="/failure", tags=["Failure Analysis"])


@router.get("/{symbol}")
def failure_analysis(symbol: str, expected_action: str = Query(default="BUY")):
    symbol = symbol.upper().strip()
    expected_action = expected_action.upper().strip()

    df = load_ohlcv(symbol)

    sentiment_result = sentiment_model.analyze(symbol)
    anomaly_result = anomaly_model.detect(df)

    # ✅ FIX HERE
    price_result = price_model.predict(
        symbol,
        sentiment=sentiment_result,
        anomaly=anomaly_result,
    )

    fusion_result = fuse(price_result, sentiment_result, anomaly_result)

    actual_action = fusion_result.get("action", "HOLD")
    failed = actual_action != expected_action

    possible_reasons = []

    if anomaly_result.get("is_anomaly"):
        possible_reasons.append("Market anomaly detected")

    if sentiment_result.get("negative", 0) > sentiment_result.get("positive", 0):
        possible_reasons.append("Negative sentiment stronger")

    if price_result.get("sell", 0) > price_result.get("buy", 0):
        possible_reasons.append("Price model bearish")

    if fusion_result.get("confidence", 0) < 0.5:
        possible_reasons.append("Low confidence")

    if not possible_reasons:
        possible_reasons.append("No major failure factor")

    return {
        "success": True,
        "symbol": symbol,
        "expected_action": expected_action,
        "actual_action": actual_action,
        "failed": failed,
        "confidence": fusion_result.get("confidence"),
        "reason": fusion_result.get("reason"),
        "possible_failure_reasons": possible_reasons,
        "price": price_result,
        "sentiment": sentiment_result,
        "anomaly": anomaly_result,
        "fusion": fusion_result,
    }