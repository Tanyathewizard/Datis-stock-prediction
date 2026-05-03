"""
routes/history.py
─────────────────
FastAPI router for prediction history.

GET  /history             – all predictions (paginated, optional symbol filter)
GET  /history/{symbol}    – history for a specific ticker
POST /history/outcome     – manually update a prediction's outcome
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ..blockchain.database.history_db import (
    fetch_all_history,
    fetch_resolved_predictions,
    update_outcome,
    update_outcome_by_token,
    count_predictions,
)

router = APIRouter(prefix="/history", tags=["History"])


# ─── Request Models ──────────────────────────────────────────────────────────

class OutcomeUpdate(BaseModel):
    prediction_id:    Optional[int]   = Field(None,  example=42)
    token_id:         Optional[str]   = Field(None,  example="123456789012")
    actual_result:    str             = Field(...,   example="CORRECT")
    price_at_resolve: Optional[float] = Field(None,  example=193.50)


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", summary="Full prediction history")
def get_history(
    symbol: Optional[str] = Query(None,  description="Filter by ticker symbol"),
    limit:  int           = Query(50,    ge=1, le=500, description="Max records to return"),
    offset: int           = Query(0,     ge=0,          description="Pagination offset"),
):
    """
    Returns all stored predictions, newest first.

    Each record includes:
    - `id`               – internal DB id
    - `symbol`           – ticker (AAPL, TSLA …)
    - `decision`         – BUY | SELL | HOLD
    - `confidence`       – model confidence 0.0–1.0
    - `timestamp`        – unix epoch
    - `token_id`         – blockchain token id (if stored on-chain)
    - `actual_result`    – CORRECT | INCORRECT | PENDING
    - `price_at_predict` – price when prediction was made
    - `price_at_resolve` – price when outcome was recorded
    """
    records = fetch_all_history(symbol=symbol, limit=limit, offset=offset)
    counts  = count_predictions()
    return {
        "total_in_db":  counts["total"],
        "correct":      counts["correct"],
        "incorrect":    counts["incorrect"],
        "pending":      counts["pending"],
        "returned":     len(records),
        "predictions":  records,
    }


@router.get("/resolved", summary="Only resolved (non-pending) predictions")
def get_resolved(
    symbol: Optional[str] = Query(None, description="Filter by ticker symbol"),
):
    """
    Returns only predictions that have had their outcome recorded.
    Useful for backtesting and trust score review.
    """
    records = fetch_resolved_predictions(symbol=symbol)
    return {
        "count":       len(records),
        "predictions": records,
    }


@router.get("/{symbol}", summary="History for a specific ticker")
def get_history_by_symbol(symbol: str):
    """Shortcut: returns full history for one ticker (e.g. /history/AAPL)."""
    records = fetch_all_history(symbol=symbol.upper())
    return {
        "symbol":      symbol.upper(),
        "count":       len(records),
        "predictions": records,
    }


@router.post("/outcome", summary="Record the actual outcome of a prediction")
def record_outcome(body: OutcomeUpdate):
    """
    After a prediction's window has passed, record whether it was correct.

    Supply either `prediction_id` (DB row id) or `token_id` (blockchain token).
    `actual_result` must be **CORRECT** or **INCORRECT**.
    """
    valid = {"CORRECT", "INCORRECT"}
    if body.actual_result.upper() not in valid:
        raise HTTPException(
            status_code=422,
            detail=f"actual_result must be one of: {valid}"
        )

    updated = False
    if body.prediction_id is not None:
        updated = update_outcome(
            prediction_id    = body.prediction_id,
            actual_result    = body.actual_result,
            price_at_resolve = body.price_at_resolve,
        )
    elif body.token_id is not None:
        updated = update_outcome_by_token(
            token_id         = body.token_id,
            actual_result    = body.actual_result,
            price_at_resolve = body.price_at_resolve,
        )
    else:
        raise HTTPException(
            status_code=422,
            detail="Provide either prediction_id or token_id."
        )

    if not updated:
        raise HTTPException(status_code=404, detail="Prediction not found.")

    return {
        "success":       True,
        "actual_result": body.actual_result.upper(),
        "message":       "Outcome recorded successfully.",
    }
