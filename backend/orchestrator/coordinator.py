import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class EventBus:
    """Centralized event bus for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.event_history: List[Dict] = []
        self.max_history = 10000
    
    def subscribe(self, event_type: str, callback: callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"📡 Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all subscribers"""
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        logger.debug(f"📡 Emitting event: {event_type}")
        
        # Call all subscribers
        if event_type in self.subscribers:
            tasks = [
                callback(event)
                for callback in self.subscribers[event_type]
            ]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get event history, optionally filtered by type"""
        history = self.event_history
        
        if event_type:
            history = [e for e in history if e["type"] == event_type]
        
        return history[-limit:]

class AgentCoordinator:
    """Orchestrates all agents and manages their communication"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.active_tasks: Dict[str, Dict] = {}
        self.strategies_marketplace: List[Dict] = []
        self.models_marketplace: List[Dict] = []
        logger.info("🎯 AgentCoordinator initialized")
    
    async def initialize(self):
        """Initialize all agents"""
        logger.info("⚙️  Initializing agents...")
        
        # Import agents (avoid circular imports)
        from agents.strategy_generator import StrategyGeneratorAgent
        from agents.data_downloader import DataDownloaderAgent
        from agents.backtesting_critic import BacktestingCriticAgent
        from agents.ml_trainer import MLTrainerAgent
        from agents.research_agent import ResearchAgent
        from agents.verifier_agent import VerifierAgent
        from agents.deployment_agent import DeploymentAgent
        from agents.portfolio_manager import PortfolioManagerAgent
        
        # Create agent instances
        agents_config = [
            ("strategy_generator", StrategyGeneratorAgent),
            ("data_downloader", DataDownloaderAgent),
            ("backtesting_critic", BacktestingCriticAgent),
            ("ml_trainer", MLTrainerAgent),
            ("research_agent", ResearchAgent),
            ("verifier_agent", VerifierAgent),
            ("deployment_agent", DeploymentAgent),
            ("portfolio_manager", PortfolioManagerAgent),
        ]
        
        for agent_name, agent_class in agents_config:
            try:
                agent = agent_class(self.event_bus)
                self.agents[agent_name] = agent
                logger.info(f"✅ {agent_name} initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {agent_name}: {str(e)}")
    
    async def shutdown(self):
        """Shutdown all agents"""
        logger.info("🛑 Shutting down agents...")
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
                logger.info(f"✅ {agent_name} shutdown")
            except Exception as e:
                logger.error(f"❌ Failed to shutdown {agent_name}: {str(e)}")
    
    async def dispatch_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a user command to appropriate agents"""
        task_id = str(uuid.uuid4())
        prompt = command.get("prompt", "")
        
        logger.info(f"🎤 New command received: {prompt[:100]}...")
        
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "prompt": prompt,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "agents_involved": [],
            "results": {}
        }
        
        # Emit command to event bus
        await self.event_bus.emit("command:new", {
            "task_id": task_id,
            "prompt": prompt
        })
        
        return {
            "task_id": task_id,
            "status": "accepted",
            "message": "Command dispatched to agents"
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_name: {
                "name": agent_name,
                "status": "active",
                "tasks_completed": getattr(agent, "tasks_completed", 0)
            }
            for agent_name, agent in self.agents.items()
        }
    
    def get_active_tasks(self) -> Dict[str, Any]:
        """Get all active tasks"""
        return self.active_tasks
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.active_tasks.get(task_id)
    
    async def register_strategy(self, strategy: Dict[str, Any]) -> str:
        """Register a new strategy in marketplace"""
        strategy["id"] = str(uuid.uuid4())
        strategy["created_at"] = datetime.now().isoformat()
        strategy["status"] = "pending"
        self.strategies_marketplace.append(strategy)
        
        await self.event_bus.emit("strategy:new", strategy)
        return strategy["id"]
    
    async def register_model(self, model: Dict[str, Any]) -> str:
        """Register a new ML model in marketplace"""
        model["id"] = str(uuid.uuid4())
        model["created_at"] = datetime.now().isoformat()
        model["status"] = "training"
        self.models_marketplace.append(model)
        
        await self.event_bus.emit("model:new", model)
        return model["id"]
