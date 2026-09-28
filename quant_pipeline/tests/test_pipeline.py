"""
Unit and Integration Tests for Quantitative Strategy Pipeline.
"""

import os
import pytest
import pandas as pd
import numpy as np

from quant_pipeline.data import DukascopyDownloader, DataCleaner
from quant_pipeline.features import FeatureEngineer, split_data_60_20_20
from quant_pipeline.strategies import (
    MeanReversionStrategy,
    MomentumStrategy,
    BreakoutStrategy,
    SessionBasedStrategy,
    MultiTimeframeStrategy,
    StatArbStrategy,
    export_lean_algorithm,
)
from quant_pipeline.backtest import LocalBacktester
from quant_pipeline.robustness import MonteCarloEngine, OverfittingAnalyzer
from quant_pipeline.portfolio import PortfolioConstructor
from quant_pipeline.reporting import ReportGenerator


def test_data_acquisition_and_cleaner(tmp_path):
    downloader = DukascopyDownloader(data_dir=str(tmp_path))
    df = downloader.fetch_ohlcv("EUR/USD", timeframe="1h", use_synthetic=True)
    df_clean = DataCleaner.clean(df)

    assert not df_clean.empty
    assert "close" in df_clean.columns
    assert isinstance(df_clean.index, pd.DatetimeIndex)
    assert str(df_clean.index.tz) == "UTC"


def test_feature_engineering_and_splitting(tmp_path):
    downloader = DukascopyDownloader(data_dir=str(tmp_path))
    df = DataCleaner.clean(downloader.fetch_ohlcv("EUR/USD"))
    df_feat = FeatureEngineer.compute_all_features(df)

    assert "atr_14" in df_feat.columns
    assert "rsi_14" in df_feat.columns
    assert "macd" in df_feat.columns

    is_df, oos_df, wf_df = split_data_60_20_20(df_feat)
    assert len(is_df) > 0
    assert len(oos_df) > 0
    assert len(wf_df) > 0


def test_strategies_and_backtester(tmp_path):
    downloader = DukascopyDownloader(data_dir=str(tmp_path))
    df = DataCleaner.clean(downloader.fetch_ohlcv("EUR/USD"))
    df_feat = FeatureEngineer.compute_all_features(df)

    strategies = [
        MeanReversionStrategy(),
        MomentumStrategy(),
        BreakoutStrategy(),
        SessionBasedStrategy(),
        MultiTimeframeStrategy(),
        StatArbStrategy(),
    ]

    tester = LocalBacktester()

    for strat in strategies:
        signals = strat.generate_signals(df_feat)
        assert len(signals) == len(df_feat)

        res = tester.run(df_feat, signals)
        assert "metrics" in res
        assert "Sharpe Ratio" in res["metrics"]


def test_portfolio_and_reporting(tmp_path):
    downloader = DukascopyDownloader(data_dir=str(tmp_path))
    df = DataCleaner.clean(downloader.fetch_ohlcv("EUR/USD"))
    df_feat = FeatureEngineer.compute_all_features(df)

    s1_signals = MeanReversionStrategy().generate_signals(df_feat)
    s2_signals = MomentumStrategy().generate_signals(df_feat)

    tester = LocalBacktester()
    r1 = tester.run(df_feat, s1_signals)
    r2 = tester.run(df_feat, s2_signals)

    port = PortfolioConstructor().build_portfolio({"mr": r1, "mom": r2})
    assert "metrics" in port
    assert "Portfolio Sharpe Ratio" in port["metrics"]

    report_path = os.path.join(tmp_path, "report.html")
    generated_path = ReportGenerator.generate_html_report(port, {"mr": r1, "mom": r2}, {}, report_path)
    assert os.path.exists(generated_path)


def test_lean_export(tmp_path):
    out_file = os.path.join(tmp_path, "lean_alg.py")
    res_path = export_lean_algorithm("MeanReversion", "EUR/USD", out_file)
    assert os.path.exists(res_path)
