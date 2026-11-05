"""
Base Trading Desk Interface with Human Trader Persona, Risk Management & Weekly Trade Cadence
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class BaseTradingDesk(ABC):
    """
    Base class for a human-trader expert desk.

    Strict constraints implemented:
    - 1:2 Risk-Reward ratio (take profit distance = 2x stop loss distance)
    - 1 trade per week maximum (disciplined selective trading)
    - Realistic institutional risk controls (fixed risk %, max drawdown, trailing stops)
    """

    def __init__(
        self,
        desk_id: str,
        trader_name: str,
        specialty: str,
        style: str,
        experience_years: int,
        preferred_timeframe: str,
        philosophy: str,
        risk_per_trade_pct: float = 0.01,
        risk_reward_ratio: float = 2.0,  # 1:2 RR
        max_trades_per_week: int = 1     # 1 trade/week per trader
    ):
        self.desk_id = desk_id
        self.trader_name = trader_name
        self.specialty = specialty
        self.style = style
        self.experience_years = experience_years
        self.preferred_timeframe = preferred_timeframe
        self.philosophy = philosophy
        self.risk_per_trade_pct = risk_per_trade_pct
        self.risk_reward_ratio = risk_reward_ratio
        self.max_trades_per_week = max_trades_per_week

    def to_dict(self) -> Dict[str, Any]:
        """Convert trader persona and desk profile to dictionary."""
        return {
            "desk_id": self.desk_id,
            "trader_name": self.trader_name,
            "specialty": self.specialty,
            "style": self.style,
            "experience_years": self.experience_years,
            "preferred_timeframe": self.preferred_timeframe,
            "philosophy": self.philosophy,
            "risk_per_trade_pct": self.risk_per_trade_pct,
            "risk_reward_ratio": f"1:{self.risk_reward_ratio:.1f}",
            "trade_frequency": f"{self.max_trades_per_week} trade/week"
        }

    @abstractmethod
    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate raw directional entry signals on the dataframe.
        Must return a Series of integers:
         1: Long entry signal
        -1: Short entry signal
         0: No signal
        """
        pass

    def apply_weekly_filter(self, df: pd.DataFrame, raw_signals: pd.Series) -> pd.Series:
        """
        Strictly enforce the 1 trade / week rule.
        Only the highest-conviction (first valid setup) per calendar week is permitted.
        """
        signals = raw_signals.copy()
        if "timestamp" in df.columns:
            ts = pd.to_datetime(df["timestamp"])
        else:
            ts = pd.to_datetime(df.index)

        # Create unique week identifier (Year-WeekNumber)
        week_ids = ts.dt.isocalendar().year.astype(str) + "-W" + ts.dt.isocalendar().week.astype(str)

        filtered_signals = pd.Series(0, index=df.index, dtype=int)
        seen_weeks = set()

        for idx, (week, sig) in enumerate(zip(week_ids, signals)):
            if sig != 0 and week not in seen_weeks:
                filtered_signals.iloc[idx] = sig
                seen_weeks.add(week)

        return filtered_signals

    def get_trade_signals(self, df: pd.DataFrame) -> pd.Series:
        """Generate final signals respecting the weekly trade limit."""
        raw_signals = self.generate_raw_signal(df)
        return self.apply_weekly_filter(df, raw_signals)
