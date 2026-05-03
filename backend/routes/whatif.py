from fastapi import APIRouter, Query
from ..models import price_model, sentiment_model, anomaly_model
from ..engines.fusion import fuse
from ..utils import load_ohlcv

router = APIRouter(prefix="/whatif", tags=["What-If Analysis"])


@router.get("/{symbol}")
def what_if_analysis(
    symbol: str,
    sentiment_shift: float = Query(default=0.0, ge=-1.0, le=1.0),
    anomaly_score: float | None = Query(default=None, ge=0.0, le=1.0),
):
    symbol = symbol.upper().strip()

    df = load_ohlcv(symbol)

    sentiment_result = sentiment_model.analyze(symbol)
    anomaly_result = anomaly_model.detect(df)

    # Apply shift
    sentiment_result["positive"] = max(
        0.0, min(1.0, sentiment_result.get("positive", 0.33) + sentiment_shift)
    )
    sentiment_result["negative"] = max(
        0.0, min(1.0, sentiment_result.get("negative", 0.33) - sentiment_shift)
    )

    total = (
        sentiment_result["positive"]
        + sentiment_result.get("neutral", 0.34)
        + sentiment_result["negative"]
    )

    sentiment_result["positive"] /= total
    sentiment_result["neutral"] /= total
    sentiment_result["negative"] /= total

    if anomaly_score is not None:
        anomaly_result["anomaly_score"] = anomaly_score
        anomaly_result["is_anomaly"] = anomaly_score >= 0.75

    # ✅ FIX HERE
    price_result = price_model.predict(
        symbol,
        sentiment=sentiment_result,
        anomaly=anomaly_result,
    )

    fusion_result = fuse(price_result, sentiment_result, anomaly_result)

    return {
        "success": True,
        "symbol": symbol,
        "scenario": {
            "sentiment_shift": sentiment_shift,
            "anomaly_score_override": anomaly_score,
        },
        "price": price_result,
        "sentiment": sentiment_result,
        "anomaly": anomaly_result,
        "fusion": fusion_result,
    }