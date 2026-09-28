import numpy as np
import pandas as pd
from typing import Dict, List, Any
from backend.services.strategy_engine import DataEngine
from backend.services.walk_forward_backtester import WalkForwardBacktester
from backend.services.ten_strategy_suite import TenStrategySuite

def run_portfolio_verification():
    print("🚀 Running Portfolio Verification across 10 Uncorrelated Strategies...")

    # Generate multi-asset historical datasets
    assets_datasets = {
        'EURUSD': DataEngine.generate_synthetic_ohlcv('EURUSD', 'FX', periods=6000, volatility=0.005, seed=101),
        'GBPUSD': DataEngine.generate_synthetic_ohlcv('GBPUSD', 'FX', periods=6000, volatility=0.006, seed=102),
        'BTCUSD': DataEngine.generate_synthetic_ohlcv('BTCUSD', 'Crypto', periods=6000, volatility=0.02, seed=103),
        'ETHUSD': DataEngine.generate_synthetic_ohlcv('ETHUSD', 'Crypto', periods=6000, volatility=0.025, seed=104),
        'SPX500': DataEngine.generate_synthetic_ohlcv('SPX500', 'Indices', periods=6000, volatility=0.01, seed=105),
        'NAS100': DataEngine.generate_synthetic_ohlcv('NAS100', 'Indices', periods=6000, volatility=0.012, seed=106),
        'AUDUSD': DataEngine.generate_synthetic_ohlcv('AUDUSD', 'FX', periods=6000, volatility=0.006, seed=107),
        'US2000': DataEngine.generate_synthetic_ohlcv('US2000', 'Indices', periods=6000, volatility=0.014, seed=108),
        'SOLUSD': DataEngine.generate_synthetic_ohlcv('SOLUSD', 'Crypto', periods=6000, volatility=0.03, seed=109),
        'USDCAD': DataEngine.generate_synthetic_ohlcv('USDCAD', 'FX', periods=6000, volatility=0.005, seed=110),
    }

    strategies = [
        ('Strategy 1 (FX EMA Trend)', TenStrategySuite.strategy_1_fx_ema_trend, assets_datasets['EURUSD']),
        ('Strategy 2 (FX BB Mean Rev)', TenStrategySuite.strategy_2_fx_bb_mean_reversion, assets_datasets['GBPUSD']),
        ('Strategy 3 (Crypto Vol Breakout)', TenStrategySuite.strategy_3_crypto_volatility_breakout, assets_datasets['BTCUSD']),
        ('Strategy 4 (Crypto ML RF)', TenStrategySuite.strategy_4_crypto_ml_random_forest, assets_datasets['ETHUSD']),
        ('Strategy 5 (Indices MACD Mom)', TenStrategySuite.strategy_5_indices_macd_momentum, assets_datasets['SPX500']),
        ('Strategy 6 (Indices ML GB)', TenStrategySuite.strategy_6_indices_ml_gradient_boosting, assets_datasets['NAS100']),
        ('Strategy 7 (Multi-TF Trend)', TenStrategySuite.strategy_7_multi_timeframe_trend, assets_datasets['AUDUSD']),
        ('Strategy 8 (Stat Arb Spread)', TenStrategySuite.strategy_8_stat_arb_spread, assets_datasets['US2000']),
        ('Strategy 9 (ATR Keltner)', TenStrategySuite.strategy_9_atr_keltner_breakout, assets_datasets['SOLUSD']),
        ('Strategy 10 (ML Log Divergence)', TenStrategySuite.strategy_10_ml_logistic_divergence, assets_datasets['USDCAD']),
    ]

    backtester = WalkForwardBacktester(risk_reward_ratio=2.0)
    strategy_results = []
    equity_curves = {}

    total_combined_trades = 0

    for name, strat_func, df_data in strategies:
        # Run Walk-Forward Validation
        res = backtester.walk_forward_validation(df_data, strat_func, n_splits=5, train_ratio=0.7)
        metrics = res['metrics']
        trades = res['trades']

        # Build equity curve for correlation
        if trades:
            trades_df = pd.DataFrame(trades).set_index('exit_time')
            eq = (1 + trades_df['net_return']).cumprod()
            eq = eq.reindex(df_data.index, method='ffill').fillna(1.0)
        else:
            eq = pd.Series(1.0, index=df_data.index)

        equity_curves[name] = eq
        total_combined_trades += metrics['total_trades']

        strategy_results.append({
            'name': name,
            'trades': metrics['total_trades'],
            'win_rate': metrics['win_rate'],
            'profit_factor': metrics['profit_factor'],
            'trades_per_week': metrics['avg_trades_per_week']
        })

    # Portfolio correlation matrix
    eq_df = pd.DataFrame(equity_curves).pct_change().dropna()
    corr_matrix = eq_df.corr().copy()

    # Calculate average off-diagonal correlation
    corr_vals = corr_matrix.to_numpy(copy=True)
    np.fill_diagonal(corr_vals, np.nan)
    avg_corr = np.nanmean(corr_vals)

    # Time span in weeks
    sample_df = list(assets_datasets.values())[0]
    total_weeks = (sample_df.index[-1] - sample_df.index[0]).total_seconds() / (86400.0 * 7)
    combined_trades_per_week = total_combined_trades / total_weeks

    # Overall portfolio win rate
    all_wins = sum(s['trades'] * s['win_rate'] for s in strategy_results)
    portfolio_win_rate = all_wins / total_combined_trades if total_combined_trades > 0 else 0.0

    print("\n--- Portfolio Verification Summary ---")
    print(f"Total Combined OOS Trades: {total_combined_trades}")
    print(f"Combined Portfolio Trades / Week: {combined_trades_per_week:.2f} trades/week")
    print(f"Weighted Portfolio Win Rate: {portfolio_win_rate * 100:.2f}% (Target: >= 60%)")
    print(f"Risk-to-Reward Ratio: 1:2 RR (Fixed)")
    print(f"Average Pairwise Strategy Return Correlation: {avg_corr:.3f} (Uncorrelated Target: < 0.30)")

    print("\n--- Individual Strategy Metrics ---")
    for s in strategy_results:
        print(f"{s['name']}: Win Rate = {s['win_rate']*100:.1f}%, Trades = {s['trades']}, Trades/Wk = {s['trades_per_week']}")

    return {
        'total_combined_trades': total_combined_trades,
        'combined_trades_per_week': combined_trades_per_week,
        'portfolio_win_rate': portfolio_win_rate,
        'avg_correlation': float(avg_corr),
        'strategy_results': strategy_results
    }

if __name__ == "__main__":
    run_portfolio_verification()
