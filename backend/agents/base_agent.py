import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all trading agents"""
    
    def __init__(self, event_bus, agent_name: str):
        self.event_bus = event_bus
        self.agent_name = agent_name
        self.tasks_completed = 0
        self.is_active = True
        logger.info(f"🤖 {agent_name} initialized")
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary task"""
        pass
    
    async def shutdown(self):
        """Cleanup resources"""
        self.is_active = False
        logger.info(f"🛑 {self.agent_name} shutdown")
    
    async def log_task(self, task_id: str, status: str, result: Any = None):
        """Log task execution"""
        await self.event_bus.emit(f"agent:{self.agent_name}", {
            "task_id": task_id,
            "status": status,
            "result": result
        })
        self.tasks_completed += 1
