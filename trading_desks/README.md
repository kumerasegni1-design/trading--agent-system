"""
30 Human Expert Trading Desks System
====================================
This module implements 30 unique human-expert trading desks backtested on Hugging Face
OANDA 1-minute historical data (Gold / XAUUSD and EUR/USD).

Key Constraints:
- Risk to Reward Ratio: Strictly 1:2 (Take Profit = 2 * Stop Loss distance)
- Trade Frequency: Strictly maximum 1 trade per week per trader desk
- Win Rate Target: Configured for institutional edge with realistic volatility stops

Directory Structure:
--------------------
trading_desks/
├── data/
│   ├── __init__.py
│   └── hf_downloader.py       # Hugging Face OANDA 1-min Parquet downloader & multi-timeframe resampler
├── desks/
│   ├── __init__.py
│   ├── base_desk.py           # BaseTradingDesk with weekly frequency filter and institutional constraints
│   ├── indicators.py          # Technical analysis indicators (SMA, EMA, RSI, ATR, BB, MACD, etc.)
│   └── all_desks.py           # Implementation of 30 unique expert desks with human trader personas
├── engine/
│   ├── __init__.py
│   └── backtest_engine.py     # DeskBacktestEngine & PortfolioManagerEngine (Sharpe, Drawdown, Equity Curves)
├── dashboard/
│   ├── __init__.py
│   ├── app.py                 # FastAPI app providing REST APIs
│   └── index.html             # Responsive institutional web dashboard with Chart.js equity curves
├── tests/
│   └── test_trading_desks.py  # Comprehensive test suite covering all modules
└── main.py                    # CLI entrypoint for downloading, backtesting, and dashboard serving

Quick Start:
------------
1. Run backtest across all 30 desks:
   python3 -m trading_desks.main --backtest --symbol GOLD

2. Launch interactive web dashboard:
   python3 -m trading_desks.main --dashboard --port 8000

3. Run full test suite:
   PYTHONPATH=. pytest trading_desks/tests/
"""
