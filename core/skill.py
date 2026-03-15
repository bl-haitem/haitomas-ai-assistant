from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Skill(ABC):
    """Base class for all haitomas modular skills."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier of the skill."""
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Returns the function definitions for the LLM."""
        pass

    @abstractmethod
    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Executes a specific action within this skill."""
        pass
