import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

class TradingPlatformService:
    """Service to manage connections with multiple trading platforms"""
    
    def __init__(self):
        self.platforms = {}
        logger.info("🚁 Trading platform service initialized")
    
    async def register_platform(self, platform_name: str, connector) -> bool:
        """Register a trading platform connector"""
        logger.info(f"📂 Registering platform: {platform_name}")
        self.platforms[platform_name] = connector
        return True
    
    async def execute_trade(self, platform: str, symbol: str, side: str, 
                           volume: float, price: float = None) -> Dict[str, Any]:
        """Execute trade on specified platform"""
        logger.info(f"🚀 Executing {side} on {platform}: {symbol} {volume} lots")
        
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} not registered")
        
        connector = self.platforms[platform]
        
        # Execute based on platform type
        if platform == "mt5":
            result = await connector.open_order(symbol, side.upper(), volume, price)
        elif platform == "alpaca":
            result = await connector.submit_order(symbol, volume, side, "market")
        else:
            raise ValueError(f"Unknown platform: {platform}")
        
        logger.info(f"✅ Trade executed: {result}")
        return result
    
    async def get_account_balance(self, platform: str) -> Dict[str, Any]:
        """Get account balance from platform"""
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} not registered")
        
        connector = self.platforms[platform]
        balance = await connector.get_account_info()
        return balance
    
    async def get_open_positions(self, platform: str) -> list:
        """Get all open positions on platform"""
        if platform not in self.platforms:
            raise ValueError(f"Platform {platform} not registered")
        
        connector = self.platforms[platform]
        positions = await connector.get_positions()
        return positions
