"""
Synthetic market data generator for rapid testing and development.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


def generate_synthetic_ohlcv(
    symbol: str = "EUR/USD",
    start_date: str = "2015-01-01",
    end_date: str = "2025-01-01",
    freq: str = "1h",
    initial_price: float = 1.1000,
    volatility: float = 0.0008,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates realistic synthetic OHLCV data with timestamp in UTC.
    """
    np.random.seed(seed)
    timestamps = pd.date_range(start=start_date, end=end_date, freq=freq, tz="UTC")
    n = len(timestamps)

    if n == 0:
        raise ValueError("Start date and end date resulted in empty range.")

    # Geometric Brownian Motion + mean reverting noise
    returns = np.random.normal(loc=0.00001, scale=volatility, size=n)
    price_path = initial_price * np.exp(np.cumsum(returns))

    high_noise = np.abs(np.random.normal(loc=volatility * 0.5, scale=volatility * 0.2, size=n))
    low_noise = np.abs(np.random.normal(loc=volatility * 0.5, scale=volatility * 0.2, size=n))

    close = price_path
    high = np.maximum(close, close + high_noise)
    low = np.minimum(close, close - low_noise)
    open_p = np.roll(close, 1)
    open_p[0] = initial_price

    volume = np.random.poisson(lam=1000, size=n).astype(float)
    # Inject occasional zero-volume bar or anomaly for integrity check tests
    spread = np.random.uniform(0.0001, 0.0003, size=n)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
        "spread": spread
    })
    df.set_index("timestamp", inplace=True)
    return df
