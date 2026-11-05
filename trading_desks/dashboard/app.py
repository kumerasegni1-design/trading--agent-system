"""
FastAPI Application and Interactive Dashboard for 30 Trading Desks
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from trading_desks.desks import get_all_trading_desks, get_desk_by_id
from trading_desks.data.hf_downloader import HuggingFaceOandaDownloader
from trading_desks.engine import DeskBacktestEngine, PortfolioManagerEngine

app = FastAPI(
    title="30 Human Expert Trading Desks System",
    description="Multi-Desk Trading Terminal on Hugging Face OANDA 1-Min Gold & EUR/USD Data",
    version="1.0.0"
)

downloader = HuggingFaceOandaDownloader(cache_dir="./data/oanda")

# Cache loaded dataframes in memory for snappy responses
DATA_CACHE: Dict[str, Any] = {}

def get_cached_market_data(symbol: str = "GOLD", timeframe: str = "15m"):
    cache_key = f"{symbol.upper()}_{timeframe}"
    if cache_key not in DATA_CACHE:
        # Load 1-month sample or available cached data
        try:
            df = downloader.load_data(symbol, start_year=2024, end_year=2024, max_files=1)
        except Exception:
            # Download initial file if missing
            available = downloader.get_available_months(symbol)
            if available:
                downloader.download_month(symbol, available[-1])
                df = downloader.load_data(symbol, start_year=2024, end_year=2024, max_files=1)
            else:
                raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

        resampled = downloader.resample_data(df, timeframe)
        DATA_CACHE[cache_key] = resampled

    return DATA_CACHE[cache_key]

@app.get("/api/desks")
def list_trading_desks():
    """List all 30 human expert trading desks."""
    desks = get_all_trading_desks()
    return {"total": len(desks), "desks": [d.to_dict() for d in desks]}

@app.get("/api/desks/{desk_id}")
def get_desk_details(desk_id: str):
    """Get details for a specific trading desk."""
    try:
        desk = get_desk_by_id(desk_id)
        return desk.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/backtest/desk/{desk_id}")
def backtest_single_desk(
    desk_id: str,
    symbol: str = Query("GOLD", description="Asset: GOLD or EURUSD"),
    timeframe: str = Query("15m", description="Timeframe: 5m, 15m, 30m, 1h, 4h, 1d")
):
    """Run backtest on a specific desk with strict 1:2 RR and 1 trade/week limit."""
    try:
        desk = get_desk_by_id(desk_id)
        df = get_cached_market_data(symbol, timeframe)
        engine = DeskBacktestEngine(desk)
        results = engine.run(df)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest/all")
def backtest_all_desks(
    symbol: str = Query("GOLD", description="Asset: GOLD or EURUSD"),
    timeframe: str = Query("15m", description="Timeframe: 5m, 15m, 30m, 1h, 4h, 1d")
):
    """Run backtest across all 30 desks simultaneously and return ranked summary."""
    try:
        desks = get_all_trading_desks()
        df = get_cached_market_data(symbol, timeframe)
        portfolio = PortfolioManagerEngine(desks)
        results = portfolio.run_all(df)

        # Rank by total return %
        ranked = sorted(results, key=lambda x: x["metrics"]["total_return_pct"], reverse=True)
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "bars_tested": len(df),
            "desks_count": len(ranked),
            "results": ranked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def get_dashboard_html():
    """Serve the interactive institutional trading dashboard HTML."""
    html_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r") as f:
            return f.read()
    return "<h1>Trading Desk Dashboard - HTML file missing</h1>"
