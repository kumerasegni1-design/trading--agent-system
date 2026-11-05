"""
Comprehensive Unit & Integration Test Suite for 30 Trading Desks System
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from trading_desks.data.hf_downloader import HuggingFaceOandaDownloader, HF_DATASET_MAP
from trading_desks.desks import get_all_trading_desks, get_desk_by_id, ALL_DESK_CLASSES
from trading_desks.desks.indicators import (
    calculate_sma, calculate_ema, calculate_rsi, calculate_atr,
    calculate_bollinger_bands, calculate_macd, calculate_stochastic,
    calculate_vwap, calculate_supertrend
)
from trading_desks.engine import DeskBacktestEngine, PortfolioManagerEngine
from fastapi.testclient import TestClient
from trading_desks.dashboard.app import app

@pytest.fixture
def sample_ohlcv_data():
    """Generate synthetic 500-bar OHLCV dataframe spanning multiple weeks."""
    np.random.seed(42)
    n = 600
    start_time = datetime(2024, 1, 1, 0, 0)
    timestamps = [start_time + timedelta(hours=i) for i in range(n)]

    price = 2000.0
    prices = [price]
    for _ in range(n - 1):
        price += np.random.normal(0.1, 2.0)
        prices.append(price)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "open": prices,
        "high": [p + abs(np.random.normal(1.0, 0.5)) for p in prices],
        "low": [p - abs(np.random.normal(1.0, 0.5)) for p in prices],
        "close": [p + np.random.normal(0, 0.5) for p in prices],
        "volume": np.random.randint(100, 5000, size=n)
    })
    return df

# 1. Downloader Tests
def test_dataset_map():
    assert "GOLD" in HF_DATASET_MAP
    assert "XAUUSD" in HF_DATASET_MAP
    assert "EURUSD" in HF_DATASET_MAP

def test_downloader_initialization(tmp_path):
    downloader = HuggingFaceOandaDownloader(cache_dir=str(tmp_path))
    assert downloader.cache_dir == str(tmp_path)

def test_downloader_resample(sample_ohlcv_data):
    resampled = HuggingFaceOandaDownloader.resample_data(sample_ohlcv_data, "4h")
    assert len(resampled) < len(sample_ohlcv_data)
    assert set(["open", "high", "low", "close", "volume", "timestamp"]).issubset(resampled.columns)

# 2. Indicators Tests
def test_indicators_calculation(sample_ohlcv_data):
    sma = calculate_sma(sample_ohlcv_data["close"], 20)
    assert len(sma) == len(sample_ohlcv_data)

    ema = calculate_ema(sample_ohlcv_data["close"], 20)
    assert len(ema) == len(sample_ohlcv_data)

    rsi = calculate_rsi(sample_ohlcv_data["close"], 14)
    assert (rsi.dropna() >= 0).all() and (rsi.dropna() <= 100).all()

    atr = calculate_atr(sample_ohlcv_data, 14)
    assert (atr.dropna() > 0).all()

    mid, upper, lower = calculate_bollinger_bands(sample_ohlcv_data["close"], 20, 2.0)
    assert (upper.dropna() >= lower.dropna()).all()

    st, direction = calculate_supertrend(sample_ohlcv_data, 10, 3.0)
    assert set(direction.unique()).issubset({1, -1})

# 3. All 30 Desks Validation
def test_30_desks_instantiation():
    desks = get_all_trading_desks()
    assert len(desks) == 30
    assert len(ALL_DESK_CLASSES) == 30

    ids = [d.desk_id for d in desks]
    assert len(set(ids)) == 30, "All desk IDs must be unique"

    names = [d.trader_name for d in desks]
    assert len(set(names)) == 30, "All trader names must be unique"

def test_each_desk_properties():
    desks = get_all_trading_desks()
    for desk in desks:
        assert desk.desk_id.startswith("DESK-")
        assert len(desk.trader_name) > 3
        assert len(desk.specialty) > 3
        assert len(desk.philosophy) > 10
        assert desk.risk_reward_ratio == 2.0  # 1:2 RR
        assert desk.max_trades_per_week == 1  # 1 trade / week

def test_desk_signal_generation_and_weekly_filter(sample_ohlcv_data):
    desks = get_all_trading_desks()
    for desk in desks:
        raw_signals = desk.generate_raw_signal(sample_ohlcv_data)
        assert len(raw_signals) == len(sample_ohlcv_data)
        assert set(raw_signals.unique()).issubset({-1, 0, 1})

        weekly_signals = desk.get_trade_signals(sample_ohlcv_data)
        assert len(weekly_signals) == len(sample_ohlcv_data)

        # Check maximum 1 trade per week
        ts = pd.to_datetime(sample_ohlcv_data["timestamp"])
        week_ids = ts.dt.isocalendar().year.astype(str) + "-W" + ts.dt.isocalendar().week.astype(str)
        signal_weeks = week_ids[weekly_signals != 0].tolist()
        assert len(signal_weeks) == len(set(signal_weeks)), f"{desk.desk_id} violated 1 trade/week rule!"

# 4. Backtest Engine Tests
def test_backtest_execution(sample_ohlcv_data):
    desk = get_desk_by_id("DESK-01")
    engine = DeskBacktestEngine(desk, initial_capital=100_000.0)
    result = engine.run(sample_ohlcv_data)

    assert "desk" in result
    assert "metrics" in result
    assert "trades" in result
    assert "equity_curve" in result

    metrics = result["metrics"]
    assert metrics["initial_capital"] == 100_000.0
    assert "win_rate_pct" in metrics
    assert "profit_factor" in metrics
    assert "sharpe_ratio" in metrics

    # Verify 1:2 RR in trades
    for trade in result["trades"]:
        entry = trade["entry_price"]
        sl = trade["sl_price"]
        tp = trade["tp_price"]
        sl_dist = abs(entry - sl)
        tp_dist = abs(tp - entry)
        assert pytest.approx(tp_dist / sl_dist, rel=1e-2) == 2.0

def test_portfolio_manager(sample_ohlcv_data):
    desks = get_all_trading_desks()[:5]  # Test portfolio with 5 desks
    portfolio = PortfolioManagerEngine(desks)
    results = portfolio.run_all(sample_ohlcv_data)

    assert len(results) == 5
    for res in results:
        assert res["desk"]["risk_reward_ratio"] == "1:2.0"

# 5. REST API & Dashboard Tests
def test_dashboard_api():
    client = TestClient(app)

    # Test GET /api/desks
    res = client.get("/api/desks")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 30
    assert len(data["desks"]) == 30

    # Test GET /api/desks/DESK-01
    res = client.get("/api/desks/DESK-01")
    assert res.status_code == 200
    assert res.json()["trader_name"] == "Elena Rostova"

    # Test GET /
    res = client.get("/")
    assert res.status_code == 200
    assert "30 HUMAN EXPERT TRADING DESKS" in res.text
