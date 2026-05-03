from fastapi import APIRouter, Query

router = APIRouter(prefix="/persona", tags=["Persona"])


@router.get("/{persona_type}")
def get_persona_strategy(
    persona_type: str,
    risk_level: str = Query(default="medium"),
):
    persona_type = persona_type.lower().strip()
    risk_level = risk_level.lower().strip()

    strategies = {
        "beginner": {
            "style": "Safe and simple",
            "recommendation": "Prefer HOLD or low-risk BUY signals only.",
            "max_risk": "low",
        },
        "trader": {
            "style": "Active trading",
            "recommendation": "Use BUY/SELL signals with confidence above 0.65.",
            "max_risk": "medium",
        },
        "investor": {
            "style": "Long-term investing",
            "recommendation": "Focus on trend, fundamentals, and low anomaly risk.",
            "max_risk": "medium",
        },
        "aggressive": {
            "style": "High-risk high-reward",
            "recommendation": "Can act on strong BUY/SELL signals if confidence is high.",
            "max_risk": "high",
        },
    }

    if persona_type not in strategies:
        return {
            "success": False,
            "message": "Invalid persona type",
            "available_personas": list(strategies.keys()),
        }

    return {
        "success": True,
        "persona": persona_type,
        "risk_level": risk_level,
        "strategy": strategies[persona_type],
    }


@router.get("/")
def list_personas():
    return {
        "success": True,
        "personas": ["beginner", "trader", "investor", "aggressive"],
    }