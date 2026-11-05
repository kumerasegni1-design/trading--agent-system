"""
Definition of 30 Unique Human Trader Expert Trading Desks.
All desks adhere to:
- 1:2 Risk/Reward ratio
- Maximum 1 high-conviction trade per week
- Distinct institutional trader backgrounds, styles, and mathematical alpha models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Type
from trading_desks.desks.base_desk import BaseTradingDesk
from trading_desks.desks.indicators import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_atr,
    calculate_bollinger_bands, calculate_macd, calculate_stochastic,
    calculate_vwap, calculate_supertrend
)

# -------------------------------------------------------------
# 1. Asian Range Mean Reversion Scalper
# -------------------------------------------------------------
class AsianRangeReversionDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-01",
            trader_name="Elena Rostova",
            specialty="Asian Range Mean Reversion",
            style="Range Arbitrage",
            experience_years=14,
            preferred_timeframe="15m",
            philosophy="Asian consolidation ranges define clear liquidity boundaries. Fade false breakouts at session boundaries."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        sma20, upper, lower = calculate_bollinger_bands(df["close"], 20, 2.0)
        rsi = calculate_rsi(df["close"], 14)

        long_cond = (df["close"] < lower) & (rsi < 30)
        short_cond = (df["close"] > upper) & (rsi > 70)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 2. London Breakout Momentum Specialist
# -------------------------------------------------------------
class LondonBreakoutDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-02",
            trader_name="Marcus Vance",
            specialty="London Session Breakout",
            style="Momentum Breakout",
            experience_years=18,
            preferred_timeframe="15m",
            philosophy="London open establishes the true directional intent of European and Middle East capital flows."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        high_20 = df["high"].rolling(20).max()
        low_20 = df["low"].rolling(20).min()
        vol_ma = df["volume"].rolling(20).mean()

        long_cond = (df["close"] >= high_20.shift(1)) & (df["volume"] > vol_ma * 1.2)
        short_cond = (df["close"] <= low_20.shift(1)) & (df["volume"] > vol_ma * 1.2)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 3. NY Opening Drive Specialist
# -------------------------------------------------------------
class NYOpeningDriveDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-03",
            trader_name="Liam O'Connor",
            specialty="NY Opening Impulse",
            style="Impulse Trend",
            experience_years=12,
            preferred_timeframe="5m",
            philosophy="Ride the initial institutional order imbalance during the first 90 minutes of US market liquidity."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        ema9 = calculate_ema(df["close"], 9)
        ema21 = calculate_ema(df["close"], 21)
        ema50 = calculate_ema(df["close"], 50)
        atr = calculate_atr(df, 14)
        atr_ma = atr.rolling(20).mean()

        long_cond = (ema9 > ema21) & (ema21 > ema50) & (atr > atr_ma)
        short_cond = (ema9 < ema21) & (ema21 < ema50) & (atr > atr_ma)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 4. Multi-Timeframe EMA Trend Follower
# -------------------------------------------------------------
class MultiTimeframeEMADesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-04",
            trader_name="Sophia Chen",
            specialty="Multi-Timeframe Trend Following",
            style="Trend Alignment",
            experience_years=15,
            preferred_timeframe="1h",
            philosophy="Never fight higher timeframe trend structure. Enter only on pullback confluence with fast-to-slow exponential alignment."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        ema20 = calculate_ema(df["close"], 20)
        ema50 = calculate_ema(df["close"], 50)
        ema200 = calculate_ema(df["close"], 200)

        long_cond = (ema20 > ema50) & (ema50 > ema200) & (df["low"] <= ema20) & (df["close"] > ema20)
        short_cond = (ema20 < ema50) & (ema50 < ema200) & (df["high"] >= ema20) & (df["close"] < ema20)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 5. Donchian Channel Breakout Trend Rider
# -------------------------------------------------------------
class DonchianBreakoutDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-05",
            trader_name="Darius Thorne",
            specialty="Turtle Channel Breakout",
            style="Systematic Trend",
            experience_years=22,
            preferred_timeframe="1h",
            philosophy="Strict 20-period Donchian highs and lows capture explosive macroeconomic multi-week trends with zero discretionary bias."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        donchian_high = df["high"].rolling(20).max()
        donchian_low = df["low"].rolling(20).min()

        long_cond = (df["close"] > donchian_high.shift(1))
        short_cond = (df["close"] < donchian_low.shift(1))
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 6. Bollinger Band Squeeze & Expansion Specialist
# -------------------------------------------------------------
class BollingerSqueezeDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-06",
            trader_name="Amara Okafor",
            specialty="Volatility Squeeze Expansion",
            style="Volatility Expansion",
            experience_years=11,
            preferred_timeframe="15m",
            philosophy="Volatility is cyclical: extended low volatility compression inevitably releases in violent directional expansion."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        sma20, upper, lower = calculate_bollinger_bands(df["close"], 20, 2.0)
        bandwidth = (upper - lower) / (sma20 + 1e-10)
        bw_min = bandwidth.rolling(30).min()

        is_expanding = bandwidth > bw_min * 1.25
        long_cond = is_expanding & (df["close"] > upper)
        short_cond = is_expanding & (df["close"] < lower)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 7. Volatility ATR Breakout Desk
# -------------------------------------------------------------
class ATRVolatilityBreakoutDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-07",
            trader_name="Viktor Petrov",
            specialty="ATR Volatility Surges",
            style="Statistical Volatility",
            experience_years=16,
            preferred_timeframe="30m",
            philosophy="When real candle body size exceeds 2x the average true range, smart money is repositioning large size."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        atr = calculate_atr(df, 14)
        body = (df["close"] - df["open"]).abs()

        long_cond = ((df["close"] - df["open"]) > atr * 1.5) & (df["close"] > df["close"].rolling(20).mean())
        short_cond = ((df["open"] - df["close"]) > atr * 1.5) & (df["close"] < df["close"].rolling(20).mean())
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 8. VWAP Institutional Reversion Desk
# -------------------------------------------------------------
class VWAPReversionDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-08",
            trader_name="Chloe Laurent",
            specialty="Volume-Weighted Average Price Reversion",
            style="Institutional Mean Reversion",
            experience_years=13,
            preferred_timeframe="15m",
            philosophy="Institutions execute benchmarked to VWAP. Displacements of more than 2 standard deviations revert back towards fair value."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        vwap = calculate_vwap(df)
        std = (df["close"] - vwap).rolling(50).std()

        long_cond = df["close"] < (vwap - 2.0 * std)
        short_cond = df["close"] > (vwap + 2.0 * std)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 9. RSI Multi-Period Divergence Scalper
# -------------------------------------------------------------
class RSIDivergenceDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-09",
            trader_name="Kenji Takahashi",
            specialty="Oscillator Momentum Divergence",
            style="Counter-Trend Divergence",
            experience_years=20,
            preferred_timeframe="15m",
            philosophy="Price making new extremes while momentum oscillator forms lower highs reveals underlying exhaustion."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        rsi = calculate_rsi(df["close"], 14)

        # Bullish divergence: price lower, RSI higher
        price_lower = df["low"] < df["low"].shift(10)
        rsi_higher = rsi > rsi.shift(10)
        long_cond = price_lower & rsi_higher & (rsi < 35)

        # Bearish divergence: price higher, RSI lower
        price_higher = df["high"] > df["high"].shift(10)
        rsi_lower = rsi < rsi.shift(10)
        short_cond = price_higher & rsi_lower & (rsi > 65)

        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 10. Supertrend Dynamic Trailing Desk
# -------------------------------------------------------------
class SupertrendDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-10",
            trader_name="Isabella Morales",
            specialty="Adaptive Volatility Trend",
            style="Trend Following",
            experience_years=10,
            preferred_timeframe="30m",
            philosophy="ATR-based Supertrend eliminates noise and holds winners while cutting losses instantly on trend flips."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        st, direction = calculate_supertrend(df, period=10, multiplier=3.0)

        flip_up = (direction == 1) & (direction.shift(1) == -1)
        flip_down = (direction == -1) & (direction.shift(1) == 1)
        signals[flip_up] = 1
        signals[flip_down] = -1
        return signals

# -------------------------------------------------------------
# 11. Pivot Point Level-to-Level Desk
# -------------------------------------------------------------
class PivotPointDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-11",
            trader_name="Tariq Al-Mansoor",
            specialty="Floor Trader Daily Pivot Levels",
            style="Support & Resistance",
            experience_years=17,
            preferred_timeframe="15m",
            philosophy="Floor trader pivot levels are self-fulfilling prophecy magnet levels for institutional limit orders."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        pp = (df["high"].rolling(48).max() + df["low"].rolling(48).min() + df["close"]) / 3.0
        r1 = 2 * pp - df["low"].rolling(48).min()
        s1 = 2 * pp - df["high"].rolling(48).max()

        long_cond = (df["low"] <= s1) & (df["close"] > s1)
        short_cond = (df["high"] >= r1) & (df["close"] < r1)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 12. MACD Histogram Momentum Divergence Desk
# -------------------------------------------------------------
class MACDMomentumDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-12",
            trader_name="Hannah Schmidt",
            specialty="MACD Histogram Momentum Impulse",
            style="Momentum Crossover",
            experience_years=14,
            preferred_timeframe="1h",
            philosophy="The rate of change of moving average convergence/divergence signals explosive momentum turns before price breaks."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        macd, signal, hist = calculate_macd(df["close"], 12, 26, 9)

        long_cond = (hist > 0) & (hist.shift(1) <= 0) & (macd > 0)
        short_cond = (hist < 0) & (hist.shift(1) >= 0) & (macd < 0)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 13. Keltner Channel Trend Reversal Desk
# -------------------------------------------------------------
class KeltnerChannelDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-13",
            trader_name="Arthur Pendelton",
            specialty="Keltner Volatility Envelopes",
            style="Mean Reversion",
            experience_years=25,
            preferred_timeframe="30m",
            philosophy="ATR-based envelopes reflect true market breath and overextended extremes."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        ema20 = calculate_ema(df["close"], 20)
        atr = calculate_atr(df, 14)
        upper = ema20 + 2.0 * atr
        lower = ema20 - 2.0 * atr

        long_cond = (df["low"] < lower) & (df["close"] > lower)
        short_cond = (df["high"] > upper) & (df["close"] < upper)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 14. Heikin-Ashi Smoothed Trend Desk
# -------------------------------------------------------------
class HeikinAshiTrendDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-14",
            trader_name="Freja Lindqvist",
            specialty="Filtered Trend Continuity",
            style="Smooth Trend",
            experience_years=9,
            preferred_timeframe="15m",
            philosophy="Filter noise out of 1-minute bars using synthetic average pricing bars to ride uninterrupted trends."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        ha_close = (df["open"] + df["high"] + df["low"] + df["close"]) / 4.0
        ema10 = calculate_ema(ha_close, 10)
        ema30 = calculate_ema(ha_close, 30)

        cross_up = (ema10 > ema30) & (ema10.shift(1) <= ema30.shift(1))
        cross_down = (ema10 < ema30) & (ema10.shift(1) >= ema30.shift(1))
        signals[cross_up] = 1
        signals[cross_down] = -1
        return signals

# -------------------------------------------------------------
# 15. Stochastic Pullback Specialist
# -------------------------------------------------------------
class StochasticPullbackDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-15",
            trader_name="Gabriel Silva",
            specialty="Stochastic Oscillator Trend Pullback",
            style="Trend Pullback",
            experience_years=11,
            preferred_timeframe="15m",
            philosophy="Identify strong prevailing trend on EMA50, and time precise entries when Stochastic dips into oversold."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        k, d = calculate_stochastic(df, 14, 3)
        ema50 = calculate_ema(df["close"], 50)

        long_cond = (df["close"] > ema50) & (k < 20) & (k > d) & (k.shift(1) <= d.shift(1))
        short_cond = (df["close"] < ema50) & (k > 80) & (k < d) & (k.shift(1) >= d.shift(1))
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 16. Parabolic SAR Reversal Desk
# -------------------------------------------------------------
class ParabolicSARDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-16",
            trader_name="Priya Patel",
            specialty="Trailing Stop Reversal (SAR)",
            style="Volatility Stop & Reverse",
            experience_years=12,
            preferred_timeframe="30m",
            philosophy="Accelerating trailing stops lock in runaway profits and instantly flip bias when acceleration slows."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        # Simplified acceleration reversal proxy
        ema12 = calculate_ema(df["close"], 12)
        ema26 = calculate_ema(df["close"], 26)
        atr = calculate_atr(df, 14)

        long_cond = (df["close"] > ema12 + atr) & (ema12 > ema26)
        short_cond = (df["close"] < ema12 - atr) & (ema12 < ema26)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 17. Golden Cross Swing Desk
# -------------------------------------------------------------
class GoldenCrossDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-17",
            trader_name="Diego Ramirez",
            specialty="Golden Cross / Death Cross Swings",
            style="Macro Swing Trend",
            experience_years=20,
            preferred_timeframe="1h",
            philosophy="The 50/200 period crossover represents canonical institutional macro trend changes."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        ma50 = calculate_sma(df["close"], 50)
        ma200 = calculate_sma(df["close"], 200)

        cross_up = (ma50 > ma200) & (ma50.shift(1) <= ma200.shift(1))
        cross_down = (ma50 < ma200) & (ma50.shift(1) >= ma200.shift(1))
        signals[cross_up] = 1
        signals[cross_down] = -1
        return signals

# -------------------------------------------------------------
# 18. Volume Weighted Momentum Scalper
# -------------------------------------------------------------
class VolumeMomentumDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-18",
            trader_name="Zoe Kazantzis",
            specialty="Volume-Price Surge Scalping",
            style="Volume Scalp",
            experience_years=8,
            preferred_timeframe="5m",
            philosophy="Price moves without volume are fake; price breaks confirmed by heavy volume indicate aggressive liquidity takers."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        vol_ma = df["volume"].rolling(20).mean()
        price_change = df["close"].pct_change(5)

        long_cond = (price_change > 0.003) & (df["volume"] > vol_ma * 2.0)
        short_cond = (price_change < -0.003) & (df["volume"] > vol_ma * 2.0)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 19. Fractal Market Structure Desk
# -------------------------------------------------------------
class FractalStructureDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-19",
            trader_name="Lucas Meyer",
            specialty="Billi Williams Market Fractals & Break of Structure",
            style="Price Action Structure",
            experience_years=13,
            preferred_timeframe="15m",
            philosophy="Fractal swing highs and swing lows identify structural pivots and institutional stop-loss clusters."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        h = df["high"]
        l = df["low"]
        # 5-bar fractal
        bull_fractal = (h.shift(2) > h.shift(4)) & (h.shift(2) > h.shift(3)) & (h.shift(2) > h.shift(1)) & (h.shift(2) > h)
        bear_fractal = (l.shift(2) < l.shift(4)) & (l.shift(2) < l.shift(3)) & (l.shift(2) < l.shift(1)) & (l.shift(2) < l)

        signals[bull_fractal & (df["close"] > h.shift(2))] = 1
        signals[bear_fractal & (df["close"] < l.shift(2))] = -1
        return signals

# -------------------------------------------------------------
# 20. Hull Moving Average Zero-Lag Scalper
# -------------------------------------------------------------
class HullMADesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-20",
            trader_name="Nadir Boussouf",
            specialty="Hull Moving Average (HMA) Zero-Lag",
            style="Zero-Lag Trend",
            experience_years=16,
            preferred_timeframe="15m",
            philosophy="HMA eliminates lag while smoothing price action, allowing capture of exact inflection points."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        # HMA proxy: 2*WMA(n/2) - WMA(n)
        hma_fast = calculate_ema(df["close"], 9)
        hma_slow = calculate_ema(df["close"], 21)
        slope = hma_fast.diff(3)

        long_cond = (hma_fast > hma_slow) & (slope > 0) & (slope.shift(1) <= 0)
        short_cond = (hma_fast < hma_slow) & (slope < 0) & (slope.shift(1) >= 0)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 21. Commodity Channel Index (CCI) Extreme Desk
# -------------------------------------------------------------
class CCIExtremeDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-21",
            trader_name="Camilla Rossi",
            specialty="Commodity Channel Index Mean Reversion",
            style="Extreme Reversal",
            experience_years=12,
            preferred_timeframe="30m",
            philosophy="Gold and currency pairs oscillate predictably when CCI exceeds statistical extremes of +/- 200."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        tp = (df["high"] + df["low"] + df["close"]) / 3.0
        sma_tp = tp.rolling(20).mean()
        mad = (tp - sma_tp).abs().rolling(20).mean()
        cci = (tp - sma_tp) / (0.015 * mad + 1e-10)

        long_cond = (cci < -150) & (cci > cci.shift(1))
        short_cond = (cci > 150) & (cci < cci.shift(1))
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 22. Chaikin Money Flow Volume Breakout Desk
# -------------------------------------------------------------
class ChaikinMoneyFlowDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-22",
            trader_name="Oliver Brooks",
            specialty="Institutional Accumulation / Distribution",
            style="Volume Flow Trend",
            experience_years=19,
            preferred_timeframe="1h",
            philosophy="Track where smart money accumulates inventory through money flow multiplier before the public markup begins."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        hl = df["high"] - df["low"] + 1e-10
        mf_multiplier = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl
        mf_volume = mf_multiplier * df["volume"]
        cmf = mf_volume.rolling(20).sum() / (df["volume"].rolling(20).sum() + 1e-10)

        long_cond = (cmf > 0.15) & (df["close"] > df["close"].rolling(20).mean())
        short_cond = (cmf < -0.15) & (df["close"] < df["close"].rolling(20).mean())
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 23. Williams %R Range Exhaustion Desk
# -------------------------------------------------------------
class WilliamsRDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-23",
            trader_name="Anya Voronina",
            specialty="Williams %R Overbought/Oversold Reversals",
            style="Exhaustion Reversal",
            experience_years=10,
            preferred_timeframe="15m",
            philosophy="Detect market exhaustion at multi-session high/low boundaries using Larry Williams' bounded oscillator."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        highest_high = df["high"].rolling(14).max()
        lowest_low = df["low"].rolling(14).min()
        wr = -100 * ((highest_high - df["close"]) / (highest_high - lowest_low + 1e-10))

        long_cond = (wr < -80) & (wr > wr.shift(1))
        short_cond = (wr > -20) & (wr < wr.shift(1))
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 24. Rate of Change (ROC) Velocity Surge Desk
# -------------------------------------------------------------
class ROCVelocityDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-24",
            trader_name="Stefan Novak",
            specialty="Momentum Velocity Acceleration",
            style="Momentum Velocity",
            experience_years=15,
            preferred_timeframe="30m",
            philosophy="Pure speed and velocity: assets experiencing acceleration in price change sustain trends."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        roc = ((df["close"] - df["close"].shift(12)) / df["close"].shift(12)) * 100
        roc_ma = roc.rolling(10).mean()

        long_cond = (roc > 0.5) & (roc > roc_ma) & (df["close"] > df["close"].rolling(50).mean())
        short_cond = (roc < -0.5) & (roc < roc_ma) & (df["close"] < df["close"].rolling(50).mean())
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 25. Dual Supertrend Volatility Cascade Desk
# -------------------------------------------------------------
class DualSupertrendDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-25",
            trader_name="Maya Angelis",
            specialty="Dual Multi-Period Supertrend Confluence",
            style="Trend Confluence",
            experience_years=17,
            preferred_timeframe="15m",
            philosophy="Confluence of two distinct ATR multipliers (fast 10/2 and slow 20/4) filters 90% of false whipsaws."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        st_fast, dir_fast = calculate_supertrend(df, period=10, multiplier=2.0)
        st_slow, dir_slow = calculate_supertrend(df, period=20, multiplier=4.0)

        both_bull = (dir_fast == 1) & (dir_slow == 1) & ((dir_fast.shift(1) == -1) | (dir_slow.shift(1) == -1))
        both_bear = (dir_fast == -1) & (dir_slow == -1) & ((dir_fast.shift(1) == 1) | (dir_slow.shift(1) == 1))
        signals[both_bull] = 1
        signals[both_bear] = -1
        return signals

# -------------------------------------------------------------
# 26. Micro-Structure Mean Reversion Desk
# -------------------------------------------------------------
class MicroStructureReversionDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-26",
            trader_name="Ethan Hunt",
            specialty="Tick Micro-Structure Order Book Reversion",
            style="Micro Mean Reversion",
            experience_years=9,
            preferred_timeframe="5m",
            philosophy="Extreme 3-bar standard deviation stretches on 1-min / 5-min bars snap back quickly to local equilibrium."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        rolling_std = df["close"].rolling(20).std()
        rolling_mean = df["close"].rolling(20).mean()
        z_score = (df["close"] - rolling_mean) / (rolling_std + 1e-10)

        signals[z_score < -2.2] = 1
        signals[z_score > 2.2] = -1
        return signals

# -------------------------------------------------------------
# 27. Triple EMA (TRIX) Momentum Desk
# -------------------------------------------------------------
class TRIXMomentumDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-27",
            trader_name="Jin-Woo Park",
            specialty="Triple Smoothed Exponential Momentum (TRIX)",
            style="Filtered Momentum",
            experience_years=13,
            preferred_timeframe="30m",
            philosophy="Triply smoothing the moving average extracts the pure cyclical underlying trend free of cyclical noise."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        ema1 = calculate_ema(df["close"], 15)
        ema2 = calculate_ema(ema1, 15)
        ema3 = calculate_ema(ema2, 15)
        trix = ema3.pct_change() * 100
        trix_signal = trix.rolling(9).mean()

        long_cond = (trix > trix_signal) & (trix.shift(1) <= trix_signal.shift(1))
        short_cond = (trix < trix_signal) & (trix.shift(1) >= trix_signal.shift(1))
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 28. Fibonacci Pivot Retracement Desk
# -------------------------------------------------------------
class FibonacciRetracementDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-28",
            trader_name="Beatrice Dupont",
            specialty="Golden Ratio Fibonacci 61.8% Retracement",
            style="Harmonic Pullback",
            experience_years=21,
            preferred_timeframe="1h",
            philosophy="Major swing impulses retrace to the golden 61.8% ratio before resuming the master primary trend."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        swing_high = df["high"].rolling(50).max()
        swing_low = df["low"].rolling(50).min()
        fib_618 = swing_low + 0.618 * (swing_high - swing_low)

        long_cond = (df["low"] <= fib_618) & (df["close"] > fib_618) & (df["close"] > df["close"].rolling(200).mean())
        short_cond = (df["high"] >= fib_618) & (df["close"] < fib_618) & (df["close"] < df["close"].rolling(200).mean())
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 29. Exponential Volume Breakout Desk
# -------------------------------------------------------------
class ExponentialVolumeBreakoutDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-29",
            trader_name="Jackson Reed",
            specialty="Volume Climax Range Breakouts",
            style="Volume Climax Breakout",
            experience_years=11,
            preferred_timeframe="15m",
            philosophy="When volume spikes 300% over the 50-period average on a break of the 20-period high, follow the institutional footsteps."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        vol_avg = df["volume"].rolling(50).mean()
        high_20 = df["high"].rolling(20).max()
        low_20 = df["low"].rolling(20).min()

        long_cond = (df["close"] > high_20.shift(1)) & (df["volume"] > vol_avg * 2.5)
        short_cond = (df["close"] < low_20.shift(1)) & (df["volume"] > vol_avg * 2.5)
        signals[long_cond] = 1
        signals[short_cond] = -1
        return signals

# -------------------------------------------------------------
# 30. Risk-Parity Regime-Adaptive Dynamic Desk
# -------------------------------------------------------------
class RegimeAdaptiveDesk(BaseTradingDesk):
    def __init__(self):
        super().__init__(
            desk_id="DESK-30",
            trader_name="Samuel Vance",
            specialty="Volatility Regime-Adaptive Portfolio Desk",
            style="Macro Regime Switching",
            experience_years=24,
            preferred_timeframe="1h",
            philosophy="Dynamically switch between trend continuation in low-vol regimes and mean-reversion in high-vol regimes."
        )

    def generate_raw_signal(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index, dtype=int)
        atr = calculate_atr(df, 20)
        atr_median = atr.rolling(100).median()
        ema20 = calculate_ema(df["close"], 20)

        # Low volatility regime -> Trend following
        low_vol = atr < atr_median
        trend_long = low_vol & (df["close"] > ema20) & (df["close"].shift(1) <= ema20.shift(1))
        trend_short = low_vol & (df["close"] < ema20) & (df["close"].shift(1) >= ema20.shift(1))

        # High volatility regime -> Mean reversion
        sma20, upper, lower = calculate_bollinger_bands(df["close"], 20, 2.0)
        high_vol = atr >= atr_median
        rev_long = high_vol & (df["close"] < lower)
        rev_short = high_vol & (df["close"] > upper)

        signals[trend_long | rev_long] = 1
        signals[trend_short | rev_short] = -1
        return signals


# -------------------------------------------------------------
# Desk Registry
# -------------------------------------------------------------
ALL_DESK_CLASSES: List[Type[BaseTradingDesk]] = [
    AsianRangeReversionDesk,
    LondonBreakoutDesk,
    NYOpeningDriveDesk,
    MultiTimeframeEMADesk,
    DonchianBreakoutDesk,
    BollingerSqueezeDesk,
    ATRVolatilityBreakoutDesk,
    VWAPReversionDesk,
    RSIDivergenceDesk,
    SupertrendDesk,
    PivotPointDesk,
    MACDMomentumDesk,
    KeltnerChannelDesk,
    HeikinAshiTrendDesk,
    StochasticPullbackDesk,
    ParabolicSARDesk,
    GoldenCrossDesk,
    VolumeMomentumDesk,
    FractalStructureDesk,
    HullMADesk,
    CCIExtremeDesk,
    ChaikinMoneyFlowDesk,
    WilliamsRDesk,
    ROCVelocityDesk,
    DualSupertrendDesk,
    MicroStructureReversionDesk,
    TRIXMomentumDesk,
    FibonacciRetracementDesk,
    ExponentialVolumeBreakoutDesk,
    RegimeAdaptiveDesk
]

def get_all_trading_desks() -> List[BaseTradingDesk]:
    """Instantiate and return all 30 unique human trader expert desks."""
    return [desk_cls() for desk_cls in ALL_DESK_CLASSES]

def get_desk_by_id(desk_id: str) -> BaseTradingDesk:
    """Retrieve a specific trading desk by ID."""
    for desk_cls in ALL_DESK_CLASSES:
        desk = desk_cls()
        if desk.desk_id.upper() == desk_id.upper():
            return desk
    raise ValueError(f"Trading desk {desk_id} not found")
