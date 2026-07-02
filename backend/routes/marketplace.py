from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter()

@router.get("/strategies")
async def list_strategies() -> Dict[str, List[Dict]]:
    """List all approved strategies"""
    return {"strategies": []}

@router.get("/models")
async def list_models() -> Dict[str, List[Dict]]:
    """List all deployed models"""
    return {"models": []}

@router.get("/stats")
async def get_marketplace_stats() -> Dict[str, Any]:
    """Get marketplace statistics"""
    return {
        "total_strategies": 0,
        "total_models": 0,
        "total_pnl": 0.0
    }
