"""
Technical, Statistical, Microstructure, and Session Feature Engineering Engine.
"""

import numpy as np
import pandas as pd


class FeatureEngineer:
    """
    Computes technical, statistical, market microstructure, and session features
    strictly using past data to prevent lookahead bias.
    """

    @staticmethod
    def compute_all_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df.get("volume", pd.Series(1.0, index=df.index))

        # --- Technical Indicators ---
        # 1. ATR (Average True Range)
        tr = np.maximum(
            high - low,
            np.maximum(
                (high - close.shift(1)).abs(),
                (low - close.shift(1)).abs()
            )
        )
        df["atr_14"] = tr.rolling(window=14).mean()

        # 2. RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df["rsi_14"] = 100 - (100 / (1 + rs))

        # 3. MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # 4. Bollinger Bands
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        df["bb_upper"] = bb_middle + (bb_std * 2)
        df["bb_lower"] = bb_middle - (bb_std * 2)
        df["bb_zscore"] = (close - bb_middle) / (bb_std + 1e-9)

        # 5. VWAP (Rolling 24h)
        pv = close * volume
        df["vwap_24"] = pv.rolling(window=24).sum() / (volume.rolling(window=24).sum() + 1e-9)

        # --- Market Structure (HH/HL/LH/LL) ---
        df["hh"] = high.rolling(window=10).max()
        df["ll"] = low.rolling(window=10).min()

        # --- Statistical Features ---
        # Z-Score of Returns
        returns = close.pct_change()
        df["returns"] = returns
        df["ret_zscore_20"] = (returns - returns.rolling(20).mean()) / (returns.rolling(20).std() + 1e-9)

        # Rolling Volatility (20-period)
        df["volatility_20"] = returns.rolling(20).std()

        # Hurst Exponent (Approximate rolling window implementation)
        def calc_hurst(ts):
            if len(ts) < 20 or ts.std() == 0:
                return 0.5
            lags = range(2, 10)
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0] * 2.0

        df["hurst_50"] = close.rolling(50).apply(calc_hurst, raw=True)

        # --- Microstructure & Session Features ---
        if isinstance(df.index, pd.DatetimeIndex):
            hour = df.index.hour
            df["session_tokyo"] = ((hour >= 0) & (hour < 8)).astype(int)
            df["session_london"] = ((hour >= 7) & (hour < 16)).astype(int)
            df["session_ny"] = ((hour >= 12) & (hour < 21)).astype(int)
            df["session_sydney"] = ((hour >= 21) | (hour < 6)).astype(int)

            df["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
            df["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)

        # Drop initial NaN values from rolling windows
        df.dropna(inplace=True)
        return df
