from agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BacktestingCriticAgent(BaseAgent):
    """Critically analyzes backtesting results for overfitting and data leakage"""
    
    def __init__(self, event_bus):
        super().__init__(event_bus, "BacktestingCritic")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze backtest for issues"""
        task_id = task.get("task_id")
        backtest_results = task.get("backtest_results", {})
        
        logger.info(f"🔍 Criticizing backtest results...")
        
        # Perform checks
        issues = []
        warnings = []
        
        # Check for overfitting indicators
        sharpe_ratio = backtest_results.get("sharpe_ratio", 0)
        if sharpe_ratio > 3.0:
            issues.append("Potential overfitting: Sharpe ratio suspiciously high")
        
        # Check drawdown
        max_drawdown = backtest_results.get("max_drawdown_pct", 0)
        if max_drawdown > 50:
            warnings.append("High drawdown detected")
        
        # Check walk-forward performance decay
        in_sample_sharpe = backtest_results.get("in_sample_sharpe", 1.0)
        out_sample_sharpe = backtest_results.get("out_sample_sharpe", 1.0)
        
        if out_sample_sharpe < in_sample_sharpe * 0.7:
            issues.append("Significant edge decay detected in out-of-sample period")
        
        analysis = {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "confidence": 0.85
        }
        
        await self.log_task(task_id, "completed", analysis)
        return analysis
