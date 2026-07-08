import logging
import json
import os
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from datetime import datetime

logger = logging.getLogger(__name__)

class ChannelRankerAgent(BaseAgent):
    """
    Agent responsible for ranking signal providers and detecting scams
    by comparing their claimed results with backtested reality.
    """

    def __init__(self, event_bus):
        super().__init__(event_bus, "ChannelRankerAgent")
        self.persistence_file = "channel_stats.json"
        self.channel_stats = self._load_stats()

    def _load_stats(self) -> Dict:
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load stats: {e}")
        return {}

    def _save_stats(self):
        try:
            with open(self.persistence_file, 'w') as f:
                json.dump(self.channel_stats, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Failed to save stats: {e}")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        task_id = task.get("task_id")

        if task_type == "rank_channels":
            result = await self.rank_channels()
        elif task_type == "update_stats":
            result = await self.update_channel_stats(task)
        else:
            result = {"status": "error", "message": f"Unknown task type: {task_type}"}

        await self.log_task(task_id, "completed", result)
        return result

    async def update_channel_stats(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update statistics for a specific channel based on a backtest result"""
        channel_id = task.get("channel_id")
        backtest_result = task.get("backtest_result")
        provider_claim = task.get("provider_claim") # What the provider said the result was

        if channel_id not in self.channel_stats:
            self.channel_stats[channel_id] = {
                "total_signals": 0,
                "verified_win_rate": 0.0,
                "claimed_win_rate": 0.0,
                "authenticity_score": 1.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "signals": []
            }

        stats = self.channel_stats[channel_id]
        stats["total_signals"] += 1
        stats["signals"].append({
            "timestamp": datetime.now().isoformat(),
            "backtest": backtest_result,
            "claim": provider_claim
        })

        # Calculate authenticity score (0.0 to 1.0)
        # Lower score if provider claims TP but backtest shows SL or no entry
        if provider_claim:
            stats["authenticity_score"] = self._calculate_authenticity(stats["signals"])

        # Update performance metrics
        stats["verified_win_rate"] = sum(1 for s in stats["signals"] if s["backtest"]["net_profit"] > 0) / len(stats["signals"])

        self._save_stats()
        return {"status": "success", "channel_id": channel_id, "current_stats": stats}

    def _calculate_authenticity(self, signals: List[Dict]) -> float:
        """Compare backtest results with provider claims to detect fake results"""
        matches = 0
        for s in signals:
            if not s["claim"]: continue

            # Simple logic: if provider claimed profit but backtest shows loss
            backtest_profit = s["backtest"]["net_profit"] > 0
            claim_profit = s["claim"].get("profit", False)

            if backtest_profit == claim_profit:
                matches += 1

        return matches / len([s for s in signals if s["claim"]]) if signals else 1.0

    async def rank_channels(self) -> List[Dict]:
        """Rank all channels based on performance and authenticity"""
        ranked = []
        for cid, stats in self.channel_stats.items():
            rank_score = (stats["verified_win_rate"] * 0.4 +
                          stats["authenticity_score"] * 0.4 +
                          (1 - stats["max_drawdown"]/100) * 0.2)

            ranked.append({
                "channel_id": cid,
                "rank_score": rank_score,
                "win_rate": stats["verified_win_rate"],
                "authenticity": stats["authenticity_score"],
                "is_scam": stats["authenticity_score"] < 0.6
            })

        ranked.sort(key=lambda x: x["rank_score"], reverse=True)
        return ranked
