import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class MLTrainingService:
    """ML model training and optimization service"""
    
    def __init__(self, models_dir: str = "./data/models"):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        logger.info("🤖 ML Training service initialized")
    
    async def train_model(self, X: pd.DataFrame, y: pd.Series, 
                         model_type: str = "random_forest", **kwargs) -> Dict[str, Any]:
        """Train ML model"""
        logger.info(f"🚀 Training {model_type} model...")
        
        try:
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            if model_type == "random_forest":
                model = RandomForestClassifier(
                    n_estimators=kwargs.get('n_estimators', 100),
                    max_depth=kwargs.get('max_depth', 10),
                    random_state=42
                )
            elif model_type == "gradient_boosting":
                model = GradientBoostingClassifier(
                    n_estimators=kwargs.get('n_estimators', 100),
                    learning_rate=kwargs.get('learning_rate', 0.1),
                    random_state=42
                )
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            # Save model
            model_id = f"model_{int(np.random.random() * 1000000)}"
            model_path = os.path.join(self.models_dir, f"{model_id}.pkl")
            joblib.dump(model, model_path)
            
            logger.info(f"✅ Model trained and saved: {model_id}")
            
            return {
                "model_id": model_id,
                "model_type": model_type,
                "model_path": model_path,
                "train_accuracy": train_score,
                "test_accuracy": test_score,
                "overfit_ratio": train_score / max(test_score, 0.01),
                "feature_importance": self._get_feature_importance(model, X.columns)
            }
        except Exception as e:
            logger.error(f"❌ Training failed: {str(e)}")
            raise
    
    async def hyperparameter_optimization(self, X: pd.DataFrame, y: pd.Series,
                                         model_type: str = "random_forest") -> Dict[str, Any]:
        """Optimize hyperparameters using grid search"""
        logger.info("🔍 Optimizing hyperparameters...")
        
        # TODO: Implement GridSearchCV or Optuna
        best_params = {
            "n_estimators": 150,
            "max_depth": 8,
            "learning_rate": 0.05
        }
        
        return best_params
    
    async def ensemble_multiple_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Create ensemble of multiple models"""
        logger.info("🎯 Creating ensemble of models...")
        
        models = {}
        
        # Train multiple model types
        for model_type in ["random_forest", "gradient_boosting"]:
            model_info = await self.train_model(X, y, model_type=model_type)
            models[model_type] = model_info
        
        logger.info("✅ Ensemble created")
        return models
    
    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Extract feature importance from model"""
        try:
            importances = model.feature_importances_
            return dict(zip(feature_names, importances))
        except:
            return {}
