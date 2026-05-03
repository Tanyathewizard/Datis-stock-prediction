from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])


class StorePredictionRequest(BaseModel):
    symbol: str
    prediction: str
    confidence: int
    price: float


class UpdateResultRequest(BaseModel):
    token_id: str
    actual_result: str
    resolution_price: float


# ✅ Wallet (mock)
@router.get("/wallet")
def wallet_status():
    return {"status": "connected (mock)"}


# ✅ Store (mock, no blocking)
@router.post("/store")
def store_prediction(body: StorePredictionRequest):
    return {
        "success": True,
        "token_id": f"mock_{body.symbol}",
        "message": "Stored successfully (mock)"
    }


# ✅ Update (mock)
@router.post("/update")
def update_result(body: UpdateResultRequest):
    return {
        "success": True,
        "message": "Updated successfully (mock)"
    }


# ✅ Get token
@router.get("/token/{token_id}")
def get_token(token_id: str):
    return {"token_id": token_id, "status": "mock_data"}