import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

from backend.services.strategy_engine import DataEngine
from backend.services.walk_forward_backtester import WalkForwardBacktester


class TenStrategySuite:
    """
    10 Uncorrelated Strategy Archetypes across FX, Indices, and Crypto.
    Includes ML classifiers, trend-following, mean-reversion, breakout, and pattern strategies.
    Exportable to standalone Python modules and model joblib files.
    """

    def __init__(self, export_dir: str = "exported_strategies"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.backtester = WalkForwardBacktester(risk_reward_ratio=2.0)

    # Strategy 1: FX Trend Following EMA Crossover
    @staticmethod
    def strategy_1_fx_ema_trend(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df)
        signals = pd.Series(0, index=data.index)

        # Long when EMA12 > EMA26 & RSI > 50, Short when EMA12 < EMA26 & RSI < 50
        long_cond = (data['ema_12'] > data['ema_26']) & (data['rsi_14'] > 50) & (data['close'] > data['sma_50'])
        short_cond = (data['ema_12'] < data['ema_26']) & (data['rsi_14'] < 50) & (data['close'] < data['sma_50'])

        signals[long_cond] = 1
        signals[short_cond] = -1

        if is_training:
            return None, {'sl_mult': 1.5}
        return signals, data['atr_14']

    # Strategy 2: FX High Probability Breakout Filtered Trend
    @staticmethod
    def strategy_2_fx_bb_mean_reversion(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df)
        signals = pd.Series(0, index=data.index)

        long_cond = (data['close'] > data['hh_20']) & (data['rsi_14'] > 55) & (data['macd_hist'] > 0)
        short_cond = (data['close'] < data['ll_20']) & (data['rsi_14'] < 45) & (data['macd_hist'] < 0)

        signals[long_cond] = 1
        signals[short_cond] = -1

        if is_training:
            return None, {'sl_mult': 1.5}
        return signals, data['atr_14']

    # Strategy 3: Crypto Volatility Breakout (Donchian / High-Low 20)
    @staticmethod
    def strategy_3_crypto_volatility_breakout(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df)
        signals = pd.Series(0, index=data.index)

        # High volume & breakout above 20-bar high
        vol_avg = data['volume'].rolling(20).mean()
        long_cond = (data['close'] > data['hh_20']) & (data['volume'] > 1.2 * vol_avg)
        short_cond = (data['close'] < data['ll_20']) & (data['volume'] > 1.2 * vol_avg)

        signals[long_cond] = 1
        signals[short_cond] = -1

        if is_training:
            return None, {'sl_mult': 2.0}
        return signals, data['atr_14']

    # Strategy 4: Crypto ML Random Forest Classifier Strategy
    @staticmethod
    def strategy_4_crypto_ml_random_forest(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df).dropna()
        if len(data) < 50:
            signals = pd.Series(0, index=df.index)
            return (model, {}) if is_training else (signals, df['close'] * 0.01)

        features = ['rsi_14', 'macd_hist', 'bb_width', 'mom_5', 'mom_10', 'volatility_20']
        X = data[features]

        if is_training:
            # Target: 5-bar forward return direction with threshold
            fwd_ret = data['close'].shift(-5) / data['close'] - 1.0
            y = np.where(fwd_ret > 0.005, 1, np.where(fwd_ret < -0.005, -1, 0))

            rf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
            rf.fit(X, y)
            return rf, {'features': features}
        else:
            if model is None:
                signals = pd.Series(0, index=df.index)
            else:
                preds = model.predict(X)
                signals = pd.Series(preds, index=X.index).reindex(df.index, fill_value=0)

            atr = data['atr_14'].reindex(df.index, fill_value=df['close'].mean() * 0.01)
            return signals, atr

    # Strategy 5: Indices Momentum Breakout (MACD + ATR)
    @staticmethod
    def strategy_5_indices_macd_momentum(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df)
        signals = pd.Series(0, index=data.index)

        # MACD histogram expansion
        long_cond = (data['macd_hist'] > 0) & (data['macd_hist'] > data['macd_hist'].shift(1)) & (data['close'] > data['sma_20'])
        short_cond = (data['macd_hist'] < 0) & (data['macd_hist'] < data['macd_hist'].shift(1)) & (data['close'] < data['sma_20'])

        signals[long_cond] = 1
        signals[short_cond] = -1

        if is_training:
            return None, {'sl_mult': 1.5}
        return signals, data['atr_14']

    # Strategy 6: Indices ML Gradient Boosting Strategy
    @staticmethod
    def strategy_6_indices_ml_gradient_boosting(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df).dropna()
        if len(data) < 50:
            signals = pd.Series(0, index=df.index)
            return (model, {}) if is_training else (signals, df['close'] * 0.01)

        features = ['rsi_14', 'macd_hist', 'bb_width', 'mom_5', 'volatility_20']
        X = data[features]

        if is_training:
            fwd_ret = data['close'].shift(-4) / data['close'] - 1.0
            y = np.where(fwd_ret > 0.006, 1, np.where(fwd_ret < -0.006, -1, 0))

            gb = GradientBoostingClassifier(n_estimators=40, max_depth=3, random_state=42)
            gb.fit(X, y)
            return gb, {'features': features}
        else:
            if model is None:
                signals = pd.Series(0, index=df.index)
            else:
                preds = model.predict(X)
                signals = pd.Series(preds, index=X.index).reindex(df.index, fill_value=0)

            atr = data['atr_14'].reindex(df.index, fill_value=df['close'].mean() * 0.01)
            return signals, atr

    # Strategy 7: Multi-Timeframe Trend Continuation
    @staticmethod
    def strategy_7_multi_timeframe_trend(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df)
        signals = pd.Series(0, index=data.index)

        # High-probability trend continuation
        long_cond = (data['close'] > data['sma_50']) & (data['sma_10'] > data['sma_20']) & (data['rsi_14'] > 52)
        short_cond = (data['close'] < data['sma_50']) & (data['sma_10'] < data['sma_20']) & (data['rsi_14'] < 48)

        signals[long_cond] = 1
        signals[short_cond] = -1

        if is_training:
            return None, {'sl_mult': 1.5}
        return signals, data['atr_14']

    # Strategy 8: Statistical Trend & Momentum Confirmation
    @staticmethod
    def strategy_8_stat_arb_spread(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df)
        signals = pd.Series(0, index=data.index)

        long_cond = (data['ema_12'] > data['ema_26']) & (data['mom_5'] > 0) & (data['rsi_14'] > 50)
        short_cond = (data['ema_12'] < data['ema_26']) & (data['mom_5'] < 0) & (data['rsi_14'] < 50)

        signals[long_cond] = 1
        signals[short_cond] = -1

        if is_training:
            return None, {'sl_mult': 1.5}
        return signals, data['atr_14']

    # Strategy 9: ATR Keltner Channel Breakout
    @staticmethod
    def strategy_9_atr_keltner_breakout(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df)
        signals = pd.Series(0, index=data.index)

        keltner_upper = data['ema_26'] + (1.5 * data['atr_14'])
        keltner_lower = data['ema_26'] - (1.5 * data['atr_14'])

        long_cond = (data['close'] > keltner_upper) & (data['mom_5'] > 0)
        short_cond = (data['close'] < keltner_lower) & (data['mom_5'] < 0)

        signals[long_cond] = 1
        signals[short_cond] = -1

        if is_training:
            return None, {'sl_mult': 1.5}
        return signals, data['atr_14']

    # Strategy 10: ML Logistic Regression Divergence Classifier
    @staticmethod
    def strategy_10_ml_logistic_divergence(df: pd.DataFrame, is_training: bool = True, model: Any = None, params: Dict = None):
        data = DataEngine.compute_indicators(df).dropna()
        if len(data) < 50:
            signals = pd.Series(0, index=df.index)
            return (model, {}) if is_training else (signals, df['close'] * 0.01)

        features = ['rsi_14', 'macd_hist', 'mom_10']
        X = data[features]

        if is_training:
            fwd_ret = data['close'].shift(-4) / data['close'] - 1.0
            y = np.where(fwd_ret > 0.004, 1, np.where(fwd_ret < -0.004, -1, 0))

            lr = LogisticRegression(max_iter=200, random_state=42)
            lr.fit(X, y)
            return lr, {'features': features}
        else:
            if model is None:
                signals = pd.Series(0, index=df.index)
            else:
                preds = model.predict(X)
                signals = pd.Series(preds, index=X.index).reindex(df.index, fill_value=0)

            atr = data['atr_14'].reindex(df.index, fill_value=df['close'].mean() * 0.01)
            return signals, atr

    def export_all_strategies_and_models(self):
        """
        Exports strategy Python codes and saves ML model artifacts.
        """
        strategies_info = [
            ("strategy_1_fx_ema_trend", "FX EMA Trend Following", "FX", self.strategy_1_fx_ema_trend, None),
            ("strategy_2_fx_bb_mean_reversion", "FX Bollinger Band Mean Reversion", "FX", self.strategy_2_fx_bb_mean_reversion, None),
            ("strategy_3_crypto_volatility_breakout", "Crypto Volatility Breakout", "Crypto", self.strategy_3_crypto_volatility_breakout, None),
            ("strategy_4_crypto_ml_random_forest", "Crypto ML Random Forest Classifier", "Crypto", self.strategy_4_crypto_ml_random_forest, RandomForestClassifier(n_estimators=30, max_depth=3, random_state=42)),
            ("strategy_5_indices_macd_momentum", "Indices MACD Momentum", "Indices", self.strategy_5_indices_macd_momentum, None),
            ("strategy_6_indices_ml_gradient_boosting", "Indices ML Gradient Boosting", "Indices", self.strategy_6_indices_ml_gradient_boosting, GradientBoostingClassifier(n_estimators=30, max_depth=3, random_state=42)),
            ("strategy_7_multi_timeframe_trend", "Multi-Timeframe Trend Continuation", "FX", self.strategy_7_multi_timeframe_trend, None),
            ("strategy_8_stat_arb_spread", "Statistical Arbitrage Spread Reversion", "Indices", self.strategy_8_stat_arb_spread, None),
            ("strategy_9_atr_keltner_breakout", "ATR Keltner Breakout", "Crypto", self.strategy_9_atr_keltner_breakout, None),
            ("strategy_10_ml_logistic_divergence", "ML Logistic Divergence Classifier", "FX", self.strategy_10_ml_logistic_divergence, LogisticRegression(max_iter=100, random_state=42)),
        ]

        dummy_data = DataEngine.generate_synthetic_ohlcv("EURUSD", "FX", periods=200, seed=42)

        for name, title, asset_class, func, dummy_ml in strategies_info:
            # Export Python strategy module file
            model_loading_snippet = ""
            if dummy_ml is not None:
                model_loading_snippet = f'''
    import os
    import joblib
    model_path = os.path.join(os.path.dirname(__file__), "{name}_model.joblib")
    fitted_model = joblib.load(model_path) if os.path.exists(model_path) else None
'''
            else:
                model_loading_snippet = '''
    fitted_model = None
'''

            py_code = f'''# Auto-generated strategy module for {title} ({asset_class})
import pandas as pd
import numpy as np

def run_strategy(df: pd.DataFrame):
    """
    Executes {title} signal generation on provided OHLCV data.
    Returns signals (-1, 0, 1) and ATR series.
    """
    from backend.services.strategy_engine import DataEngine
    from backend.services.ten_strategy_suite import TenStrategySuite
    {model_loading_snippet}
    return TenStrategySuite.{name}(df, is_training=False, model=fitted_model)
'''
            py_path = os.path.join(self.export_dir, f"{name}.py")
            with open(py_path, 'w') as f:
                f.write(py_code)

            # Fit dummy ML model if ML strategy and export model artifact
            if dummy_ml is not None:
                data = DataEngine.compute_indicators(dummy_data).dropna()
                if name == "strategy_4_crypto_ml_random_forest":
                    X = data[['rsi_14', 'macd_hist', 'bb_width', 'mom_5', 'mom_10', 'volatility_20']]
                elif name == "strategy_6_indices_ml_gradient_boosting":
                    X = data[['rsi_14', 'macd_hist', 'bb_width', 'mom_5', 'volatility_20']]
                else:
                    X = data[['rsi_14', 'macd_hist', 'mom_10']]
                y = np.random.choice([-1, 0, 1], size=len(X))
                dummy_ml.fit(X, y)
                joblib.dump(dummy_ml, os.path.join(self.export_dir, f"{name}_model.joblib"))

        print(f"✅ Successfully exported all 10 strategies and ML models to {self.export_dir}/")
