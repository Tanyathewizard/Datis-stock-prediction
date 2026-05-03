"""
main.py — Unified FastAPI entrypoint for DATIS backend

Run:
    uvicorn backend.main:app --reload --port 8000
"""

from pathlib import Path
import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import APP_TITLE, APP_VERSION, APP_DESCRIPTION, CORS_ORIGINS
from .models import price_model, sentiment_model, anomaly_model
from .engines.fusion import fuse
from .engines.contradiction import (
    _rule_positive_sentiment_falling_price,
    _rule_bullish_trend_anomaly,
    _rule_negative_sentiment_rising_price,
    _rule_model_disagreement,
    _rule_volume_anomaly_no_price_move,
)
from .utils import load_ohlcv
from .blockchain.database.history_db import init_db

from .routes.explain import router as explain_router
from .routes.whatif import router as whatif_router
from .routes.persona import router as persona_router
from .routes.portfolio import router as portfolio_router
from .routes.failure import router as failure_router
from .routes.blockchain import router as blockchain_router
from .routes.history import router as history_router
from .routes.trust import router as trust_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time(request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)},
    )


app.include_router(explain_router, prefix="/api")
app.include_router(whatif_router, prefix="/api")
app.include_router(persona_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(failure_router, prefix="/api")
app.include_router(blockchain_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(trust_router, prefix="/api")


frontend_path = Path(__file__).parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")


@app.get("/api/health", tags=["Health"])
def health():
    return {"success": True, "status": "ok"}


@app.get("/api/predict/{symbol}", tags=["Prediction"])
def predict(symbol: str):
    try:
        symbol = symbol.upper().strip()

        df = load_ohlcv(symbol)

        sentiment_result = sentiment_model.analyze(symbol)
        anomaly_result = anomaly_model.detect(df)

        price_result = price_model.predict(
            symbol,
            sentiment=sentiment_result,
            anomaly=anomaly_result,
        )

        fusion_result = fuse(price_result, sentiment_result, anomaly_result)

        rules = [
            _rule_positive_sentiment_falling_price(price_result, sentiment_result),
            _rule_bullish_trend_anomaly(price_result, anomaly_result),
            _rule_negative_sentiment_rising_price(price_result, sentiment_result),
            _rule_model_disagreement(price_result, sentiment_result, anomaly_result),
            _rule_volume_anomaly_no_price_move(price_result, anomaly_result),
        ]

        contradictions = [rule for rule in rules if rule is not None]

        return {
            "success": True,
            "symbol": symbol,
            "price": price_result,
            "sentiment": sentiment_result,
            "anomaly": anomaly_result,
            "fusion": fusion_result,
            "contradictions": contradictions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sentiment/{symbol}", tags=["Sentiment"])
def get_sentiment(symbol: str, text: str | None = None):
    symbol = symbol.upper().strip()
    return sentiment_model.analyze(symbol, text)


@app.get("/", include_in_schema=False)
def root():
    if frontend_path.exists():
        return RedirectResponse(url="/frontend/index.html")

    return {
        "success": True,
        "message": "DATIS Backend is running",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.on_event("startup")
async def startup_event():
    init_db()

    print("=" * 60)
    print(" DATIS Backend — Unified Server")
    print(f" Version : {APP_VERSION}")
    print(" Status  : Running")
    print(" Docs    : http://localhost:8000/docs")
    print(" Frontend: http://localhost:8000/frontend/index.html")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )