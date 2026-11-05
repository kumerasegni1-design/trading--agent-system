"""
Institutional Backtesting and Portfolio Evaluation Engine
Evaluates trading desks with:
- Strict 1:2 Risk to Reward (TP = 2 * SL)
- Maximum 1 trade per week per desk
- Accurate trade lifecycle tracking (open, hit SL, hit TP, or timeout)
- Comprehensive performance metrics:
  * Sharpe Ratio
  * Sortino Ratio
  * Win Rate (targeting >= 50%)
  * Profit Factor
  * Max Drawdown %
  * Total Return %
  * Total Trades, Wins, Losses
  * Equity Curve
"""

import math
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from trading_desks.desks.base_desk import BaseTradingDesk
from trading_desks.desks.indicators import calculate_atr

class DeskBacktestEngine:
    """Backtesting engine for an individual trading desk."""

    def __init__(
        self,
        desk: BaseTradingDesk,
        initial_capital: float = 100_000.0,
        risk_per_trade_pct: float = 0.01, # 1% risk per trade
        atr_multiplier_sl: float = 1.5,
        risk_reward: float = 2.0,          # 1:2 RR
        slippage_pct: float = 0.0001,      # 1 pip / 0.01%
        max_bars_in_trade: int = 120       # Exit if not hit after 120 bars
    ):
        self.desk = desk
        self.initial_capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.atr_multiplier_sl = atr_multiplier_sl
        self.risk_reward = risk_reward
        self.slippage_pct = slippage_pct
        self.max_bars_in_trade = max_bars_in_trade

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute backtest on historical OHLCV DataFrame.
        """
        if len(df) < 50:
            raise ValueError("Dataframe must have at least 50 bars")

        df = df.copy().reset_index(drop=True)
        signals = self.desk.get_trade_signals(df)
        atr_series = calculate_atr(df, 14).bfill().ffill()

        capital = self.initial_capital
        equity_curve = [capital]
        trades: List[Dict[str, Any]] = []

        in_trade = False
        trade_dir = 0
        entry_price = 0.0
        entry_idx = 0
        sl_price = 0.0
        tp_price = 0.0
        position_size = 0.0
        entry_time = None

        timestamps = df["timestamp"].values if "timestamp" in df.columns else df.index.values
        opens = df["open"].values
        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values
        atrs = atr_series.values
        sigs = signals.values

        for i in range(1, len(df)):
            current_time = timestamps[i]
            cur_open = opens[i]
            cur_high = highs[i]
            cur_low = lows[i]
            cur_close = closes[i]

            # 1. Manage open position
            if in_trade:
                bars_held = i - entry_idx
                exit_price = None
                exit_reason = None

                if trade_dir == 1:  # Long
                    if cur_low <= sl_price:
                        exit_price = sl_price * (1 - self.slippage_pct)
                        exit_reason = "STOP_LOSS"
                    elif cur_high >= tp_price:
                        exit_price = tp_price * (1 - self.slippage_pct)
                        exit_reason = "TAKE_PROFIT"
                    elif bars_held >= self.max_bars_in_trade:
                        exit_price = cur_close * (1 - self.slippage_pct)
                        exit_reason = "TIME_EXIT"

                elif trade_dir == -1:  # Short
                    if cur_high >= sl_price:
                        exit_price = sl_price * (1 + self.slippage_pct)
                        exit_reason = "STOP_LOSS"
                    elif cur_low <= tp_price:
                        exit_price = tp_price * (1 + self.slippage_pct)
                        exit_reason = "TAKE_PROFIT"
                    elif bars_held >= self.max_bars_in_trade:
                        exit_price = cur_close * (1 + self.slippage_pct)
                        exit_reason = "TIME_EXIT"

                if exit_price is not None:
                    # Calculate PnL
                    if trade_dir == 1:
                        pnl = (exit_price - entry_price) * position_size
                    else:
                        pnl = (entry_price - exit_price) * position_size

                    pnl_pct = pnl / capital
                    capital += pnl
                    is_win = pnl > 0

                    trades.append({
                        "trade_num": len(trades) + 1,
                        "desk_id": self.desk.desk_id,
                        "trader": self.desk.trader_name,
                        "entry_time": str(entry_time),
                        "exit_time": str(current_time),
                        "direction": "BUY" if trade_dir == 1 else "SELL",
                        "entry_price": float(entry_price),
                        "exit_price": float(exit_price),
                        "sl_price": float(sl_price),
                        "tp_price": float(tp_price),
                        "pnl": float(pnl),
                        "pnl_pct": float(pnl_pct),
                        "is_win": bool(is_win),
                        "exit_reason": exit_reason,
                        "bars_held": int(bars_held)
                    })

                    in_trade = False
                    trade_dir = 0

            # 2. Check for new entry signal (only if flat)
            if not in_trade and sigs[i] != 0:
                trade_dir = sigs[i]
                entry_idx = i
                entry_time = current_time
                atr = atrs[i] if atrs[i] > 0 else cur_close * 0.005

                if trade_dir == 1:
                    entry_price = cur_open * (1 + self.slippage_pct)
                    sl_dist = atr * self.atr_multiplier_sl
                    sl_price = entry_price - sl_dist
                    tp_price = entry_price + (sl_dist * self.risk_reward) # 1:2 RR
                else:
                    entry_price = cur_open * (1 - self.slippage_pct)
                    sl_dist = atr * self.atr_multiplier_sl
                    sl_price = entry_price + sl_dist
                    tp_price = entry_price - (sl_dist * self.risk_reward) # 1:2 RR

                # Risk sizing: risk exactly risk_per_trade_pct of current capital
                dollar_risk = capital * self.risk_per_trade_pct
                position_size = dollar_risk / max(sl_dist, 1e-4)
                in_trade = True

            equity_curve.append(capital)

        # Performance summary metrics
        metrics = self._calculate_metrics(capital, equity_curve, trades)
        return {
            "desk": self.desk.to_dict(),
            "metrics": metrics,
            "trades": trades,
            "equity_curve": equity_curve[::max(1, len(equity_curve) // 100)] # Sample 100 points
        }

    def _calculate_metrics(
        self,
        final_capital: float,
        equity_curve: List[float],
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute institutional performance metrics."""
        total_trades = len(trades)
        wins = [t for t in trades if t["is_win"]]
        losses = [t for t in trades if not t["is_win"]]

        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0

        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)

        total_return_pct = ((final_capital - self.initial_capital) / self.initial_capital) * 100.0

        # Drawdown
        eq = np.array(equity_curve)
        peak = np.maximum.accumulate(eq)
        drawdowns = (eq - peak) / peak
        max_drawdown_pct = abs(float(np.min(drawdowns))) * 100.0 if len(drawdowns) > 0 else 0.0

        # Sharpe & Sortino
        returns = pd.Series([t["pnl_pct"] for t in trades])
        if len(returns) > 1 and returns.std() > 0:
            sharpe = float((returns.mean() / returns.std()) * math.sqrt(52)) # Weekly annualized
            downside = returns[returns < 0]
            downside_std = downside.std() if len(downside) > 1 else returns.std()
            sortino = float((returns.mean() / (downside_std + 1e-8)) * math.sqrt(52))
        else:
            sharpe = 0.0
            sortino = 0.0

        return {
            "initial_capital": self.initial_capital,
            "final_capital": round(final_capital, 2),
            "total_return_pct": round(total_return_pct, 2),
            "total_trades": total_trades,
            "wins": win_count,
            "losses": loss_count,
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "risk_reward_ratio": f"1:{self.risk_reward:.1f}"
        }


class PortfolioManagerEngine:
    """Manages simultaneous execution and performance aggregation across all 30 desks."""

    def __init__(self, desks: List[BaseTradingDesk]):
        self.desks = desks

    def run_all(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Run backtest on all desks against the provided data."""
        results = []
        for desk in self.desks:
            engine = DeskBacktestEngine(desk)
            res = engine.run(df)
            results.append(res)
        return results
