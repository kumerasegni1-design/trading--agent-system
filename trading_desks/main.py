"""
CLI entrypoint to run trading desks backtest, download data, or launch dashboard.
Usage:
  python -m trading_desks.main --download --symbol GOLD --years 2020 2024
  python -m trading_desks.main --backtest --symbol GOLD
  python -m trading_desks.main --dashboard --port 8080
"""

import argparse
import uvicorn
from trading_desks.data.hf_downloader import HuggingFaceOandaDownloader
from trading_desks.desks import get_all_trading_desks
from trading_desks.engine import PortfolioManagerEngine
from trading_desks.dashboard.app import app

def main():
    parser = argparse.ArgumentParser(description="30 Human Expert Trading Desks System")
    parser.add_argument("--download", action="store_true", help="Download 5 years of 1-min data from Hugging Face")
    parser.add_argument("--symbol", type=str, default="GOLD", help="Symbol (GOLD or EURUSD)")
    parser.add_argument("--start-year", type=int, default=2020, help="Start year")
    parser.add_argument("--end-year", type=int, default=2024, help="End year")
    parser.add_argument("--backtest", action="store_true", help="Run backtest across all 30 desks")
    parser.add_argument("--dashboard", action="store_true", help="Launch interactive dashboard")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Dashboard host")
    parser.add_argument("--port", type=int, default=8000, help="Dashboard port")

    args = parser.parse_args()

    downloader = HuggingFaceOandaDownloader()

    if args.download:
        print(f"📥 Downloading {args.symbol} 1-min data from Hugging Face ({args.start_year}-{args.end_year})...")
        paths = downloader.download_date_range(args.symbol, args.start_year, args.end_year)
        print(f"✅ Downloaded {len(paths)} monthly Parquet files to {downloader.cache_dir}/{args.symbol}")

    if args.backtest:
        print(f"⚡ Loading {args.symbol} data and running all 30 expert desks...")
        df = downloader.load_data(args.symbol, args.start_year, args.end_year, max_files=1)
        df_15m = downloader.resample_data(df, "15m")
        desks = get_all_trading_desks()
        portfolio = PortfolioManagerEngine(desks)
        results = portfolio.run_all(df_15m)
        print(f"\n================ 30 DESKS PERFORMANCE SUMMARY ({args.symbol}) ================")
        print(f"{'Desk ID':<9} {'Trader Name':<20} {'Trades':<8} {'Wins':<6} {'Win Rate':<10} {'Return %':<10} {'Max DD %':<10}")
        print("-" * 75)
        for r in sorted(results, key=lambda x: x["metrics"]["total_return_pct"], reverse=True):
            m = r["metrics"]
            d = r["desk"]
            print(f"{d['desk_id']:<9} {d['trader_name']:<20} {m['total_trades']:<8} {m['wins']:<6} {m['win_rate_pct']:<10} {m['total_return_pct']:<10} {m['max_drawdown_pct']:<10}")
        print("=" * 75)

    if args.dashboard:
        print(f"🚀 Starting Trading Desks Dashboard at http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
