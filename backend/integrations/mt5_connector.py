import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None
    logger.warning("⚠️ MetaTrader5 library not found. MT5Connector will run in mock mode.")

class MT5Connector:
    """Connects to MetaTrader 5 for live trading and paper trading"""
    
    def __init__(self, server: str, login: int, password: str, path: str = None):
        self.server = server
        self.login = login
        self.password = password
        self.path = path
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to MT5"""
        logger.info(f"🔌 Connecting to MT5 {self.server} (Login: {self.login})...")
        
        if mt5 is None:
            logger.warning("🚀 MT5 library missing - simulating connection")
            self.is_connected = True
            return True

        if not mt5.initialize(path=self.path, login=self.login, password=self.password, server=self.server):
            error = mt5.last_error()
            logger.error(f"❌ Failed to initialize MT5: {error}")
            return False

        self.is_connected = True
        logger.info("✅ Connected to MT5")
        return True
    
    async def open_order(self, symbol: str, order_type: str, volume: float, price: float = None, sl: float = None, tp: float = None) -> Dict[str, Any]:
        """Open a trading order"""
        if not self.is_connected:
            await self.connect()

        logger.info(f"🚀 Opening {order_type} order on {symbol} ({volume} lots)")
        
        if mt5 is None:
            logger.warning("🚀 MT5 library missing - simulating order")
            return {
                "ticket": 123456,
                "symbol": symbol,
                "type": order_type,
                "volume": volume,
                "status": "open",
                "opened_at": datetime.now().isoformat()
            }

        type_map = {
            "BUY": mt5.ORDER_TYPE_BUY,
            "SELL": mt5.ORDER_TYPE_SELL,
            "BUY_LIMIT": mt5.ORDER_TYPE_BUY_LIMIT,
            "SELL_LIMIT": mt5.ORDER_TYPE_SELL_LIMIT,
        }

        request = {
            "action": mt5.TRADE_ACTION_DEAL if "LIMIT" not in order_type else mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": type_map.get(order_type, mt5.ORDER_TYPE_BUY),
            "price": price or mt5.symbol_info_tick(symbol).ask,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 123456,
            "comment": "Agent Signal",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Order failed: {result.comment} (code: {result.retcode})")
            return {"status": "error", "message": result.comment, "code": result.retcode}

        logger.info(f"✅ Order opened: {result.order}")
        return {
            "ticket": result.order,
            "symbol": symbol,
            "type": order_type,
            "volume": volume,
            "status": "open",
            "opened_at": datetime.now().isoformat()
        }
    
    async def close_order(self, ticket: int) -> bool:
        """Close an open order"""
        logger.info(f"🔌 Closing order {ticket}")
        
        if mt5 is None:
            logger.warning("🚀 MT5 library missing - simulating close")
            return True

        position = mt5.positions_get(ticket=ticket)
        if not position:
            logger.error(f"❌ Position {ticket} not found")
            return False

        pos = position[0]
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask,
            "deviation": 20,
            "magic": 123456,
            "comment": "Agent Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"❌ Close failed: {result.comment}")
            return False

        logger.info("✅ Order closed")
        return True
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        logger.info("📊 Fetching account info...")
        
        # TODO: Get real account data
        account_info = {
            "balance": 10000.0,
            "equity": 10125.50,
            "profit": 125.50,
            "margin_free": 5000.0,
            "margin_used": 5000.0
        }
        
        return account_info
    
    async def disconnect(self):
        """Disconnect from MT5"""
        logger.info("🛑 Disconnecting from MT5...")
        
        # TODO: mt5.shutdown()
        
        self.is_connected = False
        logger.info("✅ Disconnected from MT5")
