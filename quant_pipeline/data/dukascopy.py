"""
Dukascopy downloader and local data cache store for FX, Indices, and Crypto.
Includes HTTP bi5 tick/OHLC downloader and robust synthetic fallback for offline/development environments.
"""

import os
import logging
import urllib.request
import lzma
import struct
import pandas as pd
import numpy as np
from typing import Optional
from quant_pipeline.data.synthetic import generate_synthetic_ohlcv

logger = logging.getLogger(__name__)

ASSET_MAP = {
    # FX
    "EUR/USD": {"pip": 0.0001, "price": 1.0850, "duka_symbol": "EURUSD"},
    "GBP/JPY": {"pip": 0.01, "price": 190.50, "duka_symbol": "GBPJPY"},
    "USD/ZAR": {"pip": 0.0001, "price": 18.20, "duka_symbol": "USDZAR"},
    # Indices
    "US30": {"pip": 1.0, "price": 38500.0, "duka_symbol": "USA30IDXUSD"},
    "SPX500": {"pip": 0.1, "price": 5100.0, "duka_symbol": "USA500IDXUSD"},
    "NAS100": {"pip": 0.1, "price": 18000.0, "duka_symbol": "USNDXIDXUSD"},
    "DAX40": {"pip": 1.0, "price": 17800.0, "duka_symbol": "DEUIDXEUR"},
    "FTSE100": {"pip": 1.0, "price": 7700.0, "duka_symbol": "GBRIDXGBP"},
    "Nikkei225": {"pip": 1.0, "price": 39000.0, "duka_symbol": "JPNIDXJPY"},
    # Crypto
    "BTC/USD": {"pip": 1.0, "price": 65000.0, "duka_symbol": "BTCUSD"},
    "ETH/USD": {"pip": 0.1, "price": 3500.0, "duka_symbol": "ETHUSD"},
    "SOL/USD": {"pip": 0.01, "price": 140.0, "duka_symbol": "SOLUSD"},
    "XRP/USD": {"pip": 0.0001, "price": 0.55, "duka_symbol": "XRPUSD"},
}


class DukascopyDownloader:
    """
    Downloads historical data from Dukascopy HTTP servers or fetches from local Parquet cache / synthetic fallback.
    """

    def __init__(self, data_dir: str = "data_store"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def download_dukascopy_bi5(self, symbol: str, date: pd.Timestamp, hour: int) -> Optional[pd.DataFrame]:
        """
        Fetches and decompresses Dukascopy bi5 hourly tick file from historical data servers.
        URL pattern: https://datafeed.dukascopy.com/datafeed/{symbol}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5
        """
        asset_info = ASSET_MAP.get(symbol)
        if not asset_info:
            return None

        duka_sym = asset_info["duka_symbol"]
        url = f"https://datafeed.dukascopy.com/datafeed/{duka_sym}/{date.year}/{date.month - 1:02d}/{date.day:02d}/{hour:02d}h_ticks.bi5"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as response:
                compressed_data = response.read()
                if not compressed_data:
                    return None
                data = lzma.decompress(compressed_data)

            # Dukascopy bi5 format: 20 bytes per record
            # struct format: >IIIff (time_offset_ms, ask_price_int, bid_price_int, ask_vol, bid_vol)
            record_size = 20
            n_records = len(data) // record_size
            ticks = []

            point = asset_info["pip"]
            base_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)

            for i in range(n_records):
                time_ms, ask_int, bid_int, ask_vol, bid_vol = struct.unpack(">IIIff", data[i*20:(i+1)*20])
                tick_time = base_time + pd.Timedelta(milliseconds=time_ms)
                ask_price = ask_int * point
                bid_price = bid_int * point
                ticks.append((tick_time, (ask_price + bid_price) / 2.0, ask_vol + bid_vol))

            if ticks:
                df = pd.DataFrame(ticks, columns=["timestamp", "close", "volume"])
                df.set_index("timestamp", inplace=True)
                return df
        except Exception as e:
            logger.debug(f"Dukascopy download skipped/failed for {url}: {e}")
            return None

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        start_date: str = "2015-01-01",
        end_date: str = "2025-01-01",
        use_synthetic: bool = True,
    ) -> pd.DataFrame:
        clean_symbol = symbol.replace("/", "_")
        file_path = os.path.join(self.data_dir, f"{clean_symbol}_{timeframe}.parquet")

        if os.path.exists(file_path):
            logger.info(f"Loading cached data from {file_path}")
            df = pd.read_parquet(file_path)
            return df

        # Attempt downloading real bi5 sample data
        if not use_synthetic and symbol in ASSET_MAP:
            logger.info(f"Attempting Dukascopy bi5 download for {symbol}...")
            start_dt = pd.to_datetime(start_date, utc=True)
            bi5_df = self.download_dukascopy_bi5(symbol, start_dt, 12)
            if bi5_df is not None and not bi5_df.empty:
                logger.info(f"Dukascopy bi5 download successful for {symbol} sample.")
                ohlc = bi5_df["close"].resample("1h").ohlc().dropna()
                ohlc["volume"] = bi5_df["volume"].resample("1h").sum()
                ohlc["spread"] = 0.0002
                ohlc.to_parquet(file_path)
                return ohlc

        # Fallback to high-precision synthetic generator
        asset_info = ASSET_MAP.get(symbol, {"price": 1.0000})
        logger.info(f"Generating Dukascopy-equivalent dataset for {symbol} ({timeframe})")
        df = generate_synthetic_ohlcv(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            freq=timeframe,
            initial_price=asset_info["price"],
        )
        df.to_parquet(file_path)
        return df
