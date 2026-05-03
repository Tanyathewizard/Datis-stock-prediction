
import json
import math
import random
import sqlite3
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler

# Optional SHAP import — graceful fallback if not installed
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

# ──────────────────────────────────────────────────────────────────────────────
# App bootstrap
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DATIS Part 2 API",
    description="Explainability · What-If · Persona · Portfolio · Failure Learning",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────────────
# ─── DATABASE LAYER ───────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

DB_PATH = "datis_portfolio.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cash        REAL    NOT NULL DEFAULT 10000.0,
            total_value REAL    NOT NULL DEFAULT 10000.0,
            pnl         REAL    NOT NULL DEFAULT 0.0,
            updated_at  TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT    NOT NULL UNIQUE,
            shares     REAL    NOT NULL DEFAULT 0,
            avg_price  REAL    NOT NULL DEFAULT 0,
            updated_at TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol     TEXT NOT NULL,
            action     TEXT NOT NULL,
            shares     REAL NOT NULL,
            price      REAL NOT NULL,
            total      REAL NOT NULL,
            pnl        REAL NOT NULL DEFAULT 0,
            timestamp  TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prediction_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol      TEXT NOT NULL,
            predicted   TEXT NOT NULL,
            actual      TEXT,
            confidence  REAL,
            features    TEXT,
            timestamp   TEXT NOT NULL
        )
    """)

    # Seed portfolio if empty
    cur.execute("SELECT COUNT(*) FROM portfolio")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO portfolio (cash, total_value, pnl, updated_at) VALUES (?, ?, ?, ?)",
            (10000.0, 10000.0, 0.0, _now()),
        )

    conn.commit()
    conn.close()


def _now() -> str:
    return datetime.utcnow().isoformat()


init_db()


# ──────────────────────────────────────────────────────────────────────────────
# ─── SHARED UTILITIES ─────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

FEATURE_NAMES = ["sentiment", "trend", "volume", "anomaly_score"]


def _mock_feature_vector(symbol: str) -> Dict[str, float]:
    """
    Deterministic mock feature vector for a symbol.
    In production: replace with real feature extraction from Part 1 pipeline.
    """
    rng = random.Random(hash(symbol) % (2**31))
    return {
        "sentiment":     round(rng.uniform(-1, 1), 4),
        "trend":         round(rng.uniform(-1, 1), 4),
        "volume":        round(rng.uniform(0, 1), 4),
        "anomaly_score": round(rng.uniform(0, 1), 4),
    }


def _decision_from_features(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Simple rule-based decision engine (mirrors Part 1 logic).
    Replace with your trained model's predict() call.
    """
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
    """SHAP-based importance (linear approximation for demo)."""
    weights = {"sentiment": 0.35, "trend": 0.30, "volume": 0.20, "anomaly_score": -0.15}
    return {k: round(features[k] * weights[k], 5) for k in features}


def _feature_importance_lime(features: Dict[str, float]) -> Dict[str, float]:
    """LIME-style perturbation importance fallback."""
    base = _decision_from_features(features)["raw_score"]
    importance = {}
    for key in features:
        perturbed = dict(features)
        perturbed[key] = features[key] + 0.1
        delta = _decision_from_features(perturbed)["raw_score"] - base
        importance[key] = round(delta, 5)
    return importance


# ──────────────────────────────────────────────────────────────────────────────
# ─── 1. EXPLAINABILITY LAYER ──────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/explain/{symbol}", tags=["Explainability"])
def explain_symbol(symbol: str):
    """
    GET /explain/{symbol}
    Returns feature importance, top reasons, and chart-ready JSON.
    Uses SHAP if available, otherwise falls back to LIME-style perturbation.
    """
    symbol = symbol.upper()
    features = _mock_feature_vector(symbol)
    decision_info = _decision_from_features(features)

    method = "shap" if SHAP_AVAILABLE else "lime"
    importance = _feature_importance_shap(features) if SHAP_AVAILABLE else _feature_importance_lime(features)

    # Sort by absolute contribution
    sorted_importance = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)

    # Build human-readable top reasons
    top_reasons = []
    direction_label = {"BUY": "bullish", "SELL": "bearish", "HOLD": "neutral"}
    for feat, imp in sorted_importance[:3]:
        if imp > 0:
            reason = f"High {feat} ({features[feat]:.3f}) supports a {direction_label[decision_info['decision']]} signal."
        else:
            reason = f"Low {feat} ({features[feat]:.3f}) suppresses the {direction_label[decision_info['decision']]} signal."
        top_reasons.append(reason)

    # Chart-ready JSON (bar chart data)
    chart_data = [
        {
            "feature": feat,
            "importance": imp,
            "raw_value": features[feat],
            "direction": "positive" if imp >= 0 else "negative",
        }
        for feat, imp in sorted_importance
    ]

    return {
        "symbol": symbol,
        "method": method,
        "decision": decision_info["decision"],
        "confidence": decision_info["confidence"],
        "features": features,
        "feature_importance": dict(sorted_importance),
        "top_reasons": top_reasons,
        "chart_data": chart_data,
        "timestamp": _now(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# ─── 2. WHAT-IF SIMULATOR ─────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    symbol: str = Field(..., example="RELIANCE")
    sentiment: Optional[float] = Field(None, ge=-1, le=1)
    trend: Optional[float] = Field(None, ge=-1, le=1)
    volume: Optional[float] = Field(None, ge=0, le=1)
    anomaly_score: Optional[float] = Field(None, ge=0, le=1)


@app.post("/whatif", tags=["What-If Simulator"])
def what_if_simulator(req: WhatIfRequest):
    """
    POST /whatif
    Override any feature values and recalculate decision + explanation.
    Unspecified features use the symbol's default mock values.
    """
    symbol = req.symbol.upper()
    base_features = _mock_feature_vector(symbol)

    # Apply user overrides
    overrides: Dict[str, float] = {}
    if req.sentiment is not None:
        base_features["sentiment"] = req.sentiment
        overrides["sentiment"] = req.sentiment
    if req.trend is not None:
        base_features["trend"] = req.trend
        overrides["trend"] = req.trend
    if req.volume is not None:
        base_features["volume"] = req.volume
        overrides["volume"] = req.volume
    if req.anomaly_score is not None:
        base_features["anomaly_score"] = req.anomaly_score
        overrides["anomaly_score"] = req.anomaly_score

    # Original decision (no overrides)
    original_features = _mock_feature_vector(symbol)
    original = _decision_from_features(original_features)

    # New decision
    new_decision_info = _decision_from_features(base_features)
    importance = _feature_importance_shap(base_features) if SHAP_AVAILABLE else _feature_importance_lime(base_features)

    sorted_importance = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)
    top_reasons = []
    for feat, imp in sorted_importance[:2]:
        tag = "drove" if abs(imp) > 0.05 else "slightly influenced"
        top_reasons.append(f"{feat}={base_features[feat]:.3f} {tag} the {new_decision_info['decision']} call.")

    decision_changed = original["decision"] != new_decision_info["decision"]

    return {
        "symbol": symbol,
        "overrides_applied": overrides,
        "original": {
            "decision": original["decision"],
            "confidence": original["confidence"],
        },
        "simulated": {
            "decision": new_decision_info["decision"],
            "confidence": new_decision_info["confidence"],
            "raw_score": new_decision_info["raw_score"],
        },
        "decision_changed": decision_changed,
        "features_used": base_features,
        "feature_importance": dict(sorted_importance),
        "top_reasons": top_reasons,
        "timestamp": _now(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# ─── 3. MARKET PERSONA DETECTION ──────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

# Persona cluster definitions (cluster index → label)
PERSONA_MAP = {
    0: "Bullish",
    1: "Bearish",
    2: "Smart Money",
    3: "Manipulated",
}

# Reference cluster centres (trained offline on synthetic data)
# Columns: [sentiment, trend, volume, anomaly_score]
_REFERENCE_CENTRES = np.array([
    [ 0.70,  0.65,  0.60,  0.10],  # Bullish
    [-0.70, -0.65,  0.40,  0.15],  # Bearish
    [ 0.30,  0.25,  0.85,  0.05],  # Smart Money (high volume, low anomaly)
    [-0.10,  0.10,  0.70,  0.90],  # Manipulated (high anomaly)
])


def _detect_persona(features: Dict[str, float]) -> Dict[str, Any]:
    vec = np.array([[features["sentiment"], features["trend"],
                     features["volume"], features["anomaly_score"]]])

    distances = np.linalg.norm(_REFERENCE_CENTRES - vec, axis=1)
    cluster_idx = int(np.argmin(distances))
    persona = PERSONA_MAP[cluster_idx]

    # Confidence: inverse normalised distance
    min_d = distances[cluster_idx]
    max_d = distances.max()
    confidence = round(1 - (min_d / (max_d + 1e-9)), 4)

    # All cluster scores for chart
    cluster_scores = {
        PERSONA_MAP[i]: round(float(1 - distances[i] / (distances.max() + 1e-9)), 4)
        for i in range(len(PERSONA_MAP))
    }

    return {
        "persona": persona,
        "confidence": confidence,
        "cluster_index": cluster_idx,
        "cluster_distances": {PERSONA_MAP[i]: round(float(distances[i]), 5) for i in range(4)},
        "cluster_scores": cluster_scores,
    }


@app.get("/persona/{symbol}", tags=["Market Persona"])
def get_persona(symbol: str, method: str = "kmeans"):
    """
    GET /persona/{symbol}?method=kmeans|dbscan
    Classifies market regime: Bullish / Bearish / Smart Money / Manipulated.
    """
    symbol = symbol.upper()
    features = _mock_feature_vector(symbol)
    result = _detect_persona(features)

    explanation_map = {
        "Bullish":     "Strong positive sentiment and trend with moderate volume.",
        "Bearish":     "Negative sentiment and trend; selling pressure dominates.",
        "Smart Money": "High volume with controlled sentiment — institutional activity.",
        "Manipulated": "High anomaly score relative to volume — possible wash trading or pump.",
    }

    return {
        "symbol": symbol,
        "method": method,
        "persona": result["persona"],
        "confidence": result["confidence"],
        "explanation": explanation_map[result["persona"]],
        "features": features,
        "cluster_scores": result["cluster_scores"],
        "cluster_distances": result["cluster_distances"],
        "timestamp": _now(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# ─── 4. PORTFOLIO SIMULATION ENGINE ───────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

class TradeRequest(BaseModel):
    symbol: str = Field(..., example="RELIANCE")
    action: str = Field(..., example="BUY")   # BUY | SELL | HOLD
    shares: float = Field(..., gt=0, example=5)
    price: float = Field(..., gt=0, example=2400.0)


def _get_portfolio_row(cur) -> sqlite3.Row:
    cur.execute("SELECT * FROM portfolio ORDER BY id LIMIT 1")
    return cur.fetchone()


def _get_holding(cur, symbol: str) -> Optional[sqlite3.Row]:
    cur.execute("SELECT * FROM holdings WHERE symbol = ?", (symbol,))
    return cur.fetchone()


@app.post("/trade", tags=["Portfolio"])
def execute_trade(req: TradeRequest):
    """
    POST /trade
    Execute BUY / SELL / HOLD against the simulated ₹10,000 portfolio.
    """
    symbol = req.symbol.upper()
    action = req.action.upper()

    if action not in ("BUY", "SELL", "HOLD"):
        raise HTTPException(status_code=400, detail="action must be BUY, SELL, or HOLD")

    conn = get_db()
    cur = conn.cursor()
    portfolio = _get_portfolio_row(cur)
    cash = portfolio["cash"]
    pnl_session = 0.0
    message = ""

    if action == "HOLD":
        message = f"HOLD signal for {symbol}. No trade executed."
        conn.close()
        return {
            "action": "HOLD",
            "symbol": symbol,
            "message": message,
            "cash": round(cash, 2),
            "timestamp": _now(),
        }

    total = round(req.shares * req.price, 2)
    holding = _get_holding(cur, symbol)

    if action == "BUY":
        if cash < total:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient cash. Need ₹{total}, available ₹{round(cash, 2)}"
            )

        new_cash = cash - total
        if holding:
            existing_shares = holding["shares"]
            existing_avg = holding["avg_price"]
            new_shares = existing_shares + req.shares
            new_avg = ((existing_shares * existing_avg) + total) / new_shares
            cur.execute(
                "UPDATE holdings SET shares=?, avg_price=?, updated_at=? WHERE symbol=?",
                (new_shares, round(new_avg, 4), _now(), symbol),
            )
        else:
            cur.execute(
                "INSERT INTO holdings (symbol, shares, avg_price, updated_at) VALUES (?,?,?,?)",
                (symbol, req.shares, req.price, _now()),
            )
        message = f"Bought {req.shares} shares of {symbol} @ ₹{req.price}"

    elif action == "SELL":
        if not holding or holding["shares"] < req.shares:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Not enough shares to sell. Have {holding['shares'] if holding else 0}, need {req.shares}",
            )
        avg_buy = holding["avg_price"]
        pnl_session = round((req.price - avg_buy) * req.shares, 2)
        new_cash = cash + total
        new_shares = holding["shares"] - req.shares
        if new_shares <= 0:
            cur.execute("DELETE FROM holdings WHERE symbol=?", (symbol,))
        else:
            cur.execute(
                "UPDATE holdings SET shares=?, updated_at=? WHERE symbol=?",
                (new_shares, _now(), symbol),
            )
        message = f"Sold {req.shares} shares of {symbol} @ ₹{req.price} | PnL: ₹{pnl_session}"

    # Recalculate total portfolio value
    cur.execute("SELECT SUM(shares * avg_price) FROM holdings")
    holdings_value = cur.fetchone()[0] or 0.0
    total_value = round(new_cash + holdings_value, 2)
    new_pnl = round(total_value - 10000.0, 2)

    cur.execute(
        "UPDATE portfolio SET cash=?, total_value=?, pnl=?, updated_at=? WHERE id=1",
        (round(new_cash, 2), total_value, new_pnl, _now()),
    )

    cur.execute(
        "INSERT INTO trade_history (symbol, action, shares, price, total, pnl, timestamp) VALUES (?,?,?,?,?,?,?)",
        (symbol, action, req.shares, req.price, total, pnl_session, _now()),
    )

    conn.commit()
    conn.close()

    return {
        "action": action,
        "symbol": symbol,
        "shares": req.shares,
        "price": req.price,
        "total": total,
        "pnl_this_trade": pnl_session,
        "cash_remaining": round(new_cash, 2),
        "portfolio_value": total_value,
        "overall_pnl": new_pnl,
        "message": message,
        "timestamp": _now(),
    }


@app.get("/portfolio", tags=["Portfolio"])
def get_portfolio():
    """
    GET /portfolio
    Returns current cash, holdings, total PnL, and full trade history.
    """
    conn = get_db()
    cur = conn.cursor()

    portfolio = _get_portfolio_row(cur)

    cur.execute("SELECT * FROM holdings")
    holdings = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM trade_history ORDER BY id DESC LIMIT 50")
    trades = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "starting_capital": 10000.0,
        "cash": portfolio["cash"],
        "total_value": portfolio["total_value"],
        "pnl": portfolio["pnl"],
        "pnl_pct": round((portfolio["pnl"] / 10000.0) * 100, 2),
        "holdings": holdings,
        "trade_count": len(trades),
        "trade_history": trades,
        "updated_at": portfolio["updated_at"],
    }


@app.delete("/portfolio/reset", tags=["Portfolio"])
def reset_portfolio():
    """
    DELETE /portfolio/reset
    Wipe all trades and reset to ₹10,000 starting capital.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM trade_history")
    cur.execute("DELETE FROM holdings")
    cur.execute("UPDATE portfolio SET cash=10000.0, total_value=10000.0, pnl=0.0, updated_at=?", (_now(),))
    conn.commit()
    conn.close()
    return {"message": "Portfolio reset to ₹10,000", "timestamp": _now()}


# ──────────────────────────────────────────────────────────────────────────────
# ─── 5. FAILURE LEARNING MODULE ───────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

class PredictionLogRequest(BaseModel):
    symbol: str
    predicted: str   # BUY | SELL | HOLD
    actual: str      # BUY | SELL | HOLD  (ground truth after the fact)
    confidence: float = Field(..., ge=0, le=1)
    features: Dict[str, float]


@app.post("/log_prediction", tags=["Failure Learning"])
def log_prediction(req: PredictionLogRequest):
    """
    POST /log_prediction
    Store a prediction + actual outcome for failure analysis.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO prediction_log (symbol, predicted, actual, confidence, features, timestamp) VALUES (?,?,?,?,?,?)",
        (req.symbol.upper(), req.predicted, req.actual, req.confidence,
         json.dumps(req.features), _now()),
    )
    conn.commit()
    conn.close()
    return {"message": "Prediction logged.", "timestamp": _now()}


@app.get("/failure_analysis/{symbol}", tags=["Failure Learning"])
def failure_analysis(symbol: str, limit: int = 20):
    """
    GET /failure_analysis/{symbol}
    Analyse wrong predictions: why they failed, misleading signals, confidence errors.
    """
    symbol = symbol.upper()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM prediction_log WHERE symbol=? ORDER BY id DESC LIMIT ?",
        (symbol, limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    if not rows:
        return {
            "symbol": symbol,
            "message": "No predictions logged yet for this symbol.",
            "failures": [],
        }

    failures = []
    feature_error_accumulator: Dict[str, List[float]] = {f: [] for f in FEATURE_NAMES}

    for row in rows:
        if row["actual"] and row["predicted"] != row["actual"]:
            features = json.loads(row["features"]) if row["features"] else {}
            importance = (
                _feature_importance_shap(features) if SHAP_AVAILABLE
                else _feature_importance_lime(features)
            ) if features else {}

            misleading = []
            for feat, imp in importance.items():
                actual_direction = row["actual"]
                pred_direction = row["predicted"]
                if (imp > 0.05 and pred_direction == "BUY" and actual_direction == "SELL") or \
                   (imp < -0.05 and pred_direction == "SELL" and actual_direction == "BUY"):
                    misleading.append({
                        "feature": feat,
                        "value": features.get(feat),
                        "importance": imp,
                        "reason": f"{feat} pushed toward {pred_direction} but market went {actual_direction}",
                    })
                feature_error_accumulator[feat].append(abs(imp))

            confidence_error = "overconfident" if row["confidence"] > 0.7 else "underconfident"
            failure_reason = (
                f"Model predicted {row['predicted']} with "
                f"{row['confidence']:.0%} confidence but actual was {row['actual']}. "
                f"Model was {confidence_error}."
            )

            failures.append({
                "timestamp": row["timestamp"],
                "predicted": row["predicted"],
                "actual": row["actual"],
                "confidence": row["confidence"],
                "confidence_error": confidence_error,
                "failure_reason": failure_reason,
                "misleading_signals": misleading,
                "features": features,
            })

    # Aggregate: which feature caused most errors
    avg_error_by_feature = {
        feat: round(float(np.mean(vals)), 5) if vals else 0.0
        for feat, vals in feature_error_accumulator.items()
    }
    most_misleading_feature = max(avg_error_by_feature, key=avg_error_by_feature.get)

    total = len(rows)
    wrong = len(failures)
    accuracy = round((total - wrong) / total * 100, 1) if total else 0

    return {
        "symbol": symbol,
        "total_predictions": total,
        "wrong_predictions": wrong,
        "accuracy_pct": accuracy,
        "most_misleading_feature": most_misleading_feature,
        "avg_feature_error_contribution": avg_error_by_feature,
        "failures": failures,
        "timestamp": _now(),
    }


@app.get("/failure_summary", tags=["Failure Learning"])
def failure_summary():
    """
    GET /failure_summary
    Global failure stats across all symbols.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT symbol, COUNT(*) as total, SUM(CASE WHEN predicted != actual THEN 1 ELSE 0 END) as wrong FROM prediction_log GROUP BY symbol")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    summary = []
    for row in rows:
        total = row["total"]
        wrong = row["wrong"] or 0
        summary.append({
            "symbol": row["symbol"],
            "total": total,
            "wrong": wrong,
            "accuracy_pct": round((total - wrong) / total * 100, 1) if total else 0,
        })

    return {"summary": summary, "timestamp": _now()}


# ──────────────────────────────────────────────────────────────────────────────
# ─── HEALTH & ROOT ────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "service": "DATIS Part 2",
        "status": "running",
        "shap_available": SHAP_AVAILABLE,
        "endpoints": [
            "GET  /explain/{symbol}",
            "POST /whatif",
            "GET  /persona/{symbol}",
            "POST /trade",
            "GET  /portfolio",
            "DELETE /portfolio/reset",
            "POST /log_prediction",
            "GET  /failure_analysis/{symbol}",
            "GET  /failure_summary",
        ],
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "timestamp": _now()}


# ──────────────────────────────────────────────────────────────────────────────
# ─── ENTRYPOINT ───────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
# DISABLED STANDALONE SERVER - Integrated into main.py port 8000
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)

