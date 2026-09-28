import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable

class WalkForwardBacktester:
    """
    Backtesting engine enforcing strict 1:2 Risk-to-Reward (RR) ratio, zero future data leakage,
    and Walk-Forward Analysis (WFA) rolling splits.
    """

    def __init__(self, risk_reward_ratio: float = 2.0, max_holding_bars: int = 48, fee_pct: float = 0.0001):
        self.rr_ratio = risk_reward_ratio
        self.max_holding_bars = max_holding_bars
        self.fee_pct = fee_pct

    def backtest_signals(
        self,
        df: pd.DataFrame,
        signals: pd.Series,
        atr_series: pd.Series,
        sl_atr_mult: float = 1.5
    ) -> Dict[str, Any]:
        """
        Simulates trades based on signal Series (-1 for short, +1 for long, 0 for cash).
        Signals generated at bar t are executed at open of bar t+1.
        """
        trades = []
        n = len(df)
        times = df.index
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        atrs = atr_series.values
        sig_vals = signals.values

        i = 0
        while i < n - 1:
            sig = sig_vals[i]
            if sig != 0 and not np.isnan(atrs[i]) and atrs[i] > 0:
                entry_idx = i + 1
                if entry_idx >= n:
                    break

                entry_time = times[entry_idx]
                entry_price = opens[entry_idx]
                atr = atrs[i] # ATR calculated at signal bar

                sl_dist = atr * sl_atr_mult
                tp_dist = sl_dist * self.rr_ratio

                if sig == 1: # Long
                    sl_price = entry_price - sl_dist
                    tp_price = entry_price + tp_dist
                else: # Short
                    sl_price = entry_price + sl_dist
                    tp_price = entry_price - tp_dist

                # Simulate execution through subsequent bars
                exit_price = None
                exit_reason = None
                exit_idx = entry_idx

                for j in range(entry_idx, min(entry_idx + self.max_holding_bars, n)):
                    bar_high = highs[j]
                    bar_low = lows[j]

                    if sig == 1:
                        # Check if both SL and TP hit in same bar (conservative: assume SL hit first)
                        if bar_low <= sl_price and bar_high >= tp_price:
                            exit_price = sl_price
                            exit_reason = 'SL'
                            exit_idx = j
                            break
                        elif bar_low <= sl_price:
                            exit_price = sl_price
                            exit_reason = 'SL'
                            exit_idx = j
                            break
                        elif bar_high >= tp_price:
                            exit_price = tp_price
                            exit_reason = 'TP'
                            exit_idx = j
                            break
                    elif sig == -1:
                        if bar_high >= sl_price and bar_low <= tp_price:
                            exit_price = sl_price
                            exit_reason = 'SL'
                            exit_idx = j
                            break
                        elif bar_high >= sl_price:
                            exit_price = sl_price
                            exit_reason = 'SL'
                            exit_idx = j
                            break
                        elif bar_low <= tp_price:
                            exit_price = tp_price
                            exit_reason = 'TP'
                            exit_idx = j
                            break

                # If trade did not hit TP/SL within max_holding_bars, close at market close
                if exit_price is None:
                    exit_idx = min(entry_idx + self.max_holding_bars - 1, n - 1)
                    exit_price = closes[exit_idx]
                    exit_reason = 'TIME_EXIT'

                # Calculate pnl return
                if sig == 1:
                    raw_ret = (exit_price - entry_price) / entry_price
                else:
                    raw_ret = (entry_price - exit_price) / entry_price

                net_ret = raw_ret - (2 * self.fee_pct)

                trades.append({
                    'entry_time': entry_time,
                    'exit_time': times[exit_idx],
                    'signal': sig,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'sl_price': sl_price,
                    'tp_price': tp_price,
                    'exit_reason': exit_reason,
                    'net_return': net_ret,
                    'win': 1 if net_ret > 0 else 0,
                    'duration_bars': exit_idx - entry_idx + 1
                })

                # Move index past trade exit to avoid overlapping trades for the same strategy
                i = exit_idx
            else:
                i += 1

        return self._compute_metrics(trades, df)

    def walk_forward_validation(
        self,
        df: pd.DataFrame,
        strategy_func: Callable,
        n_splits: int = 5,
        train_ratio: float = 0.7
    ) -> Dict[str, Any]:
        """
        Runs walk-forward analysis over rolling n_splits windows.
        Guarantees zero overlap and zero data leakage.
        """
        n = len(df)
        window_size = n // n_splits
        all_oos_trades = []
        metrics_per_fold = []

        for k in range(n_splits):
            start_idx = k * window_size
            end_idx = min((k + 1) * window_size, n)
            fold_df = df.iloc[start_idx:end_idx].copy()

            split_idx = int(len(fold_df) * train_ratio)
            train_df = fold_df.iloc[:split_idx]
            test_df = fold_df.iloc[split_idx:]

            if len(train_df) < 50 or len(test_df) < 20:
                continue

            # Train/Fit strategy on train_df
            fitted_model, strategy_params = strategy_func(train_df, is_training=True)

            # Evaluate on out-of-sample test_df using fitted strategy
            test_signals, test_atr = strategy_func(test_df, is_training=False, model=fitted_model, params=strategy_params)

            fold_results = self.backtest_signals(test_df, test_signals, test_atr)
            metrics_per_fold.append(fold_results['metrics'])
            all_oos_trades.extend(fold_results['trades'])

        # Aggregate overall Out-Of-Sample (OOS) performance
        oos_summary = self._compute_metrics(all_oos_trades, df)
        oos_summary['fold_metrics'] = metrics_per_fold
        return oos_summary

    def _compute_metrics(self, trades: List[Dict[str, Any]], df: pd.DataFrame) -> Dict[str, Any]:
        if not trades:
            return {
                'metrics': {
                    'total_trades': 0,
                    'win_rate': 0.0,
                    'profit_factor': 0.0,
                    'total_return_pct': 0.0,
                    'sharpe_ratio': 0.0,
                    'max_drawdown_pct': 0.0,
                    'avg_trades_per_week': 0.0,
                },
                'trades': []
            }

        trades_df = pd.DataFrame(trades)
        total_trades = len(trades_df)
        wins = trades_df[trades_df['win'] == 1]
        losses = trades_df[trades_df['win'] == 0]

        win_rate = len(wins) / total_trades if total_trades > 0 else 0.0

        gross_profit = wins['net_return'].sum() if len(wins) > 0 else 0.0
        gross_loss = abs(losses['net_return'].sum()) if len(losses) > 0 else 0.0
        profit_factor = gross_profit / (gross_loss + 1e-10)

        cum_returns = (1 + trades_df['net_return']).cumprod()
        total_return_pct = (cum_returns.iloc[-1] - 1.0) * 100.0 if len(cum_returns) > 0 else 0.0

        # Drawdown
        peak = cum_returns.cummax()
        dd = (cum_returns - peak) / peak
        max_dd_pct = abs(dd.min()) * 100.0 if len(dd) > 0 else 0.0

        # Sharpe ratio (annualized assuming hourly bars or trade returns)
        rets = trades_df['net_return']
        sharpe_ratio = (rets.mean() / (rets.std() + 1e-10)) * np.sqrt(252) if len(rets) > 1 else 0.0

        # Calculate time span in weeks
        if len(df) > 1:
            time_span_days = (df.index[-1] - df.index[0]).total_seconds() / (86400.0)
            num_weeks = max(time_span_days / 7.0, 1.0)
        else:
            num_weeks = 1.0

        avg_trades_per_week = total_trades / num_weeks

        return {
            'metrics': {
                'total_trades': total_trades,
                'win_rate': float(round(win_rate, 4)),
                'profit_factor': float(round(profit_factor, 4)),
                'total_return_pct': float(round(total_return_pct, 4)),
                'sharpe_ratio': float(round(sharpe_ratio, 4)),
                'max_drawdown_pct': float(round(max_dd_pct, 4)),
                'avg_trades_per_week': float(round(avg_trades_per_week, 2)),
            },
            'trades': trades
        }
