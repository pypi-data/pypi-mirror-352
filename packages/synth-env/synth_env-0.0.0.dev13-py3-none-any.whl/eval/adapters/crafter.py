"""
Crafter environment adapter for the evaluation framework.

Integrates the beautiful evaluation framework with Crafter Classic environment.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

from .base import BaseEnvironmentAdapter
from ..core.types import TaskInstance


@dataclass
class CrafterTaskInstance:
    """Wrapper for Crafter task instances to match TaskInstance protocol."""
    
    original_instance: Any  # The original crafter task instance
    
    @property
    def instance_id(self) -> str:
        return str(getattr(self.original_instance, 'seed', 'unknown'))
    
    @property
    def description(self) -> str:
        # Extract description from various possible fields
        if hasattr(self.original_instance, 'description'):
            return self.original_instance.description
        elif hasattr(self.original_instance, 'task_description'):
            return self.original_instance.task_description
        else:
            return f"Crafter task with seed {self.instance_id}"
    
    @property
    def metadata(self) -> Dict[str, Any]:
        metadata = {
            "environment": "crafter",
            "seed": self.instance_id
        }
        
        # Add metadata from original instance if available
        if hasattr(self.original_instance, 'metadata'):
            metadata.update(self.original_instance.metadata.__dict__)
        
        return metadata


class CrafterAdapter(BaseEnvironmentAdapter):
    """Adapter for Crafter Classic environment."""
    
    def __init__(self):
        super().__init__("crafter")
    
    async def _load_all_instances(self) -> List[TaskInstance]:
        """Load all Crafter task instances."""
        try:
            # Import crafter taskset
            from examples.crafter_classic.taskset import create_crafter_taskset
            
            # Create taskset and extract instances
            taskset = await create_crafter_taskset()
            
            # Wrap instances to match TaskInstance protocol
            wrapped_instances = []
            for instance in taskset.instances:
                wrapped = CrafterTaskInstance(original_instance=instance)
                wrapped_instances.append(wrapped)
            
            return wrapped_instances
            
        except ImportError as e:
            raise ImportError(f"Crafter environment not available: {e}")
        except Exception as e:
            raise Exception(f"Failed to load Crafter instances: {e}")
    
    async def _create_environment(self, instance: TaskInstance):
        """Create Crafter environment for the given task."""
        from examples.crafter_classic.environment import CrafterClassicEnvironment
        
        # Create environment with the original task instance
        env = CrafterClassicEnvironment(task_instance=instance.original_instance)
        return env
    
    async def _reset_environment(self, env, instance: TaskInstance) -> str:
        """Reset Crafter environment and return initial observation."""
        # Reset environment
        observation = await env.initialize()
        
        # Format observation for agent
        if isinstance(observation, dict):
            # Try different field names for the formatted observation
            for field in ["formatted_obs", "observation", "text", "state"]:
                if field in observation:
                    return str(observation[field])
            # Fallback to the whole dict as string
            return str(observation)
        else:
            return str(observation)
    
    async def _step_environment(self, env, action) -> Dict[str, Any]:
        """Step Crafter environment with action."""
        # Import the action map
        try:
            from examples.crafter_classic.engine_helpers.action_map import CRAFTER_ACTION_MAP
        except ImportError:
            # Fallback action map
            CRAFTER_ACTION_MAP = {
                'noop': 0, 'move_left': 1, 'move_right': 2, 'move_up': 3, 'move_down': 4, 
                'do': 5, 'sleep': 6, 'place_stone': 7, 'place_table': 8, 'place_furnace': 9, 
                'place_plant': 10, 'make_wood_pickaxe': 11, 'make_stone_pickaxe': 12, 
                'make_iron_pickaxe': 13, 'make_wood_sword': 14, 'make_stone_sword': 15, 
                'make_iron_sword': 16
            }
        
        # Parse action from agent (could be string action name or dict)
        if isinstance(action, str):
            action_int = CRAFTER_ACTION_MAP.get(action, 0)  # Default to no-op
        elif isinstance(action, dict) and "action" in action:
            action_str = action["action"]
            if isinstance(action_str, str):
                action_int = CRAFTER_ACTION_MAP.get(action_str, 0)  # Map string to int
            elif isinstance(action_str, int):
                action_int = action_str
            else:
                action_int = 0  # Default to no-op
        elif isinstance(action, int):
            action_int = action
        else:
            action_int = 0  # Default to no-op
        
        # Create tool call for Crafter environment  
        from environment.tools import EnvToolCall
        tool_call = EnvToolCall(tool="interact", args={"action": action_int})
        
        # Step environment
        observation = await env.step(tool_call)
        
        # Extract reward, done, and info from observation
        reward = 0.0
        done = False
        info = {}
        
        if isinstance(observation, dict):
            # Extract reward - prioritize total_reward_episode over last step
            if "total_reward_episode" in observation:
                reward = observation.get("total_reward_episode", 0.0)
            elif "reward_last_step" in observation:
                reward = observation.get("reward_last_step", 0.0)
            elif "private" in observation and isinstance(observation["private"], dict):
                private = observation["private"]
                reward = private.get("total_reward_episode", private.get("reward_last_step", 0.0))
            
            # Extract termination status
            if "terminated" in observation:
                done = observation.get("terminated", False) or observation.get("truncated", False)
            elif "private" in observation and isinstance(observation["private"], dict):
                private = observation["private"]
                done = private.get("terminated", False) or private.get("truncated", False)
            
            # Extract comprehensive info
            info = {
                "num_steps_taken": observation.get("num_steps_taken", 0),
                "max_steps_episode": observation.get("max_steps_episode", 0),
                "achievements_status": observation.get("achievements_status", {}),
                "inventory": observation.get("inventory", {}),
                "total_reward_episode": observation.get("total_reward_episode", 0.0),
                "reward_last_step": observation.get("reward_last_step", 0.0),
            }
            
            # Count achievements for better success determination
            achievements = observation.get("achievements_status", {})
            if achievements:
                unlocked_count = sum(1 for achieved in achievements.values() if achieved)
                info["achievements_unlocked"] = unlocked_count
            
            # Format observation text for agent (make it more readable)
            formatted_obs = self._format_crafter_observation(observation)
        else:
            formatted_obs = str(observation)
        
        return {
            "observation": formatted_obs,
            "reward": reward,
            "done": done,
            "info": info
        }
    
    async def _get_final_state(self, env) -> Dict[str, Any]:
        """Get final state from Crafter environment."""
        # Get current state from environment
        if hasattr(env, 'engine') and hasattr(env.engine, 'get_state'):
            state = env.engine.get_state()
        else:
            state = {}
        
        return state
    
    async def _cleanup_environment(self, env):
        """Clean up Crafter environment."""
        # Close environment if it has a close method
        if hasattr(env, 'close'):
            await env.close()
    
    def _format_crafter_observation(self, obs: Dict[str, Any]) -> str:
        """Format Crafter observation for agent readability."""
        # Extract key information
        inventory = obs.get("inventory", {})
        achievements = obs.get("achievements_status", {})
        steps = obs.get("num_steps_taken", 0)
        max_steps = obs.get("max_steps_episode", 0)
        total_reward = obs.get("total_reward_episode", 0.0)
        
        # Count achievements
        unlocked = sum(1 for achieved in achievements.values() if achieved)
        
        # Build readable observation
        parts = [
            f"=== Crafter Environment (Step {steps}/{max_steps}) ===",
            f"Total Reward: {total_reward:.3f}",
            f"Achievements Unlocked: {unlocked}/22",
            "",
            "=== Inventory ===",
        ]
        
        # Add inventory details
        for item, count in inventory.items():
            if count > 0:
                parts.append(f"{item}: {count}")
        
        # Add recently unlocked achievements
        if unlocked > 0:
            parts.append("\n=== Unlocked Achievements ===")
            for name, achieved in achievements.items():
                if achieved:
                    parts.append(f"✅ {name}")
        
        parts.append("\nAvailable actions: move_up, move_down, move_left, move_right, do, sleep, place_stone, place_table, place_furnace, place_plant, make_wood_pickaxe, make_stone_pickaxe, make_iron_pickaxe, make_wood_sword, make_stone_sword, make_iron_sword")
        
        return "\n".join(parts)
    
    def _determine_success(self, final_state: Dict[str, Any], final_score: float) -> bool:
        """Determine success for Crafter tasks."""
        # For Crafter, success means unlocking at least one achievement
        # The final_score might be negative due to time penalties, but achievements matter more
        
        # Check achievements in final state (from info)
        if "achievements_unlocked" in final_state and final_state["achievements_unlocked"] > 0:
            return True
        
        # Check achievements status
        if "achievements_status" in final_state:
            achievements = final_state["achievements_status"]
            if isinstance(achievements, dict):
                unlocked_count = sum(1 for achieved in achievements.values() if achieved)
                return unlocked_count > 0
        
        # Fallback to positive score (rare in Crafter due to time penalties)
        if final_score > 0:
            return True
        
        return False 