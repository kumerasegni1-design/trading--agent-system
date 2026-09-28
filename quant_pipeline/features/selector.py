"""
Feature Importance Ranking and Selection Engine using MDI, MDA, and correlation filters.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple
from sklearn.ensemble import RandomForestClassifier


class FeatureSelector:
    """
    Computes feature importance rankings (MDI) and removes redundant/collinear features.
    """

    @staticmethod
    def filter_collinear(df_features: pd.DataFrame, threshold: float = 0.85) -> List[str]:
        """
        Removes collinear features with absolute correlation above threshold.
        """
        corr = df_features.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
        selected_features = [col for col in df_features.columns if col not in to_drop]
        return selected_features

    @staticmethod
    def rank_features_mdi(
        df_features: pd.DataFrame, target: pd.Series
    ) -> pd.Series:
        """
        Mean Decrease Impurity (MDI) feature importance.
        """
        rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        rf.fit(df_features, target)
        importances = pd.Series(rf.feature_importances_, index=df_features.columns)
        return importances.sort_values(ascending=False)
