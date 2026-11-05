"""
Common Indicators and Calculation Utilities for Trading Desks
"""
import pandas as pd
import numpy as np

def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['high']
    low = df['low']
    close = df['close']
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def calculate_bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0):
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return sma, upper, lower

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    k = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
    d = k.rolling(window=d_period).mean()
    return k, d

def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df['high'] + df['low'] + df['close']) / 3.0
    vol = df['volume'] + 1e-10
    # Group by calendar date for intraday VWAP or rolling window
    cum_vol_price = (typical_price * vol).cumsum()
    cum_vol = vol.cumsum()
    return cum_vol_price / cum_vol

def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    atr = calculate_atr(df, period)
    hl2 = (df['high'] + df['low']) / 2.0
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    close = df['close'].values
    ub = upperband.values
    lb = lowerband.values

    curr_in_uptrend = True
    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = lb[i]
            direction.iloc[i] = 1
            continue

        if close[i] > ub[i-1]:
            curr_in_uptrend = True
        elif close[i] < lb[i-1]:
            curr_in_uptrend = False

        if curr_in_uptrend:
            supertrend.iloc[i] = max(lb[i], supertrend.iloc[i-1]) if supertrend.iloc[i-1] != 0 else lb[i]
            direction.iloc[i] = 1
        else:
            supertrend.iloc[i] = min(ub[i], supertrend.iloc[i-1]) if supertrend.iloc[i-1] != 0 else ub[i]
            direction.iloc[i] = -1

    return supertrend, direction
