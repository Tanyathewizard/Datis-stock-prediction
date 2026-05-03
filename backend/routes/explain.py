from fastapi import APIRouter, Query
from ..models import price_model, sentiment_model, anomaly_model
from ..engines.fusion import fuse
from ..utils import load_ohlcv

router = APIRouter(prefix="/explain", tags=["Explainability"])


@router.get("/{symbol}")
def explain_prediction(symbol: str, text: str | None = Query(default=None)):
    symbol = symbol.upper().strip()

    df = load_ohlcv(symbol)

    sentiment_result = sentiment_model.analyze(symbol, text)
    anomaly_result = anomaly_model.detect(df)

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
        "final_action": fusion_result.get("action"),
        "confidence": fusion_result.get("confidence"),
        "reason": fusion_result.get("reason"),
        "market_state": fusion_result.get("market_state"),
        "model_explanation": {
            "price_model": price_result,
            "sentiment_model": sentiment_result,
            "anomaly_model": anomaly_result,
        },
        "fusion_details": fusion_result,
    }