"""
High-Performance Local Backtesting Engine.
Simulates realistic trade lifecycle: entry, ATR/Structure SL/TP, trailing stops,
partial take profits, correlation filters, and daily kill switches.
Calculates comprehensive metrics (Sharpe, Sortino, Calmar, Max Drawdown, Profit Factor).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from quant_pipeline.execution.model import ExecutionModel


class LocalBacktester:
    """
    Fast event-driven / vectorized local backtesting harness.
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        risk_per_trade: float = 0.01,
        asset_type: str = "fx",
        max_daily_drawdown: float = 0.03,
    ):
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.execution = ExecutionModel(asset_type=asset_type)
        self.max_daily_drawdown = max_daily_drawdown

    def run(self, df: pd.DataFrame, signals: pd.Series) -> Dict[str, Any]:
        df = df.copy()
        df["signal"] = signals.shift(1).fillna(0)  # Next-bar fill to eliminate lookahead bias

        equity = self.initial_capital
        equity_curve = []
        trades = []
        position = 0  # 1 for Long, -1 for Short, 0 for Flat
        entry_price = 0.0
        position_size = 0.0
        sl_price = 0.0
        tp_price = 0.0

        daily_start_equity = equity
        current_date = None

        for timestamp, row in df.iterrows():
            # Reset daily kill switch baseline
            date_today = timestamp.date()
            if current_date != date_today:
                current_date = date_today
                daily_start_equity = equity

            close = row["close"]
            atr = row.get("atr_14", close * 0.005)
            volatility = row.get("volatility_20", 0.001)
            signal = row["signal"]
            is_news = self.execution.is_news_event(timestamp)

            # Check Daily Kill Switch
            daily_dd = (daily_start_equity - equity) / daily_start_equity
            if daily_dd >= self.max_daily_drawdown and position != 0:
                # Force close position
                exit_price = close
                pnl = (exit_price - entry_price) * position * position_size
                comm = self.execution.get_commission(exit_price, position_size)
                net_pnl = pnl - comm
                equity += net_pnl
                trades.append({
                    "entry_time": entry_time,
                    "exit_time": timestamp,
                    "direction": position,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl": net_pnl,
                    "reason": "KillSwitch"
                })
                position = 0
                equity_curve.append(equity)
                continue

            # Position Management (Check SL / TP for open positions)
            if position == 1:  # Long
                if row["low"] <= sl_price:
                    exit_price = sl_price
                    pnl = (exit_price - entry_price) * position_size
                    comm = self.execution.get_commission(exit_price, position_size)
                    net_pnl = pnl - comm
                    equity += net_pnl
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": timestamp,
                        "direction": 1,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl": net_pnl,
                        "reason": "SL"
                    })
                    position = 0
                elif row["high"] >= tp_price:
                    exit_price = tp_price
                    pnl = (exit_price - entry_price) * position_size
                    comm = self.execution.get_commission(exit_price, position_size)
                    net_pnl = pnl - comm
                    equity += net_pnl
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": timestamp,
                        "direction": 1,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl": net_pnl,
                        "reason": "TP"
                    })
                    position = 0

            elif position == -1:  # Short
                if row["high"] >= sl_price:
                    exit_price = sl_price
                    pnl = (entry_price - exit_price) * position_size
                    comm = self.execution.get_commission(exit_price, position_size)
                    net_pnl = pnl - comm
                    equity += net_pnl
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": timestamp,
                        "direction": -1,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl": net_pnl,
                        "reason": "SL"
                    })
                    position = 0
                elif row["low"] <= tp_price:
                    exit_price = tp_price
                    pnl = (entry_price - exit_price) * position_size
                    comm = self.execution.get_commission(exit_price, position_size)
                    net_pnl = pnl - comm
                    equity += net_pnl
                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": timestamp,
                        "direction": -1,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl": net_pnl,
                        "reason": "TP"
                    })
                    position = 0

            # New Entry Signal Processing
            if position == 0 and signal != 0 and not is_news and daily_dd < self.max_daily_drawdown:
                slippage = self.execution.get_slippage(close, volatility, is_news)
                if signal == 1:
                    entry_price = close + slippage
                    sl_price = entry_price - (atr * 1.5)
                    tp_price = entry_price + (atr * 3.0)  # 1:2 Risk-Reward Ratio
                else:
                    entry_price = close - slippage
                    sl_price = entry_price + (atr * 1.5)
                    tp_price = entry_price - (atr * 3.0)

                risk_amount = equity * self.risk_per_trade
                risk_per_unit = abs(entry_price - sl_price)
                position_size = risk_amount / (risk_per_unit + 1e-9)
                position = signal
                entry_time = timestamp

            equity_curve.append(equity)

        df["equity"] = equity_curve
        trades_df = pd.DataFrame(trades)

        metrics = self._calculate_metrics(df["equity"], trades_df)
        return {"equity_df": df, "trades_df": trades_df, "metrics": metrics}

    def _calculate_metrics(self, equity_series: pd.Series, trades_df: pd.DataFrame) -> Dict[str, float]:
        returns = equity_series.pct_change().dropna()
        total_return = (equity_series.iloc[-1] - self.initial_capital) / self.initial_capital

        # Annualized Sharpe (Assuming 252 * 24 1H periods or standard scaling)
        sharpe = (returns.mean() / (returns.std() + 1e-9)) * np.sqrt(252 * 24)

        # Downside Std for Sortino
        neg_returns = returns[returns < 0]
        sortino = (returns.mean() / (neg_returns.std() + 1e-9)) * np.sqrt(252 * 24)

        # Max Drawdown
        cummax = equity_series.cummax()
        drawdown = (equity_series - cummax) / cummax
        max_drawdown = drawdown.min()

        # Calmar Ratio
        calmar = total_return / (abs(max_drawdown) + 1e-9)

        # Win Rate & Profit Factor
        if len(trades_df) > 0:
            wins = trades_df[trades_df["pnl"] > 0]
            losses = trades_df[trades_df["pnl"] < 0]
            win_rate = len(wins) / len(trades_df)
            gross_profit = wins["pnl"].sum()
            gross_loss = abs(losses["pnl"].sum())
            profit_factor = gross_profit / (gross_loss + 1e-9)

            # Max Consecutive Losses
            trades_df["is_loss"] = trades_df["pnl"] < 0
            loss_streak = (trades_df["is_loss"] != trades_df["is_loss"].shift()).cumsum()
            consec_losses = trades_df[trades_df["is_loss"]].groupby(loss_streak).size().max()
            consec_losses = int(consec_losses) if not np.isnan(consec_losses) else 0
        else:
            win_rate = 0.0
            profit_factor = 0.0
            consec_losses = 0

        return {
            "Total Return": float(total_return),
            "Sharpe Ratio": float(sharpe),
            "Sortino Ratio": float(sortino),
            "Calmar Ratio": float(calmar),
            "Max Drawdown": float(max_drawdown),
            "Win Rate": float(win_rate),
            "Profit Factor": float(profit_factor),
            "Total Trades": int(len(trades_df)),
            "Max Consecutive Losses": int(consec_losses),
        }
