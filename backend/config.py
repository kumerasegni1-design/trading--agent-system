import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # ==================
    # API Configuration
    # ==================
    DEBUG: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # ==================
    # LLM Configuration
    # ==================
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # ==================
    # Database Configuration
    # ==================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trading_agent.db")
    POSTGRES_URL: Optional[str] = os.getenv("POSTGRES_URL")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # ==================
    # Trading Platforms
    # ==================
    MT5_SERVER: str = os.getenv("MT5_SERVER", "ICMarkets-Demo")
    MT5_LOGIN: Optional[str] = os.getenv("MT5_LOGIN")
    MT5_PASSWORD: Optional[str] = os.getenv("MT5_PASSWORD")
    MT5_PATH: str = os.getenv("MT5_PATH", "C:\\Program Files\\FxPro - MT5\\")
    TRADINGVIEW_API_KEY: Optional[str] = os.getenv("TRADINGVIEW_API_KEY")
    ALPACA_API_KEY: Optional[str] = os.getenv("ALPACA_API_KEY")
    ALPACA_SECRET_KEY: Optional[str] = os.getenv("ALPACA_SECRET_KEY")
    ALPACA_BASE_URL: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    
    # ==================
    # Data Sources
    # ==================
    POLYGON_API_KEY: Optional[str] = os.getenv("POLYGON_API_KEY")
    DUKASCOPY_BASE_URL: str = os.getenv("DUKASCOPY_BASE_URL", "https://datafeed.dukascopy.com/datafeed/")
    YAHOO_FINANCE_USE_API: bool = os.getenv("YAHOO_FINANCE_USE_API", "true").lower() == "true"
    
    # ==================
    # Colab & Kaggle
    # ==================
    COLAB_NOTEBOOK_ID: Optional[str] = os.getenv("COLAB_NOTEBOOK_ID")
    KAGGLE_USERNAME: Optional[str] = os.getenv("KAGGLE_USERNAME")
    KAGGLE_API_KEY: Optional[str] = os.getenv("KAGGLE_API_KEY")
    GOOGLE_COLAB_AUTH_TOKEN: Optional[str] = os.getenv("GOOGLE_COLAB_AUTH_TOKEN")
    
    # ==================
    # System Configuration
    # ==================
    MAX_AGENTS: int = int(os.getenv("MAX_AGENTS", "10"))
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "3600"))
    BACKTEST_LOOKBACK_YEARS: int = int(os.getenv("BACKTEST_LOOKBACK_YEARS", "5"))
    MIN_SHARPE_RATIO: float = float(os.getenv("MIN_SHARPE_RATIO", "1.0"))
    MAX_DRAWDOWN_PCT: float = float(os.getenv("MAX_DRAWDOWN_PCT", "30"))
    WALK_FORWARD_PERIODS: int = int(os.getenv("WALK_FORWARD_PERIODS", "5"))
    
    # ==================
    # Backtesting Config
    # ==================
    BACKTEST_ENGINE: str = os.getenv("BACKTEST_ENGINE", "quantconnect")
    VECTORIZED_BACKTESTER: bool = os.getenv("VECTORIZED_BACKTESTER", "true").lower() == "true"
    CALCULATE_OPTIMIZATION_METRICS: bool = os.getenv("CALCULATE_OPTIMIZATION_METRICS", "true").lower() == "true"
    
    # ==================
    # Logging & Monitoring
    # ==================
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    MONITOR_AGENT_PERFORMANCE: bool = os.getenv("MONITOR_AGENT_PERFORMANCE", "true").lower() == "true"
    
    # ==================
    # Agent Features
    # ==================
    ENABLE_STRATEGY_GENERATOR: bool = os.getenv("ENABLE_STRATEGY_GENERATOR", "true").lower() == "true"
    ENABLE_DATA_DOWNLOADER: bool = os.getenv("ENABLE_DATA_DOWNLOADER", "true").lower() == "true"
    ENABLE_BACKTESTING_CRITIC: bool = os.getenv("ENABLE_BACKTESTING_CRITIC", "true").lower() == "true"
    ENABLE_ML_TRAINER: bool = os.getenv("ENABLE_ML_TRAINER", "true").lower() == "true"
    ENABLE_RESEARCH_AGENT: bool = os.getenv("ENABLE_RESEARCH_AGENT", "true").lower() == "true"
    ENABLE_VERIFIER_AGENT: bool = os.getenv("ENABLE_VERIFIER_AGENT", "true").lower() == "true"
    ENABLE_DEPLOYMENT_AGENT: bool = os.getenv("ENABLE_DEPLOYMENT_AGENT", "true").lower() == "true"
    ENABLE_PORTFOLIO_MANAGER: bool = os.getenv("ENABLE_PORTFOLIO_MANAGER", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{settings.LOG_DIR}/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
