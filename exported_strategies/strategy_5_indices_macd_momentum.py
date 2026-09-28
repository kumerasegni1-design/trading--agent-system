# Auto-generated strategy module for Indices MACD Momentum (Indices)
import pandas as pd
import numpy as np

def run_strategy(df: pd.DataFrame):
    """
    Executes Indices MACD Momentum signal generation on provided OHLCV data.
    Returns signals (-1, 0, 1) and ATR series.
    """
    from backend.services.strategy_engine import DataEngine
    from backend.services.ten_strategy_suite import TenStrategySuite

    fitted_model = None

    return TenStrategySuite.strategy_5_indices_macd_momentum(df, is_training=False, model=fitted_model)
