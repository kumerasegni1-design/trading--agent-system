import pytest
import pandas as pd
from services.backtesting_service import BacktestingService

@pytest.mark.asyncio
async def test_backtesting_delay():
    service = BacktestingService(engine="backtrader")
    df = pd.DataFrame({
        'open': [1.0, 1.1, 1.2],
        'high': [1.1, 1.2, 1.3],
        'low': [0.9, 1.0, 1.1],
        'close': [1.05, 1.15, 1.25]
    })

    # Test with delay
    results = await service.run_backtest("dummy_code", df, entry_delay=10)
    assert results["entry_delay"] == 10
    assert "backtrader" in results["engine"]

@pytest.mark.asyncio
async def test_backtesting_management():
    service = BacktestingService(engine="backtrader")
    df = pd.DataFrame({'open': [1.0], 'high': [1.1], 'low': [0.9], 'close': [1.05]})

    rules = [{"type": "move_sl_to_be", "trigger_price": 1.1}]
    results = await service.run_backtest("dummy_code", df, trade_management=rules)
    assert results["trade_management_applied"] == rules
