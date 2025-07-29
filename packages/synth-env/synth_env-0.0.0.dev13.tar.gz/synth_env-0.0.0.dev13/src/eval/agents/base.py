"""
Base agent interface for the evaluation framework.

Provides the abstract base class that all agents must implement.
"""

from abc import ABC, abstractmethod
from typing import Union, Dict, Any, List
from ..core.types import Agent


class BaseAgent(Agent):
    """Base implementation of the Agent interface."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._terminated = False
        self.history: List[Dict[str, Any]] = []
    
    async def reset(self) -> None:
        """Reset agent state for a new episode."""
        self._terminated = False
        self.history.clear()
    
    @property
    def is_terminated(self) -> bool:
        """Whether the agent has requested termination."""
        return self._terminated
    
    def request_termination(self, reason: str = "Agent requested termination"):
        """Request termination of the episode."""
        self._terminated = True
        self.history.append({
            "type": "termination",
            "reason": reason
        })
    
    def add_to_history(self, entry_type: str, content: Any):
        """Add an entry to the agent's history."""
        self.history.append({
            "type": entry_type,
            "content": content
        })
    
    @abstractmethod
    async def step(self, observation: str) -> Union[str, Dict[str, Any]]:
        """Take a step given an observation."""
        ... 