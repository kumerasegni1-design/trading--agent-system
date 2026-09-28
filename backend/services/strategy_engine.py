import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

class DataEngine:
    """
    Generates or fetches multi-asset historical OHLCV data across FX, Indices, and Crypto.
    Includes feature calculation with zero future-data leakage.
    """

    @staticmethod
    def generate_synthetic_ohlcv(
        symbol: str,
        asset_class: str,
        start_date: str = "2022-01-01",
        periods: int = 5000,
        freq: str = "1h",
        base_price: float = 1.0,
        volatility: float = 0.01,
        seed: Optional[int] = 42
    ) -> pd.DataFrame:
        if seed is not None:
            np.random.seed(seed)

        timestamps = pd.date_range(start=start_date, periods=periods, freq=freq)

        # Random walk drift with regime changes
        returns = np.random.normal(0, volatility, periods)
        # Add micro trends
        trend = np.sin(np.linspace(0, 10 * np.pi, periods)) * (volatility * 0.5)
        returns += trend

        price = base_price * np.exp(np.cumsum(returns))

        high = price * (1 + np.abs(np.random.normal(0, volatility * 0.5, periods)))
        low = price * (1 - np.abs(np.random.normal(0, volatility * 0.5, periods)))

        # Ensure High >= max(Open, Close) and Low <= min(Open, Close)
        open_price = np.roll(price, 1)
        open_price[0] = price[0]
        close = price

        high = np.maximum(high, np.maximum(open_price, close))
        low = np.minimum(low, np.minimum(open_price, close))
        volume = np.random.lognormal(mean=10, sigma=1, size=periods)

        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'symbol': symbol,
            'asset_class': asset_class
        })
        df.set_index('timestamp', inplace=True)
        return df

    @staticmethod
    def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes technical indicators lazily or eagerly.
        All indicators are derived STRICTLY from past bars (no shift(-1) or future lookahead).
        """
        data = df.copy()
        close = data['close']
        high = data['high']
        low = data['low']

        # Simple & Exponential Moving Averages
        data['sma_10'] = close.rolling(window=10).mean()
        data['sma_20'] = close.rolling(window=20).mean()
        data['sma_50'] = close.rolling(window=50).mean()
        data['ema_12'] = close.ewm(span=12, adjust=False).mean()
        data['ema_26'] = close.ewm(span=26, adjust=False).mean()

        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_hist'] = data['macd'] - data['macd_signal']

        # RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        data['rsi_14'] = 100 - (100 / (1 + rs))

        # ATR (14)
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        data['atr_14'] = tr.rolling(window=14).mean()

        # Bollinger Bands (20, 2)
        bb_std = close.rolling(window=20).std()
        data['bb_upper'] = data['sma_20'] + (bb_std * 2)
        data['bb_lower'] = data['sma_20'] - (bb_std * 2)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / (data['sma_20'] + 1e-10)

        # Momentum & Volatility Features
        data['mom_5'] = close.pct_change(5)
        data['mom_10'] = close.pct_change(10)
        data['volatility_20'] = close.pct_change().rolling(20).std()

        # High/Low Breakouts (20 bar lookback)
        data['hh_20'] = high.shift(1).rolling(20).max()
        data['ll_20'] = low.shift(1).rolling(20).min()

        return data
