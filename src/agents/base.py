"""Base agent class."""
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime
import uuid

from src.database.models import Activity
from src.database.database import get_db
from src.utils.logger import logger


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str):
        """
        Initialize agent.
        
        Args:
            name: Agent name (Hunter, Copywriter, Manager)
        """
        self.name = name
        logger.info("agent_initialized", agent=name)
    
    async def log_activity(
        self,
        lead_id: str,
        action: str,
        details: Dict[str, Any],
    ) -> None:
        """
        Log agent activity to database.
        
        Args:
            lead_id: Lead ID
            action: Action taken (e.g., "scraped", "scored", "drafted")
            details: Additional context
        """
        try:
            with get_db() as db:
                activity = Activity(
                    id=str(uuid.uuid4()),
                    lead_id=lead_id,
                    agent_name=self.name,
                    action=action,
                    details=details,
                    timestamp=datetime.utcnow(),
                )
                db.add(activity)
                db.commit()
            
            logger.info(
                "activity_logged",
                agent=self.name,
                lead_id=lead_id,
                action=action,
            )
            
        except Exception as e:
            logger.error(
                "activity_log_failed",
                agent=self.name,
                lead_id=lead_id,
                error=str(e),
            )
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute agent's main task.
        Must be implemented by subclasses.
        """
        pass
