from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..utils.db import get_db, _now

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


class TradeRequest(BaseModel):
    symbol: str = Field(..., example="RELIANCE")
    action: str = Field(..., example="BUY")
    shares: float = Field(..., gt=0, example=5)
    price: float = Field(..., gt=0, example=2400.0)


def _get_portfolio_row(cur):
    cur.execute("SELECT * FROM portfolio ORDER BY id LIMIT 1")
    return cur.fetchone()


def _get_holding(cur, symbol: str):
    cur.execute("SELECT * FROM holdings WHERE symbol = ?", (symbol,))
    return cur.fetchone()


@router.post("/trade")
def execute_trade(req: TradeRequest):
    symbol = req.symbol.upper().strip()
    action = req.action.upper().strip()

    if action not in ("BUY", "SELL", "HOLD"):
        raise HTTPException(status_code=400, detail="action must be BUY, SELL, or HOLD")

    conn = get_db()
    cur = conn.cursor()

    portfolio = _get_portfolio_row(cur)

    if not portfolio:
        conn.close()
        raise HTTPException(status_code=500, detail="Portfolio table not initialized")

    cash = float(portfolio["cash"])
    pnl_session = 0.0

    if action == "HOLD":
        conn.close()
        return {
            "success": True,
            "action": "HOLD",
            "symbol": symbol,
            "message": f"HOLD signal for {symbol}. No trade executed.",
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
                detail=f"Insufficient cash. Need ₹{total}, available ₹{round(cash, 2)}",
            )

        new_cash = cash - total

        if holding:
            existing_shares = float(holding["shares"])
            existing_avg = float(holding["avg_price"])

            new_shares = existing_shares + req.shares
            new_avg = ((existing_shares * existing_avg) + total) / new_shares

            cur.execute(
                "UPDATE holdings SET shares=?, avg_price=?, updated_at=? WHERE symbol=?",
                (new_shares, round(new_avg, 4), _now(), symbol),
            )
        else:
            cur.execute(
                "INSERT INTO holdings (symbol, shares, avg_price, updated_at) VALUES (?, ?, ?, ?)",
                (symbol, req.shares, req.price, _now()),
            )

        message = f"Bought {req.shares} shares of {symbol} @ ₹{req.price}"

    else:
        if not holding or float(holding["shares"]) < req.shares:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Not enough shares to sell. Have {holding['shares'] if holding else 0}, need {req.shares}",
            )

        avg_buy = float(holding["avg_price"])
        pnl_session = round((req.price - avg_buy) * req.shares, 2)

        new_cash = cash + total
        new_shares = float(holding["shares"]) - req.shares

        if new_shares <= 0:
            cur.execute("DELETE FROM holdings WHERE symbol=?", (symbol,))
        else:
            cur.execute(
                "UPDATE holdings SET shares=?, updated_at=? WHERE symbol=?",
                (new_shares, _now(), symbol),
            )

        message = f"Sold {req.shares} shares of {symbol} @ ₹{req.price} | PnL: ₹{pnl_session}"

    cur.execute("SELECT SUM(shares * avg_price) FROM holdings")
    holdings_value = cur.fetchone()[0] or 0.0

    total_value = round(new_cash + holdings_value, 2)
    new_pnl = round(total_value - 10000.0, 2)

    cur.execute(
        "UPDATE portfolio SET cash=?, total_value=?, pnl=?, updated_at=? WHERE id=1",
        (round(new_cash, 2), total_value, new_pnl, _now()),
    )

    cur.execute(
        """
        INSERT INTO trade_history 
        (symbol, action, shares, price, total, pnl, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (symbol, action, req.shares, req.price, total, pnl_session, _now()),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
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


@router.get("/")
def get_portfolio():
    conn = get_db()
    cur = conn.cursor()

    portfolio = _get_portfolio_row(cur)

    if not portfolio:
        conn.close()
        raise HTTPException(status_code=500, detail="Portfolio table not initialized")

    cur.execute("SELECT * FROM holdings")
    holdings = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM trade_history ORDER BY id DESC LIMIT 50")
    trades = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "success": True,
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


@router.delete("/reset")
def reset_portfolio():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM trade_history")
    cur.execute("DELETE FROM holdings")
    cur.execute(
        "UPDATE portfolio SET cash=10000.0, total_value=10000.0, pnl=0.0, updated_at=? WHERE id=1",
        (_now(),),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Portfolio reset to ₹10,000",
        "timestamp": _now(),
    }