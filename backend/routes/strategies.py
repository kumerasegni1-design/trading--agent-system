from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.post("/generate")
async def generate_strategy(prompt: str) -> Dict[str, Any]:
    """Generate new strategy"""
    return {"strategy_id": "strat_001", "status": "generating"}

@router.get("/{strategy_id}")
async def get_strategy(strategy_id: str) -> Dict[str, Any]:
    """Get strategy details"""
    return {"strategy_id": strategy_id}
