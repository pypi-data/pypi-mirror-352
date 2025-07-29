"""
Base adapter interface for environment integration.

Provides the abstract base class that all environment adapters must implement.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..core.types import (
    EnvironmentAdapter, 
    TaskInstance, 
    Agent, 
    EvalResult, 
    FilterCriteria
)
from ..core.filters import apply_filters


class BaseEnvironmentAdapter(EnvironmentAdapter):
    """Base implementation of EnvironmentAdapter with common functionality."""
    
    def __init__(self, environment_name: str):
        self.environment_name = environment_name
    
    async def load_instances(self, criteria: FilterCriteria) -> List[TaskInstance]:
        """Load and filter task instances."""
        # Load all instances
        all_instances = await self._load_all_instances()
        
        # Apply filtering
        filtered_instances = apply_filters(
            all_instances, 
            criteria, 
            token_estimator=self.estimate_token_count
        )
        
        return filtered_instances
    
    async def run_episode(
        self, 
        instance: TaskInstance, 
        agent: Agent,
        max_steps: int = 100
    ) -> EvalResult:
        """Run a single evaluation episode."""
        
        start_time = time.time()
        run_id = f"{agent.__class__.__name__}_{instance.instance_id}"
        
        # Initialize result
        result = EvalResult(
            run_id=run_id,
            model_name=getattr(agent, 'model_name', 'unknown'),
            instance_id=instance.instance_id,
            task_description=instance.description,
            success=False,
            final_score=0.0,
            steps_taken=0,
            duration_seconds=0.0,
            metadata={
                "environment": self.environment_name,
                "token_count": self.estimate_token_count(instance)
            }
        )
        
        try:
            # Create environment
            env = await self._create_environment(instance)
            
            # Reset agent and environment
            await agent.reset()
            observation = await self._reset_environment(env, instance)
            
            # Run episode loop
            step_count = 0
            episode_rewards = []
            
            while step_count < max_steps and not agent.is_terminated:
                # Agent takes action
                action = await agent.step(observation)
                
                # Environment processes action
                step_result = await self._step_environment(env, action)
                observation = step_result["observation"]
                reward = step_result.get("reward", 0.0)
                done = step_result.get("done", False)
                info = step_result.get("info", {})
                
                step_count += 1
                episode_rewards.append({
                    "step": step_count,
                    "reward": reward,
                    "info": info
                })
                
                # Check termination
                if done:
                    break
            
            # Extract final results
            final_state = await self._get_final_state(env)
            result.steps_taken = step_count
            result.final_score = sum(r["reward"] for r in episode_rewards)
            result.success = self._determine_success(final_state, result.final_score)
            result.reward_breakdown = episode_rewards
            result.duration_seconds = time.time() - start_time
            
            # Store final state in metadata for detailed analysis
            result.metadata.update(final_state)
            
            # Clean up environment
            await self._cleanup_environment(env)
            
        except Exception as e:
            result.error_message = str(e)
            result.duration_seconds = time.time() - start_time
        
        return result
    
    @abstractmethod
    async def _load_all_instances(self) -> List[TaskInstance]:
        """Load all available task instances for this environment."""
        ...
    
    @abstractmethod
    async def _create_environment(self, instance: TaskInstance):
        """Create environment instance for the given task."""
        ...
    
    @abstractmethod
    async def _reset_environment(self, env, instance: TaskInstance) -> str:
        """Reset environment and return initial observation."""
        ...
    
    @abstractmethod
    async def _step_environment(self, env, action) -> Dict[str, Any]:
        """Step environment with action and return result."""
        ...
    
    @abstractmethod
    async def _get_final_state(self, env) -> Dict[str, Any]:
        """Get final state from environment."""
        ...
    
    @abstractmethod
    async def _cleanup_environment(self, env):
        """Clean up environment resources."""
        ...
    
    def _determine_success(self, final_state: Dict[str, Any], final_score: float) -> bool:
        """Determine if the episode was successful."""
        # Default implementation based on positive score
        # Subclasses can override for environment-specific logic
        return final_score > 0.0
    
    def _extract_text_from_data(self, data: Any) -> str:
        """Recursively extract all string values from a data structure."""
        all_text = []
        
        if isinstance(data, str):
            all_text.append(data)
        elif isinstance(data, dict):
            for key, value in data.items():
                all_text.append(self._extract_text_from_data(value))
        elif isinstance(data, list):
            for item in data:
                all_text.append(self._extract_text_from_data(item))
        elif data is not None:
            all_text.append(str(data))
        
        return " ".join(all_text)
    
    def estimate_token_count(self, instance: TaskInstance) -> int:
        """Estimate token count for an instance."""
        # Extract all text from instance
        text_content = self._extract_text_from_data({
            "description": instance.description,
            "metadata": instance.metadata,
            "instance_id": instance.instance_id
        })
        
        try:
            # Try to use tiktoken for more accurate estimation
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            return len(encoding.encode(text_content))
        except ImportError:
            # Fallback to word-based estimation (roughly 0.75 tokens per word)
            words = len(text_content.split())
            return int(words * 0.75) 