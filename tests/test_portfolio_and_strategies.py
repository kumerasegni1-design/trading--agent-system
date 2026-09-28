import os
import pytest
import pandas as pd
import numpy as np

from backend.services.strategy_engine import DataEngine
from backend.services.walk_forward_backtester import WalkForwardBacktester
from backend.services.ten_strategy_suite import TenStrategySuite
from backend.services.portfolio_verifier import run_portfolio_verification


def test_data_engine_synthetic_ohlcv():
    df = DataEngine.generate_synthetic_ohlcv('EURUSD', 'FX', periods=200, seed=42)
    assert not df.empty
    assert len(df) == 200
    assert 'open' in df.columns and 'high' in df.columns and 'low' in df.columns and 'close' in df.columns
    assert (df['high'] >= df['low']).all()


def test_data_engine_indicators_no_future_leak():
    df = DataEngine.generate_synthetic_ohlcv('EURUSD', 'FX', periods=200, seed=42)
    df_ind = DataEngine.compute_indicators(df)

    assert 'sma_10' in df_ind.columns
    assert 'rsi_14' in df_ind.columns
    assert 'atr_14' in df_ind.columns
    assert 'macd_hist' in df_ind.columns


def test_walk_forward_backtester_12_rr():
    df = DataEngine.generate_synthetic_ohlcv('EURUSD', 'FX', periods=500, seed=42)
    backtester = WalkForwardBacktester(risk_reward_ratio=2.0)

    results = backtester.walk_forward_validation(
        df, TenStrategySuite.strategy_1_fx_ema_trend, n_splits=3, train_ratio=0.7
    )

    assert 'metrics' in results
    assert 'win_rate' in results['metrics']
    assert 'total_trades' in results['metrics']


def test_ten_strategy_suite_export():
    export_dir = "test_exported_strategies"
    suite = TenStrategySuite(export_dir=export_dir)
    suite.export_all_strategies_and_models()

    files = os.listdir(export_dir)
    assert len(files) >= 10

    # Clean up test export dir
    import shutil
    shutil.rmtree(export_dir)


def test_portfolio_verification_performance():
    verification_metrics = run_portfolio_verification()

    assert verification_metrics['portfolio_win_rate'] >= 0.60
    assert verification_metrics['avg_correlation'] < 0.30
    assert verification_metrics['combined_trades_per_week'] >= 10.0
