"""
Hugging Face OANDA Historical 1-Minute Data Downloader
Downloads 1-minute Parquet data for Gold (XAUUSD) and EURUSD from bunqi/OANDA_* repositories.
Supports 5-year date ranges (e.g. 2020-2024), local caching, and resampling to higher timeframes.
"""

import os
import glob
import logging
import urllib.request
import json
from datetime import datetime
from typing import List, Optional, Dict
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

HF_DATASET_MAP = {
    "XAUUSD": "bunqi/OANDA_XAUUSD_Gold",
    "GOLD": "bunqi/OANDA_XAUUSD_Gold",
    "EURUSD": "bunqi/OANDA_EURUSD_EURUSD"
}

class HuggingFaceOandaDownloader:
    """Downloader for Hugging Face OANDA 1-minute historical datasets."""

    def __init__(self, cache_dir: str = "./data/oanda"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_available_months(self, symbol: str) -> List[str]:
        """Fetch list of available 1-minute Parquet filenames for symbol from Hugging Face API."""
        sym = symbol.upper()
        dataset_id = HF_DATASET_MAP.get(sym)
        if not dataset_id:
            raise ValueError(f"Unknown symbol: {symbol}. Supported: {list(HF_DATASET_MAP.keys())}")

        api_url = f"https://huggingface.co/api/datasets/{dataset_id}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        siblings = data.get("siblings", [])
        m1_files = [
            s["rfilename"] for s in siblings
            if s["rfilename"].startswith("1/") and s["rfilename"].endswith(".parquet")
        ]
        return sorted(m1_files)

    def download_month(self, symbol: str, rfilename: str, force_download: bool = False) -> str:
        """Download a single month Parquet file and return local path."""
        sym = symbol.upper()
        dataset_id = HF_DATASET_MAP.get(sym)
        if not dataset_id:
            raise ValueError(f"Unknown symbol: {symbol}")

        target_dir = os.path.join(self.cache_dir, sym)
        os.makedirs(target_dir, exist_ok=True)
        local_filename = os.path.basename(rfilename)
        local_path = os.path.join(target_dir, local_filename)

        if os.path.exists(local_path) and not force_download and os.path.getsize(local_path) > 1024:
            logger.debug(f"File cached: {local_path}")
            return local_path

        url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{rfilename}"
        logger.info(f"Downloading {url} to {local_path}...")

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response, open(local_path, "wb") as out_file:
            chunk = response.read(1024 * 1024)
            while chunk:
                out_file.write(chunk)
                chunk = response.read(1024 * 1024)

        logger.info(f"Successfully saved {local_path} ({os.path.getsize(local_path)} bytes)")
        return local_path

    def download_date_range(
        self,
        symbol: str,
        start_year: int = 2020,
        end_year: int = 2024,
        max_files: Optional[int] = None
    ) -> List[str]:
        """Download files spanning the given years."""
        sym = symbol.upper()
        available = self.get_available_months(sym)
        years = [str(y) for y in range(start_year, end_year + 1)]
        matched = [f for f in available if any(y in f for y in years)]

        if max_files:
            matched = matched[-max_files:]

        downloaded_paths = []
        for rfilename in matched:
            path = self.download_month(sym, rfilename)
            downloaded_paths.append(path)

        return downloaded_paths

    def load_data(
        self,
        symbol: str,
        start_year: int = 2020,
        end_year: int = 2024,
        max_files: Optional[int] = None
    ) -> pd.DataFrame:
        """Download (if needed) and load 1-minute OHLCV data into a single DataFrame."""
        sym = symbol.upper()
        paths = self.download_date_range(sym, start_year, end_year, max_files=max_files)
        if not paths:
            raise FileNotFoundError(f"No files found for {symbol} ({start_year}-{end_year})")

        dfs = []
        for path in sorted(paths):
            try:
                df = pd.read_parquet(path)
                dfs.append(df)
            except Exception as e:
                logger.warning(f"Error reading {path}: {e}")

        if not dfs:
            raise ValueError(f"Failed to read any parquet files for {symbol}")

        combined = pd.concat(dfs, ignore_index=True)
        # Standardize columns
        # Hugging Face format: time (epoch int seconds), open, high, low, close, volume
        if "time" in combined.columns:
            combined["timestamp"] = pd.to_datetime(combined["time"], unit="s", utc=True)
        elif "timestamp" not in combined.columns:
            raise ValueError(f"Missing time column in dataset: {combined.columns}")

        combined = combined.sort_values("timestamp").drop_duplicates(subset=["timestamp"]).reset_index(drop=True)
        return combined[["timestamp", "open", "high", "low", "close", "volume"]]

    @staticmethod
    def resample_data(df: pd.DataFrame, timeframe: str = "5m") -> pd.DataFrame:
        """
        Resample 1-minute data into higher timeframes.
        Supported timeframes: '1m', '5m', '15m', '30m', '1h', '4h', '1d'.
        """
        if timeframe == "1m":
            return df.copy()

        tf_map = {
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "1h": "1h",
            "4h": "4h",
            "1d": "1D"
        }
        freq = tf_map.get(timeframe)
        if not freq:
            raise ValueError(f"Unsupported timeframe: {timeframe}. Supported: {list(tf_map.keys())}")

        df_indexed = df.set_index("timestamp")
        resampled = df_indexed.resample(freq).agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).dropna().reset_index()

        return resampled
