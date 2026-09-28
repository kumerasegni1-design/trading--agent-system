# Auto-generated strategy module for FX EMA Trend Following (FX)
import pandas as pd
import numpy as np

def run_strategy(df: pd.DataFrame):
    """
    Executes FX EMA Trend Following signal generation on provided OHLCV data.
    Returns signals (-1, 0, 1) and ATR series.
    """
    from backend.services.strategy_engine import DataEngine
    from backend.services.ten_strategy_suite import TenStrategySuite

    fitted_model = None

    return TenStrategySuite.strategy_1_fx_ema_trend(df, is_training=False, model=fitted_model)
