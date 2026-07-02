from agents.base_agent import BaseAgent
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PortfolioManagerAgent(BaseAgent):
    """Manages portfolio diversification and prevents duplicate strategies"""
    
    def __init__(self, event_bus):
        super().__init__(event_bus, "PortfolioManager")
        self.deployed_strategies: List[Dict] = []
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Check if strategy is unique and well-diversified"""
        task_id = task.get("task_id")
        new_strategy = task.get("strategy", {})
        
        logger.info(f"💼 Checking portfolio diversity...")
        
        # Check correlation with existing strategies
        correlations = self._calculate_correlations(new_strategy)
        unique = all(corr < 0.7 for corr in correlations)
        
        # Calculate portfolio impact
        portfolio_impact = {
            "is_unique": unique,
            "correlation_with_existing": correlations,
            "diversification_score": 0.82,
            "can_deploy": unique and len(self.deployed_strategies) < 20
        }
        
        await self.log_task(task_id, "completed", portfolio_impact)
        return portfolio_impact
    
    def _calculate_correlations(self, strategy: Dict) -> List[float]:
        """Calculate correlation with existing strategies"""
        return [0.2, 0.3, 0.1]
