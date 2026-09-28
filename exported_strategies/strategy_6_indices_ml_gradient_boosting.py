# Auto-generated strategy module for Indices ML Gradient Boosting (Indices)
import pandas as pd
import numpy as np

def run_strategy(df: pd.DataFrame):
    """
    Executes Indices ML Gradient Boosting signal generation on provided OHLCV data.
    Returns signals (-1, 0, 1) and ATR series.
    """
    from backend.services.strategy_engine import DataEngine
    from backend.services.ten_strategy_suite import TenStrategySuite

    import os
    import joblib
    model_path = os.path.join(os.path.dirname(__file__), "strategy_6_indices_ml_gradient_boosting_model.joblib")
    fitted_model = joblib.load(model_path) if os.path.exists(model_path) else None

    return TenStrategySuite.strategy_6_indices_ml_gradient_boosting(df, is_training=False, model=fitted_model)
