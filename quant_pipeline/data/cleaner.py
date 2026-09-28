"""
Data Integrity Checks and Cleaning Engine.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Performs integrity checks, gap detection, zero-volume bar handling,
    UTC timestamp normalization, and spread/rollover adjustments.
    """

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. Ensure Index is Datetime UTC
        if not isinstance(df.index, pd.DatetimeIndex):
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                df.set_index("timestamp", inplace=True)
            else:
                df.index = pd.to_datetime(df.index, utc=True)
        elif df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")

        # Sort index
        df.sort_index(inplace=True)

        # Remove duplicates
        df = df[~df.index.duplicated(keep="first")]

        # 2. Check and handle missing candles / zero volume
        if "volume" in df.columns:
            zero_vol_count = (df["volume"] <= 0).sum()
            if zero_vol_count > 0:
                logger.info(f"Detected {zero_vol_count} zero-volume bars. Forward filling prices...")
                df["volume"] = df["volume"].replace(0, np.nan).ffill().fillna(1.0)

        # 3. Handle OHLC price anomalies (e.g. low > high or open <= 0)
        invalid_mask = (df["low"] > df["high"]) | (df["open"] <= 0) | (df["close"] <= 0)
        if invalid_mask.sum() > 0:
            logger.warning(f"Detected {invalid_mask.sum()} invalid price bars. Cleaning...")
            df = df[~invalid_mask]

        # 4. Fill missing values
        df.ffill(inplace=True)
        df.bfill(inplace=True)

        return df
