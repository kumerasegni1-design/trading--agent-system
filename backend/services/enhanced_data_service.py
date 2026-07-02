import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from integrations.data_downloaders import (
    DukascopyToolsDownloader,
    HistDataDownloader,
    AlternativeDataDownloaders,
    MultiTimeframeDownloader
)

logger = logging.getLogger(__name__)

class EnhancedDataService:
    """
    Enhanced data service supporting tick/1-min/multi-timeframe data
    from multiple FREE sources
    """
    
    def __init__(self):
        self.dukascopy = DukascopyToolsDownloader()
        self.histdata = HistDataDownloader()
        self.alternatives = AlternativeDataDownloaders()
        self.aggregator = MultiTimeframeDownloader()
        logger.info("📉 Enhanced data service initialized")
    
    async def download_tick_data(self, symbol: str, start_date: str, 
                                 end_date: str, source: str = "dukascopy") -> pd.DataFrame:
        """
        Download tick-level data (every transaction)
        
        Args:
            symbol: Trading pair (EURUSD, GBPUSD, etc.)
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            source: Data source ('dukascopy' recommended)
        
        Returns:
            DataFrame with bid/ask columns
        """
        logger.info(f"📥 Downloading tick data: {symbol} ({source})")
        
        try:
            if source == "dukascopy":
                df = await self.dukascopy.download_tick_data(symbol, start_date, end_date)
            else:
                logger.error(f"Unknown tick source: {source}")
                return pd.DataFrame()
            
            if df.empty:
                logger.warning("⚠️ No tick data available")
            
            return df
        
        except Exception as e:
            logger.error(f"❌ Error downloading tick data: {e}")
            raise
    
    async def download_minute_ohlc(self, symbol: str, start_date: str, 
                                   end_date: str, source: str = "dukascopy") -> pd.DataFrame:
        """
        Download 1-minute OHLC data
        
        Sources:
        - 'dukascopy': Free, high quality, large files
        - 'histdata': Very popular, requires pre-download
        - 'investpy': Investing.com scraping
        """
        logger.info(f"📥 Downloading 1-minute OHLC: {symbol} ({source})")
        
        try:
            if source == "dukascopy":
                df = await self.dukascopy.download_minute_ohlc(symbol, start_date, end_date)
            
            elif source == "histdata":
                # Load from pre-downloaded CSVs
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                
                dfs = []
                current = start
                while current <= end:
                    df = self.histdata.load_csv(symbol, current.year, current.month)
                    if not df.empty:
                        dfs.append(df)
                    
                    # Move to next month
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)
                
                df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
            
            elif source == "investpy":
                df = await self.alternatives.download_from_investpy(symbol, start_date, end_date)
            
            else:
                logger.error(f"Unknown source: {source}")
                return pd.DataFrame()
            
            if df.empty:
                logger.warning("⚠️ No 1-minute data available")
            
            return df
        
        except Exception as e:
            logger.error(f"❌ Error downloading minute data: {e}")
            raise
    
    async def download_multi_timeframe(self, symbol: str, start_date: str, 
                                      end_date: str, timeframes: List[str] = None,
                                      source: str = "dukascopy") -> Dict[str, pd.DataFrame]:
        """
        Download same data in multiple timeframes
        Downloads 1-minute and aggregates to higher timeframes
        
        Args:
            symbol: Trading pair
            start_date: Start date
            end_date: End date
            timeframes: List of timeframes ('1m', '5m', '15m', '1h', '4h', '1d')
            source: Base data source
        
        Returns:
            Dict with DataFrame for each timeframe
        """
        if timeframes is None:
            timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        
        logger.info(f"📉 Downloading multi-timeframe: {symbol} ({timeframes})")
        
        result = {}
        
        try:
            # Download base 1-minute data
            base_df = await self.download_minute_ohlc(symbol, start_date, end_date, source)
            
            if base_df.empty:
                logger.warning("⚠️ Could not download base 1-minute data")
                return result
            
            result['1m'] = base_df
            
            # Aggregate to higher timeframes
            for tf in timeframes:
                if tf == '1m':
                    continue
                
                try:
                    agg_df = self.aggregator.aggregate_ohlc(base_df, tf)
                    result[tf] = agg_df
                    logger.info(f"✅ {tf}: {len(agg_df)} candles")
                except Exception as e:
                    logger.warning(f"⚠️ Could not aggregate to {tf}: {e}")
            
            logger.info(f"✅ Multi-timeframe download complete")
            return result
        
        except Exception as e:
            logger.error(f"❌ Error in multi-timeframe download: {e}")
            raise
    
    async def download_forex_major_pairs(self, start_date: str, end_date: str,
                                        timeframe: str = "1m") -> Dict[str, pd.DataFrame]:
        """
        Download all major Forex pairs at once
        
        Pairs:
        - EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD (majors)
        - EURJPY, EURGBP, GBPJPY (crosses)
        """
        logger.info(f"📥 Downloading all major Forex pairs ({timeframe})")
        
        pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
            "AUDUSD", "USDCAD", "NZDUSD", "EURJPY", "EURGBP", "GBPJPY"
        ]
        
        result = {}
        for pair in pairs:
            try:
                logger.info(f"  ⏳ {pair}...")
                df = await self.download_minute_ohlc(pair, start_date, end_date)
                
                if not df.empty and timeframe != "1m":
                    df = self.aggregator.aggregate_ohlc(df, timeframe)
                
                result[pair] = df
            
            except Exception as e:
                logger.warning(f"  ❌ {pair}: {e}")
        
        logger.info(f"✅ Downloaded {len([d for d in result.values() if not d.empty])}/{len(pairs)} pairs")
        return result
    
    async def download_indices(self, start_date: str, end_date: str,
                              timeframe: str = "1m") -> Dict[str, pd.DataFrame]:
        """
        Download popular indices (Dukascopy CFDs)
        
        Indices:
        - SPX500 (S&P 500)
        - DAX (DAX 40)
        - FTSE (FTSE 100)
        - STOXX50E (Euro Stoxx 50)
        - HSI (Hang Seng)
        - N225 (Nikkei 225)
        """
        logger.info(f"📥 Downloading indices ({timeframe})")
        
        indices = ["SPX500", "DAX", "FTSE", "STOXX50E", "HSI", "N225"]
        
        result = {}
        for index in indices:
            try:
                logger.info(f"  ⏳ {index}...")
                df = await self.dukascopy.download_minute_ohlc(index, start_date, end_date)
                
                if not df.empty and timeframe != "1m":
                    df = self.aggregator.aggregate_ohlc(df, timeframe)
                
                result[index] = df
            
            except Exception as e:
                logger.warning(f"  ❌ {index}: {e}")
        
        logger.info(f"✅ Downloaded {len([d for d in result.values() if not d.empty])}/{len(indices)} indices")
        return result
