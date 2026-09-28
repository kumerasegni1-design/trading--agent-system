"""
Complete CLI Entrypoint for Quantitative Strategy Development Pipeline.
"""

import argparse
import sys
import logging
import os
import pandas as pd

from quant_pipeline.data import DukascopyDownloader, DataCleaner
from quant_pipeline.features import FeatureEngineer, FeatureSelector, split_data_60_20_20
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
from quant_pipeline.robustness import (
    MonteCarloEngine,
    WalkForwardAnalyzer,
    OverfittingAnalyzer,
    StressTester,
    RegimeAnalyzer,
)
from quant_pipeline.portfolio import PortfolioConstructor
from quant_pipeline.reporting import ReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("quant_pipeline.cli")

STRATEGY_MAP = {
    "mean_reversion": MeanReversionStrategy,
    "momentum": MomentumStrategy,
    "breakout": BreakoutStrategy,
    "session": SessionBasedStrategy,
    "multitimeframe": MultiTimeframeStrategy,
    "statarb": StatArbStrategy,
}


def main():
    parser = argparse.ArgumentParser(
        description="Institutional-Grade Quantitative Strategy Development Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Data subcommand
    data_parser = subparsers.add_parser("data", help="Acquire and inspect data")
    data_parser.add_argument("--symbol", type=str, default="EUR/USD", help="Asset symbol")
    data_parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe (e.g. 1h, 1d)")
    data_parser.add_argument("--synthetic", action="store_true", help="Generate synthetic data for testing")
    data_parser.add_argument("--data-dir", type=str, default="data_store", help="Data store directory")

    # Features subcommand
    features_parser = subparsers.add_parser("features", help="Preprocess and engineer features")
    features_parser.add_argument("--symbol", type=str, default="EUR/USD", help="Asset symbol")
    features_parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")

    # Pipeline Run All subcommand
    run_parser = subparsers.add_parser("run", help="Run end-to-end strategy pipeline")
    run_parser.add_argument("--symbol", type=str, default="EUR/USD", help="Asset symbol")
    run_parser.add_argument("--strategy", type=str, default="mean_reversion", choices=list(STRATEGY_MAP.keys()), help="Strategy archetype")
    run_parser.add_argument("--export-lean", action="store_true", help="Export LEAN algorithm code")
    run_parser.add_argument("--output-report", type=str, default="report.html", help="HTML report output path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "data":
        downloader = DukascopyDownloader(data_dir=args.data_dir)
        df = downloader.fetch_ohlcv(symbol=args.symbol, timeframe=args.timeframe, use_synthetic=args.synthetic)
        df_clean = DataCleaner.clean(df)
        logger.info(f"Successfully fetched and cleaned dataset for {args.symbol}. Shape: {df_clean.shape}")
        print(df_clean.head())

    elif args.command == "features":
        downloader = DukascopyDownloader()
        df = DataCleaner.clean(downloader.fetch_ohlcv(symbol=args.symbol, timeframe=args.timeframe))
        df_feat = FeatureEngineer.compute_all_features(df)

        # Feature Selection & Collinearity Filtering
        numeric_cols = df_feat.select_dtypes(include=["float64", "int64"]).columns
        selected_cols = FeatureSelector.filter_collinear(df_feat[numeric_cols], threshold=0.85)
        logger.info(f"Engineered {df_feat.shape[1]} features. {len(selected_cols)} features selected after collinearity filtering.")
        print(df_feat[selected_cols].head())

    elif args.command == "run":
        logger.info(f"Executing End-to-End Pipeline for {args.symbol} using Strategy: {args.strategy}")

        # 1. Fetch & Clean Data
        downloader = DukascopyDownloader()
        df = DataCleaner.clean(downloader.fetch_ohlcv(symbol=args.symbol, timeframe="1h"))

        # 2. Engineer Features & Filter Collinearity
        df_feat = FeatureEngineer.compute_all_features(df)
        numeric_cols = [col for col in df_feat.columns if col not in ["open", "high", "low", "close", "volume"]]
        filtered_cols = FeatureSelector.filter_collinear(df_feat[numeric_cols], threshold=0.85)
        df_feat = df_feat[["open", "high", "low", "close", "volume"] + filtered_cols]

        is_df, oos_df, wf_df = split_data_60_20_20(df_feat)

        # 3. Instantiate & Backtest Strategy
        strat_cls = STRATEGY_MAP[args.strategy]
        strat = strat_cls()
        signals = strat.generate_signals(df_feat)

        tester = LocalBacktester()
        res = tester.run(df_feat, signals)
        logger.info(f"Backtest Metrics: {res['metrics']}")

        # 4. LEAN Export
        if args.export_lean:
            lean_path = export_lean_algorithm(args.strategy, args.symbol, f"exported_strategies/{args.strategy}_QC.py")
            logger.info(f"Exported QuantConnect LEAN algorithm to: {lean_path}")

        # 5. Robustness Analysis (Monte Carlo, Walk-Forward, Crisis Replay, Regime Classification)
        logger.info("Running Monte Carlo Simulations (100 iterations)...")
        mc_res = MonteCarloEngine.resample_trades(res["trades_df"], num_simulations=100)

        logger.info("Running Walk-Forward Optimization Analysis...")
        wfa = WalkForwardAnalyzer(LocalBacktester, is_periods=24*180, oos_periods=24*90, step_periods=24*45)
        wf_res = wfa.run(df_feat, strat_cls)

        logger.info("Running Crisis Replay & Regime Classification...")
        crisis_res = StressTester.run_crisis_replay(df_feat, signals, LocalBacktester)
        regimes = RegimeAnalyzer.classify_regimes(df_feat)
        dsr_pval = OverfittingAnalyzer.deflated_sharpe_ratio(res["metrics"]["Sharpe Ratio"], num_trials=10, backtest_length=len(df_feat))

        robustness_summary = {
            "mc_ruin_prob": mc_res["ruin_probability"],
            "wfe_percent": wf_res["wfe_percent"],
            "dsr_pvalue": dsr_pval,
            "regimes_detected": regimes.value_counts().to_dict(),
        }

        # 6. Portfolio Construction & Report Generation
        portfolio_res = PortfolioConstructor().build_portfolio({args.strategy: res})
        report_path = ReportGenerator.generate_html_report(portfolio_res, {args.strategy: res}, robustness_summary, args.output_report)
        logger.info(f"Interactive HTML Report generated at: {report_path}")

        decision = ReportGenerator.generate_go_no_go_checklist(portfolio_res["metrics"], robustness_summary)
        print("\n" + "="*50)
        print("DEPLOYMENT READINESS CHECK:")
        print(f"Decision: {decision['decision']}")
        print(f"Checklist: {decision['checklist']}")
        print("="*50 + "\n")


if __name__ == "__main__":
    main()
