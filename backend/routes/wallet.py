from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])

# =========================
# FILE PATH
# =========================

WALLET_FILE = Path("backend/data/wallet.json")

# =========================
# REQUEST MODEL
# =========================

class WalletRequest(BaseModel):
    amount: float


# =========================
# LOAD WALLET
# =========================

def load_wallet():

    if not WALLET_FILE.exists():

        WALLET_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(WALLET_FILE, "w") as f:
            json.dump({"balance": 50000}, f)

    with open(WALLET_FILE, "r") as f:
        return json.load(f)


# =========================
# SAVE WALLET
# =========================

def save_wallet(data):

    with open(WALLET_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# GET BALANCE
# =========================

@router.get("/")
def get_wallet():

    wallet = load_wallet()

    return {
        "balance": wallet["balance"]
    }


# =========================
# DEPOSIT MONEY
# =========================

@router.post("/deposit")
def deposit_money(payload: WalletRequest):

    wallet = load_wallet()

    if payload.amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    wallet["balance"] += payload.amount

    save_wallet(wallet)

    return {
        "message": "Money added successfully",
        "balance": wallet["balance"]
    }


# =========================
# WITHDRAW MONEY
# =========================

@router.post("/withdraw")
def withdraw_money(payload: WalletRequest):

    wallet = load_wallet()

    if payload.amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    if payload.amount > wallet["balance"]:

        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    wallet["balance"] -= payload.amount

    save_wallet(wallet)

    return {
        "message": "Money withdrawn successfully",
        "balance": wallet["balance"]
    }