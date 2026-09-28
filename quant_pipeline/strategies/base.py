"""
Base Strategy Definition and Base Archetype Class.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseStrategy(ABC):
    """
    Abstract Base Class for all Strategy Archetypes.
    Generates signals: 1 (Long), -1 (Short), 0 (Neutral/Hold).
    """

    def __init__(self, name: str, params: Dict[str, Any]):
        self.name = name
        self.params = params

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Takes feature dataframe and returns Series of trading signals (1, -1, 0).
        Must rely exclusively on past data.
        """
        pass
