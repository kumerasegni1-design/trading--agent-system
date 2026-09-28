"""
Anchored and Rolling Walk-Forward Optimization Analysis.
Walk-Forward Efficiency (WFE) verification (≥ 50%).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Type
from quant_pipeline.strategies.base import BaseStrategy


class WalkForwardAnalyzer:
    """
    Performs Walk-Forward Optimization (Rolling & Anchored).
    """

    def __init__(self, backtester_class, is_periods: int = 24*30*12, oos_periods: int = 24*30*6, step_periods: int = 24*30*3):
        self.backtester_class = backtester_class
        self.is_periods = is_periods
        self.oos_periods = oos_periods
        self.step_periods = step_periods

    def run(self, df_feat: pd.DataFrame, strategy_class: Type[BaseStrategy]) -> Dict[str, Any]:
        n = len(df_feat)
        window_start = 0
        is_returns = []
        oos_returns = []
        profitable_oos_windows = 0
        total_windows = 0

        while (window_start + self.is_periods + self.oos_periods) <= n:
            is_end = window_start + self.is_periods
            oos_end = is_end + self.oos_periods

            is_df = df_feat.iloc[window_start:is_end]
            oos_df = df_feat.iloc[is_end:oos_end]

            # Instantiates strategy and runs IS backtest
            strat = strategy_class()
            is_signals = strat.generate_signals(is_df)
            tester_is = self.backtester_class()
            res_is = tester_is.run(is_df, is_signals)

            # OOS backtest with same strategy parameters
            oos_signals = strat.generate_signals(oos_df)
            tester_oos = self.backtester_class()
            res_oos = tester_oos.run(oos_df, oos_signals)

            is_ret = res_is["metrics"]["Total Return"]
            oos_ret = res_oos["metrics"]["Total Return"]

            is_returns.append(is_ret)
            oos_returns.append(oos_ret)

            if oos_ret > 0:
                profitable_oos_windows += 1
            total_windows += 1

            window_start += self.step_periods

        if total_windows == 0:
            return {"wfe": 0.0, "profitable_oos_ratio": 0.0, "total_windows": 0}

        avg_is_ret = np.mean(is_returns) if len(is_returns) > 0 else 1.0
        avg_oos_ret = np.mean(oos_returns) if len(oos_returns) > 0 else 0.0
        wfe = (avg_oos_ret / (avg_is_ret + 1e-9)) * 100.0  # Walk-Forward Efficiency (%)
        pct_profitable = profitable_oos_windows / total_windows

        return {
            "wfe_percent": float(wfe),
            "profitable_oos_ratio": float(pct_profitable),
            "total_windows": total_windows,
            "avg_is_return": float(avg_is_ret),
            "avg_oos_return": float(avg_oos_ret),
            "passes_wfe": bool(wfe >= 50.0 and pct_profitable >= 0.75),
        }
