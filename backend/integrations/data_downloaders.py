import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
import requests
from io import BytesIO
import zipfile
import os

logger = logging.getLogger(__name__)

class DukascopyToolsDownloader:
    """
    Download tick and 1-minute OHLC data from Dukascopy (FREE)
    
    Source: https://github.com/femtotrader/dukascopy-tools
    Supports: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, DAX, SPX500, etc.
    """
    
    # Dukascopy API endpoint
    BASE_URL = "https://datafeed.dukascopy.com/datafeed"
    
    # All supported pairs
    SUPPORTED_PAIRS = {
        # Majors
        "EURUSD": "EUR/USD",
        "GBPUSD": "GBP/USD",
        "USDJPY": "USD/JPY",
        "USDCHF": "USD/CHF",
        "AUDUSD": "AUD/USD",
        "USDCAD": "USD/CAD",
        "NZDUSD": "NZD/USD",
        # Minors
        "EURJPY": "EUR/JPY",
        "EURGBP": "EUR/GBP",
        "GBPJPY": "GBP/JPY",
        # Indices (CFD)
        "SPX500": "S&P 500",
        "DAX": "DAX 40",
        "FTSE": "FTSE 100",
        "STOXX50E": "Euro Stoxx 50",
        "HSI": "Hang Seng",
        "N225": "Nikkei 225",
    }
    
    def __init__(self):
        logger.info("🔍 Dukascopy downloader initialized")
        self.session = None
    
    async def download_tick_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Download tick-level data (every transaction) from Dukascopy
        Note: Tick data files are large (~500MB for 1 month per pair)
        
        Args:
            symbol: Trading pair (e.g., 'EURUSD')
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
        
        Returns:
            DataFrame with tick data (Bid, Ask columns)
        """
        logger.info(f"📥 Downloading tick data for {symbol} from {start_date} to {end_date}")
        
        if symbol not in self.SUPPORTED_PAIRS:
            logger.error(f"❌ Symbol {symbol} not supported. Available: {list(self.SUPPORTED_PAIRS.keys())}")
            raise ValueError(f"Symbol {symbol} not supported")
        
        try:
            dfs = []
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            current = start
            while current <= end:
                tick_data = await self._fetch_tick_day(symbol, current)
                if not tick_data.empty:
                    dfs.append(tick_data)
                
                current += timedelta(days=1)
            
            if dfs:
                df = pd.concat(dfs, ignore_index=True)
                logger.info(f"✅ Downloaded {len(df)} tick records")
                return df
            else:
                logger.warning(f"⚠️ No data found for {symbol}")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"❌ Error downloading tick data: {str(e)}")
            raise
    
    async def download_minute_ohlc(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Download 1-minute OHLC data from Dukascopy
        More practical than tick data for backtesting
        
        Args:
            symbol: Trading pair (e.g., 'EURUSD')
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
        
        Returns:
            DataFrame with OHLC data
        """
        logger.info(f"📥 Downloading 1-minute OHLC for {symbol}")
        
        try:
            dfs = []
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            current = start
            while current <= end:
                minute_data = await self._fetch_minute_day(symbol, current)
                if not minute_data.empty:
                    dfs.append(minute_data)
                
                current += timedelta(days=1)
            
            if dfs:
                df = pd.concat(dfs, ignore_index=True)
                df = df.sort_values('timestamp').reset_index(drop=True)
                logger.info(f"✅ Downloaded {len(df)} 1-minute candles")
                return df
            else:
                logger.warning(f"⚠️ No data found for {symbol}")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"❌ Error downloading minute data: {str(e)}")
            raise
    
    async def _fetch_tick_day(self, symbol: str, date: datetime) -> pd.DataFrame:
        """
        Fetch tick data for single day from Dukascopy API
        Format: https://datafeed.dukascopy.com/datafeed/EURUSD/2024/01/01/22h_ticks.bi5
        """
        try:
            year = date.year
            month = date.month - 1  # Dukascopy uses 0-based months
            day = date.day
            
            # Try each hour (Dukascopy splits by hour)
            dfs = []
            for hour in range(24):
                url = f"{self.BASE_URL}/{symbol}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=10) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                tick_data = self._parse_tick_data(data)
                                if not tick_data.empty:
                                    dfs.append(tick_data)
                except:
                    continue
            
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            return pd.DataFrame()
        
        except Exception as e:
            logger.debug(f"Could not fetch tick data for {date}: {e}")
            return pd.DataFrame()
    
    async def _fetch_minute_day(self, symbol: str, date: datetime) -> pd.DataFrame:
        """
        Fetch 1-minute OHLC data for single day
        Format: https://datafeed.dukascopy.com/datafeed/EURUSD/2024/01/01/00h_quotes.bi5
        """
        try:
            year = date.year
            month = date.month - 1  # 0-based
            day = date.day
            
            dfs = []
            for hour in range(24):
                url = f"{self.BASE_URL}/{symbol}/{year}/{month:02d}/{day:02d}/{hour:02d}h_quotes.bi5"
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=10) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                minute_data = self._parse_minute_data(data)
                                if not minute_data.empty:
                                    dfs.append(minute_data)
                except:
                    continue
            
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            return pd.DataFrame()
        
        except Exception as e:
            logger.debug(f"Could not fetch minute data for {date}: {e}")
            return pd.DataFrame()
    
    def _parse_tick_data(self, binary_data: bytes) -> pd.DataFrame:
        """
        Parse Dukascopy .bi5 tick data format
        Format per record: timestamp (4), bid (4), ask (4), bidvolume (4), askvolume (4)
        """
        try:
            import struct
            
            records = []
            for i in range(0, len(binary_data), 20):  # 20 bytes per record
                if i + 20 > len(binary_data):
                    break
                
                data = struct.unpack('>IffII', binary_data[i:i+20])
                timestamp = datetime.utcfromtimestamp(data[0] / 1000)
                
                records.append({
                    'timestamp': timestamp,
                    'bid': data[1],
                    'ask': data[2],
                    'bid_volume': data[3],
                    'ask_volume': data[4]
                })
            
            return pd.DataFrame(records)
        except:
            return pd.DataFrame()
    
    def _parse_minute_data(self, binary_data: bytes) -> pd.DataFrame:
        """
        Parse Dukascopy .bi5 minute OHLC data
        Format per record: timestamp (4), open (4), close (4), low (4), high (4), volume (4)
        """
        try:
            import struct
            
            records = []
            for i in range(0, len(binary_data), 24):  # 24 bytes per record
                if i + 24 > len(binary_data):
                    break
                
                data = struct.unpack('>IfffffI', binary_data[i:i+24])
                timestamp = datetime.utcfromtimestamp(data[0] / 1000)
                
                records.append({
                    'timestamp': timestamp,
                    'open': data[1],
                    'close': data[2],
                    'low': data[3],
                    'high': data[4],
                    'volume': data[6]
                })
            
            return pd.DataFrame(records)
        except:
            return pd.DataFrame()

class HistDataDownloader:
    """
    Download 1-minute OHLC data from HistData.com (FREE for Forex)
    
    Source: https://www.histdata.com/download-free-forex-data/
    Quality: Very high, widely used by traders
    Note: Requires manual download or local CSV files
    """
    
    SUPPORTED_PAIRS = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
        "USDCAD", "NZDUSD", "EURJPY", "EURGBP", "GBPJPY",
        "AUDCAD", "AUDCHF", "AUDJPY", "CADCHF", "CADJPY",
        "CHFJPY", "EURAUD", "EURCAD", "EURCHF", "NZDJPY"
    ]
    
    def __init__(self, data_dir: str = "./data/histdata"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        logger.info("🔍 HistData downloader initialized")
    
    def load_csv(self, symbol: str, year: int, month: int) -> pd.DataFrame:
        """
        Load pre-downloaded CSV from HistData.com
        
        Download manually from:
        https://www.histdata.com/download-free-forex-data/?/ascii/1-minute-bar-quotes/eurusd/YYYY/M
        
        Then extract CSV and place in ./data/histdata/
        """
        filename = f"{symbol}_{year}_{month:02d}.csv"
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"⚠️ File not found: {filepath}")
            logger.info(f"Download from: https://www.histdata.com/download-free-forex-data/")
            return pd.DataFrame()
        
        try:
            # HistData format: Date Time,Open,High,Low,Close,Volume
            df = pd.read_csv(filepath, sep=',')
            df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
            df = df.rename(columns={
                df.columns[1]: 'open',
                df.columns[2]: 'high',
                df.columns[3]: 'low',
                df.columns[4]: 'close',
                df.columns[5]: 'volume'
            })
            
            logger.info(f"✅ Loaded {len(df)} 1-minute candles from {filename}")
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        except Exception as e:
            logger.error(f"❌ Error loading CSV: {e}")
            return pd.DataFrame()

class AlternativeDataDownloaders:
    """
    Alternative free data sources for Forex and Indices
    """
    
    @staticmethod
    async def download_from_investpy(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Download from Investing.com via investpy (includes 1-min data)
        Source: https://github.com/alvarobartt/investpy
        """
        try:
            import investpy
            
            # Convert format EUR/USD -> eurusd
            pair = symbol.replace('/', '').lower()
            
            logger.info(f"📥 Downloading from Investing.com: {symbol}")
            
            df = investpy.stocks.get_stock_historical_data(
                stock=pair,
                country='spain',  # Generic
                from_date=start_date,
                to_date=end_date
            )
            
            logger.info(f"✅ Downloaded {len(df)} candles from Investing.com")
            return df
        
        except Exception as e:
            logger.warning(f"⚠️ Investpy error: {e}")
            return pd.DataFrame()
    
    @staticmethod
    async def download_from_polygon(symbol: str, start_date: str, end_date: str, 
                                   api_key: str = None) -> pd.DataFrame:
        """
        Download from Polygon.io (Free tier: 5 API calls/min, stocks only)
        Source: https://polygon.io
        """
        if not api_key:
            logger.warning("⚠️ Polygon API key not provided")
            return pd.DataFrame()
        
        try:
            # Polygon format: AAPL for stocks
            timeframe_map = {
                '1m': ('minute', 1),
                '5m': ('minute', 5),
                '15m': ('minute', 15),
                '1h': ('hour', 1),
                '1d': ('day', 1)
            }
            
            logger.info(f"📥 Downloading from Polygon.io: {symbol}")
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_date}/{end_date}"
            params = {'apikey': api_key, 'sort': 'asc', 'limit': 50000}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if data.get('status') == 'OK' and data.get('results'):
                            df = pd.DataFrame(data['results'])
                            df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
                            
                            df = df.rename(columns={
                                'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'
                            })
                            
                            logger.info(f"✅ Downloaded {len(df)} candles from Polygon")
                            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"❌ Polygon error: {e}")
            return pd.DataFrame()

class MultiTimeframeDownloader:
    """
    Download same data in multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
    Aggregates from base 1-minute data
    """
    
    @staticmethod
    def aggregate_ohlc(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        Aggregate 1-minute OHLC to higher timeframes
        
        Args:
            df: DataFrame with 1-minute OHLC
            timeframe: Target timeframe ('5m', '15m', '1h', '4h', '1d')
        
        Returns:
            Aggregated DataFrame
        """
        logger.info(f"📉 Aggregating to {timeframe}")
        
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must have 'timestamp' column")
        
        df = df.copy()
        df.set_index('timestamp', inplace=True)
        
        timeframe_map = {
            '5m': '5T', '15m': '15T', '30m': '30T',
            '1h': '1H', '4h': '4H', '1d': '1D'
        }
        
        if timeframe not in timeframe_map:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        
        agg_rules = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        
        aggregated = df.resample(timeframe_map[timeframe]).agg(agg_rules).dropna()
        aggregated.reset_index(inplace=True)
        
        logger.info(f"✅ Aggregated to {len(aggregated)} candles ({timeframe})")
        return aggregated
