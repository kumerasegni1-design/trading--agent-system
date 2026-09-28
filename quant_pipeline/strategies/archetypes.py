"""
Concrete implementations of the 6 core quantitative strategy archetypes:
1. Mean Reversion
2. Momentum / Trend Following
3. Breakout with Confirmation
4. Session-Based (London Open / NY Kill Zone)
5. Multi-Timeframe Confluence
6. Statistical Arbitrage / Pairs Trading (or Spread Mean Reversion)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from quant_pipeline.strategies.base import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Bollinger Bands + RSI Mean Reversion Strategy.
    """

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {"rsi_overbought": 70, "rsi_oversold": 30, "zscore_entry": 2.0}
        if params:
            default_params.update(params)
        super().__init__("MeanReversion", default_params)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        bb_zscore = df.get("bb_zscore", (df["close"] - df["close"].rolling(20).mean()) / (df["close"].rolling(20).std() + 1e-9))
        rsi = df.get("rsi_14", pd.Series(50, index=df.index))

        long_cond = (bb_zscore < -self.params["zscore_entry"]) & (rsi < self.params["rsi_oversold"])
        short_cond = (bb_zscore > self.params["zscore_entry"]) & (rsi > self.params["rsi_overbought"])

        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals


class MomentumStrategy(BaseStrategy):
    """
    MACD + Moving Average Trend Following Strategy.
    """

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {"macd_threshold": 0.0}
        if params:
            default_params.update(params)
        super().__init__("Momentum", default_params)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        macd_hist = df.get("macd_hist", pd.Series(0, index=df.index))
        returns = df.get("returns", df["close"].pct_change())

        long_cond = (macd_hist > self.params["macd_threshold"]) & (macd_hist > macd_hist.shift(1)) & (returns > 0)
        short_cond = (macd_hist < -self.params["macd_threshold"]) & (macd_hist < macd_hist.shift(1)) & (returns < 0)

        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals


class BreakoutStrategy(BaseStrategy):
    """
    Donchian Channel / Highest High Breakout with Volume/ATR Confirmation.
    """

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {"lookback": 20, "vol_mult": 1.2}
        if params:
            default_params.update(params)
        super().__init__("Breakout", default_params)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        hh = df["high"].shift(1).rolling(self.params["lookback"]).max()
        ll = df["low"].shift(1).rolling(self.params["lookback"]).min()

        vol = df.get("volume", pd.Series(1.0, index=df.index))
        vol_ma = vol.rolling(20).mean()
        vol_confirm = vol > (vol_ma * self.params["vol_mult"])

        long_cond = (df["close"] > hh) & vol_confirm
        short_cond = (df["close"] < ll) & vol_confirm

        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals


class SessionBasedStrategy(BaseStrategy):
    """
    London Open / NY Kill Zone Session Strategy.
    """

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {"session": "london"}  # 'london' or 'ny'
        if params:
            default_params.update(params)
        super().__init__("SessionBased", default_params)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        if self.params["session"] == "london":
            active_session = df.get("session_london", pd.Series(0, index=df.index))
        else:
            active_session = df.get("session_ny", pd.Series(0, index=df.index))

        returns = df.get("returns", df["close"].pct_change())
        atr = df.get("atr_14", df["close"].rolling(14).std())

        long_cond = (active_session == 1) & (returns > 0) & (df["close"] > df["close"].shift(1) + atr * 0.2)
        short_cond = (active_session == 1) & (returns < 0) & (df["close"] < df["close"].shift(1) - atr * 0.2)

        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals


class MultiTimeframeStrategy(BaseStrategy):
    """
    Multi-Timeframe Trend Confluence Strategy.
    """

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {"short_window": 10, "long_window": 50}
        if params:
            default_params.update(params)
        super().__init__("MultiTimeframe", default_params)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        ma_short = df["close"].rolling(self.params["short_window"]).mean()
        ma_long = df["close"].rolling(self.params["long_window"]).mean()
        vwap = df.get("vwap_24", df["close"])

        long_cond = (df["close"] > ma_short) & (ma_short > ma_long) & (df["close"] > vwap)
        short_cond = (df["close"] < ma_short) & (ma_short < ma_long) & (df["close"] < vwap)

        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals


class StatArbStrategy(BaseStrategy):
    """
    Statistical Arbitrage / Rolling Z-Score Mean Reversion Strategy.
    """

    def __init__(self, params: Dict[str, Any] = None):
        default_params = {"entry_z": 2.0, "exit_z": 0.0}
        if params:
            default_params.update(params)
        super().__init__("StatArb", default_params)

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        ret_zscore = df.get("ret_zscore_20", pd.Series(0, index=df.index))

        long_cond = ret_zscore < -self.params["entry_z"]
        short_cond = ret_zscore > self.params["entry_z"]

        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals
