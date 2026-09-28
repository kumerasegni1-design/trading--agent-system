# Auto-generated strategy module for Statistical Arbitrage Spread Reversion (Indices)
import pandas as pd
import numpy as np

def run_strategy(df: pd.DataFrame):
    """
    Executes Statistical Arbitrage Spread Reversion signal generation on provided OHLCV data.
    Returns signals (-1, 0, 1) and ATR series.
    """
    from backend.services.strategy_engine import DataEngine
    from backend.services.ten_strategy_suite import TenStrategySuite

    fitted_model = None

    return TenStrategySuite.strategy_8_stat_arb_spread(df, is_training=False, model=fitted_model)
