import logging
from typing import Dict, Any, List
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataService:
    """Data aggregation and preparation service"""
    
    def __init__(self):
        logger.info("📊 Data service initialized")
    
    async def fetch_ohlc_data(self, symbol: str, start_date: str, end_date: str,
                             interval: str = "1d") -> pd.DataFrame:
        """Fetch OHLC data from Yahoo Finance"""
        logger.info(f"📥 Fetching {symbol} data ({interval})...")
        
        try:
            # Convert symbol format if needed (EUR/USD -> EURUSD=X)
            yf_symbol = symbol.replace("/", "") + ("=X" if "/" in symbol else "")
            
            df = yf.download(
                yf_symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False
            )
            
            logger.info(f"✅ Downloaded {len(df)} candles")
            return df
        except Exception as e:
            logger.error(f"❌ Error downloading data: {str(e)}")
            raise
    
    async def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML training"""
        logger.info("🚅 Preparing features...")
        
        df = df.copy()
        
        # Technical indicators
        df['RSI'] = self._calculate_rsi(df['Close'])
        df['MACD'], df['MACD_Signal'] = self._calculate_macd(df['Close'])
        df['BB_High'], df['BB_Low'] = self._calculate_bollinger_bands(df['Close'])
        df['ATR'] = self._calculate_atr(df['High'], df['Low'], df['Close'])
        df['CCI'] = self._calculate_cci(df['High'], df['Low'], df['Close'])
        
        # Returns and volatility
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(20).std()
        
        # Drop NaN values
        df = df.dropna()
        
        logger.info("✅ Features prepared")
        return df
    
    async def create_labels(self, df: pd.DataFrame, lookahead: int = 5,
                           threshold: float = 0.01) -> pd.Series:
        """Create trading labels (buy=1, sell=0)"""
        logger.info("📍 Creating labels...")
        
        future_returns = df['Close'].shift(-lookahead) / df['Close'] - 1
        labels = (future_returns > threshold).astype(int)
        
        return labels
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def _calculate_bollinger_bands(self, prices, period=20, num_std=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(period).mean()
        std = prices.rolling(period).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return upper, lower
    
    def _calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr
    
    def _calculate_cci(self, high, low, close, period=20):
        """Calculate Commodity Channel Index"""
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(period).mean()
        mad = tp.rolling(period).apply(lambda x: (x - x.mean()).abs().mean())
        cci = (tp - sma_tp) / (0.015 * mad)
        return cci
