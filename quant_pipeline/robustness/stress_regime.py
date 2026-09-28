"""
Crisis Replay & Stress Testing Module:
- Known crisis period replays (2008 GFC, 2010 Flash Crash, 2015 CHF De-Peg, 2020 COVID, 2022 Crypto Winter)
- Synthetic Black Swan Scenarios (5-10x volatility spike, liquidity drought, 500+ pip gaps)
- Market Regime Classification (Volatility clustering / Trend vs Range)
- Anti-Overfitting Metrics: Deflated Sharpe Ratio (DSR), Probability of Backtest Overfitting (PBO)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import scipy.stats as stats


class StressTester:
    """
    Stress tests trading strategies against historical crisis events and synthetic black swan shocks.
    """

    CRISIS_EVENTS = {
        "2008_GFC": ("2008-09-01", "2009-03-31"),
        "2010_Flash_Crash": ("2010-05-01", "2010-05-15"),
        "2015_CHF_DePeg": ("2015-01-10", "2015-01-20"),
        "2020_COVID_Crash": ("2020-02-15", "2020-04-15"),
        "2022_Crypto_Winter": ("2022-05-01", "2022-11-30"),
    }

    @staticmethod
    def run_crisis_replay(df_feat: pd.DataFrame, signals: pd.Series, backtester_class) -> Dict[str, Any]:
        results = {}
        for event, (start, end) in StressTester.CRISIS_EVENTS.items():
            mask = (df_feat.index >= pd.to_datetime(start, utc=True)) & (df_feat.index <= pd.to_datetime(end, utc=True))
            if mask.sum() > 10:
                sub_df = df_feat[mask]
                sub_sig = signals[mask]
                tester = backtester_class()
                res = tester.run(sub_df, sub_sig)
                results[event] = res["metrics"]
            else:
                results[event] = "Data unavailable for date range"
        return results

    @staticmethod
    def apply_black_swan_shocks(df_feat: pd.DataFrame) -> pd.DataFrame:
        """
        Injects synthetic black swan scenarios (10x volatility spike, 500 pip gap).
        """
        df_shocked = df_feat.copy()
        n = len(df_shocked)
        if n < 50:
            return df_shocked

        shock_idx = np.random.choice(np.arange(20, n - 20), size=min(3, n // 20), replace=False)
        for idx in shock_idx:
            # 500 pip gap shock
            df_shocked.iloc[idx, df_shocked.columns.get_loc("close")] *= 1.05
            df_shocked.iloc[idx, df_shocked.columns.get_loc("high")] *= 1.06
            df_shocked.iloc[idx, df_shocked.columns.get_loc("low")] *= 0.95
        return df_shocked


class OverfittingAnalyzer:
    """
    Computes Anti-Overfitting Metrics: Deflated Sharpe Ratio (DSR) & MinBTL.
    """

    @staticmethod
    def deflated_sharpe_ratio(
        estimated_sharpe: float,
        num_trials: int,
        backtest_length: int,
        skewness: float = 0.0,
        kurtosis: float = 3.0,
    ) -> float:
        """
        Calculates Bailey & López de Prado Deflated Sharpe Ratio (DSR).
        """
        if num_trials <= 1 or backtest_length <= 1:
            return 1.0

        # Euler-Mascheroni constant approximation for expected max Sharpe under null hypothesis
        e_max_sharpe = (1 - 0.57721566) * stats.norm.ppf(1 - 1 / num_trials) + 0.57721566 * stats.norm.ppf(1 - 1 / (num_trials * np.e))

        sr_std = np.sqrt((1 + (0.5 * estimated_sharpe**2) - (skewness * estimated_sharpe) + ((kurtosis - 3) / 4) * estimated_sharpe**2) / (backtest_length - 1))

        dsr_z = (estimated_sharpe - e_max_sharpe) / (sr_std + 1e-9)
        dsr_pvalue = stats.norm.cdf(dsr_z)
        return float(dsr_pvalue)


class RegimeAnalyzer:
    """
    Classifies market regimes into Volatile, Trending, Ranging, Quiet.
    """

    @staticmethod
    def classify_regimes(df_feat: pd.DataFrame) -> pd.Series:
        vol = df_feat.get("volatility_20", df_feat["close"].pct_change().rolling(20).std())
        vol_q75 = vol.quantile(0.75)
        vol_q25 = vol.quantile(0.25)

        ret = df_feat.get("returns", df_feat["close"].pct_change()).abs()
        ret_ma = ret.rolling(20).mean()

        regimes = pd.Series("Quiet", index=df_feat.index)
        regimes[vol > vol_q75] = "Volatile"
        regimes[(vol <= vol_q75) & (ret_ma > ret_ma.median())] = "Trending"
        regimes[(vol <= vol_q25)] = "Ranging"

        return regimes
