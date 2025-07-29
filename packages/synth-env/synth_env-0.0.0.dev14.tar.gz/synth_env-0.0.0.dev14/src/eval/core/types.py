"""
Type definitions for the evaluation framework.

Provides clean, environment-agnostic types for evaluation results,
filtering criteria, and configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Tuple, Union, Protocol
from abc import ABC, abstractmethod
from enum import Enum


class DifficultyLevel(str, Enum):
    """Standard difficulty levels for tasks."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNKNOWN = "unknown"


@dataclass
class EvalResult:
    """Result of a single evaluation run."""
    
    # Basic identification
    run_id: str
    model_name: str
    instance_id: str
    task_description: str
    
    # Core metrics
    success: bool
    final_score: float
    steps_taken: int
    duration_seconds: float
    
    # Detailed results from environment
    reward_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    
    # Error handling
    error_message: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilterCriteria:
    """Filtering criteria for evaluation instances."""
    
    # Token-based filtering
    token_range: Tuple[int, int] = (0, float('inf'))
    
    # Difficulty filtering
    difficulty_levels: Optional[Set[DifficultyLevel]] = None
    
    # Custom filtering
    scenario_types: Optional[Set[str]] = None
    required_features: Optional[Set[str]] = None
    
    # Limiting
    max_instances: Optional[int] = None
    
    # Custom filter functions
    custom_filters: List[callable] = field(default_factory=list)


@dataclass
class EvalConfig:
    """Configuration for evaluation runs."""
    
    # Model configuration
    models: List[str]
    concurrent_limit: int = 5
    timeout_seconds: float = 300.0
    
    # Evaluation parameters
    max_steps_per_episode: int = 100
    enable_progress_tracking: bool = True
    
    # Output configuration
    save_results: bool = True
    output_file: Optional[str] = None
    display_results: bool = True
    
    # Additional parameters
    extra_params: Dict[str, Any] = field(default_factory=dict)


class TaskInstance(Protocol):
    """Protocol for task instances across different environments."""
    
    @property
    def instance_id(self) -> str:
        """Unique identifier for this instance."""
        ...
    
    @property
    def description(self) -> str:
        """Human-readable description of the task."""
        ...
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Additional metadata about the task."""
        ...


class Agent(Protocol):
    """Protocol for agents that can interact with environments."""
    
    async def reset(self) -> None:
        """Reset agent state for a new episode."""
        ...
    
    async def step(self, observation: str) -> Union[str, Dict[str, Any]]:
        """Take a step given an observation."""
        ...
    
    @property
    def is_terminated(self) -> bool:
        """Whether the agent has requested termination."""
        ...


class EnvironmentAdapter(ABC):
    """Abstract base class for environment adapters."""
    
    @abstractmethod
    async def load_instances(self, criteria: FilterCriteria) -> List[TaskInstance]:
        """Load and filter task instances."""
        ...
    
    @abstractmethod
    async def run_episode(
        self, 
        instance: TaskInstance, 
        agent: Agent,
        max_steps: int = 100
    ) -> EvalResult:
        """Run a single evaluation episode."""
        ...
    
    @abstractmethod
    def estimate_token_count(self, instance: TaskInstance) -> int:
        """Estimate token count for an instance."""
        ...





@dataclass
class ProgressState:
    """State information for progress tracking."""
    
    current_instance: int
    total_instances: int
    current_model: str
    completed_runs: int
    total_runs: int
    start_time: float
    estimated_remaining: Optional[float] = None 