"""
Data splitting and Purged Cross-Validation methodology to strictly prevent data leakage.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Generator


def split_data_60_20_20(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits dataset into 60% In-Sample (IS), 20% Out-of-Sample (OOS), and 20% Walk-Forward / Live Simulation.
    """
    n = len(df)
    is_end = int(n * 0.60)
    oos_end = int(n * 0.80)

    is_df = df.iloc[:is_end].copy()
    oos_df = df.iloc[is_end:oos_end].copy()
    wf_df = df.iloc[oos_end:].copy()

    return is_df, oos_df, wf_df


class PurgedGroupTimeSeriesSplit:
    """
    Purged K-Fold Cross Validation with Embargo Periods as per Marcos López de Prado.
    """

    def __init__(self, n_splits: int = 5, pct_embargo: float = 0.01):
        self.n_splits = n_splits
        self.pct_embargo = pct_embargo

    def split(self, df: pd.DataFrame) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        n_samples = len(df)
        indices = np.arange(n_samples)
        embargo_size = int(n_samples * self.pct_embargo)
        test_size = n_samples // self.n_splits

        for i in range(self.n_splits):
            test_start = i * test_size
            test_end = (i + 1) * test_size if i < self.n_splits - 1 else n_samples
            test_indices = indices[test_start:test_end]

            # Purging & Embargo: exclude training data immediately prior to test set and after test set
            train_left = indices[:max(0, test_start - embargo_size)]
            train_right = indices[min(n_samples, test_end + embargo_size):]
            train_indices = np.concatenate([train_left, train_right])

            yield train_indices, test_indices
