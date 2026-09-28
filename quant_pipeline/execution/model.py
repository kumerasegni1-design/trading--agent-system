"""
Realistic execution models including variable spreads, volatility-based slippage,
broker commissions, limit fill probability, latency, and economic news filter.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


class ExecutionModel:
    """
    Simulates realistic broker market conditions and execution frictions.
    """

    def __init__(
        self,
        asset_type: str = "fx",  # 'fx', 'indices', 'crypto'
        base_commission: float = 3.5,  # $3.5 per 100k round turn for FX
        latency_ms: int = 100,  # Execution delay in milliseconds
    ):
        self.asset_type = asset_type
        self.base_commission = base_commission
        self.latency_ms = latency_ms

    def get_slippage(self, price: float, volatility: float, is_news_time: bool = False) -> float:
        """
        Computes realistic slippage based on asset class, volatility, and news environment.
        FX: 0.5 - 2 pips
        Indices: 1 - 5 points
        Crypto: 0.05% - 0.3%
        """
        mult = 2.5 if is_news_time else 1.0

        if self.asset_type == "fx":
            base_pips = np.random.uniform(0.00005, 0.00020)
            slippage = base_pips * mult * (1.0 + volatility * 100)
        elif self.asset_type == "indices":
            base_points = np.random.uniform(1.0, 5.0)
            slippage = base_points * mult
        else:  # crypto
            pct = np.random.uniform(0.0005, 0.003)
            slippage = price * pct * mult

        return slippage

    def get_commission(self, price: float, position_size: float) -> float:
        """
        Calculates trading fees/commissions per trade.
        """
        if self.asset_type == "fx":
            # $3.5 per 100,000 units
            return (position_size / 100000.0) * self.base_commission
        elif self.asset_type == "crypto":
            # 0.05% taker fee
            return price * position_size * 0.0005
        else:
            # $1 per contract for indices
            return position_size * 1.0

    @staticmethod
    def is_news_event(timestamp: pd.Timestamp) -> bool:
        """
        News Filter: Excludes entries near major news releases (NFP, FOMC, CPI).
        Simulated based on fixed calendar windows (e.g. 1st Friday of month 12:00-14:00 UTC, Wednesdays 18:00 UTC).
        """
        if timestamp.weekday() == 4 and timestamp.day <= 7 and 12 <= timestamp.hour <= 14:
            return True  # NFP window
        if timestamp.weekday() == 2 and 18 <= timestamp.hour <= 20:
            return True  # FOMC window
        return False
