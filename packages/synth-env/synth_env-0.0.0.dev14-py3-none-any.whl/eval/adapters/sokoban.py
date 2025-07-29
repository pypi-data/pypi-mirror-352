"""
Sokoban environment adapter for the evaluation framework.

Integrates the beautiful evaluation framework with Sokoban environment.
"""

from typing import List, Dict, Any
from dataclasses import dataclass

from .base import BaseEnvironmentAdapter
from ..core.types import TaskInstance


@dataclass
class SokobanTaskInstance:
    """Wrapper for Sokoban task instances to match TaskInstance protocol."""
    
    original_instance: Any  # The original sokoban task instance
    
    @property
    def instance_id(self) -> str:
        return str(self.original_instance.id)
    
    @property
    def description(self) -> str:
        # Extract description from various possible fields
        if hasattr(self.original_instance, 'impetus') and self.original_instance.impetus:
            return self.original_instance.impetus.instructions
        else:
            return f"Sokoban puzzle - difficulty: {self.metadata.get('difficulty', 'unknown')}"
    
    @property
    def metadata(self) -> Dict[str, Any]:
        metadata = {
            "environment": "sokoban",
            "instance_id": self.instance_id
        }
        
        # Add metadata from original instance if available
        if hasattr(self.original_instance, 'metadata') and self.original_instance.metadata:
            orig_meta = self.original_instance.metadata
            metadata.update({
                "difficulty": getattr(orig_meta, 'difficulty', 'unknown'),
                "num_boxes": getattr(orig_meta, 'num_boxes', 0),
                "dim_room": getattr(orig_meta, 'dim_room', (0, 0)),
                "max_steps": getattr(orig_meta, 'max_steps', 0),
                "shortest_path_length": getattr(orig_meta, 'shortest_path_length', 0),
                "seed": getattr(orig_meta, 'seed', 0)
            })
        
        return metadata


class SokobanAdapter(BaseEnvironmentAdapter):
    """Adapter for Sokoban environment."""
    
    def __init__(self):
        super().__init__("sokoban")
    
    async def _load_all_instances(self) -> List[TaskInstance]:
        """Load all Sokoban task instances."""
        try:
            # Import sokoban taskset
            from examples.sokoban.taskset import create_sokoban_taskset
            
            # Create taskset and extract instances  
            taskset = await create_sokoban_taskset()  # It is async after all
            
            # Wrap instances to match TaskInstance protocol
            wrapped_instances = []
            for instance in taskset.instances:
                wrapped = SokobanTaskInstance(original_instance=instance)
                wrapped_instances.append(wrapped)
            
            return wrapped_instances
            
        except ImportError as e:
            raise ImportError(f"Sokoban environment not available: {e}")
    
    async def _create_environment(self, instance: TaskInstance):
        """Create Sokoban environment for the given task."""
        from examples.sokoban.environment import SokobanEnvironment
        from examples.sokoban.engine import SynthSokobanObservationCallable
        
        # Create observation callable
        obs_callable = SynthSokobanObservationCallable()
        
        # Create environment with the original task instance
        env = SokobanEnvironment(
            task_instance=instance.original_instance,
            custom_step_obs=obs_callable
        )
        return env
    
    async def _reset_environment(self, env, instance: TaskInstance) -> str:
        """Reset Sokoban environment and return initial observation."""
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
        """Step Sokoban environment with action."""
        # Parse action from agent
        if isinstance(action, str):
            # Try to parse action as integer
            try:
                action_int = int(action)
            except ValueError:
                # Map action names to integers
                action_map = {
                    "up": 1, "move_up": 1,
                    "down": 2, "move_down": 2, 
                    "left": 3, "move_left": 3,
                    "right": 4, "move_right": 4,
                    "noop": 0, "no_action": 0
                }
                action_int = action_map.get(action.lower(), 0)  # Default to noop
        elif isinstance(action, dict) and "action" in action:
            if isinstance(action["action"], int):
                action_int = action["action"]
            elif isinstance(action["action"], str):
                try:
                    action_int = int(action["action"])
                except ValueError:
                    action_int = 0  # Default to noop
            else:
                action_int = 0
        elif isinstance(action, int):
            action_int = action
        else:
            action_int = 0  # Default to noop
        
        # Create tool call for Sokoban environment
        from environment.tools import EnvToolCall
        tool_call = EnvToolCall(tool="interact", args={"action": action_int})
        
        # Step environment
        observation = await env.step(tool_call)
        
        # Extract reward, done, and info from observation
        reward = 0.0
        done = False
        info = {}
        
        if isinstance(observation, dict):
            # Extract reward from private state if available
            if "private" in observation:
                private = observation["private"]
                if isinstance(private, dict):
                    reward = private.get("reward_last", 0.0)
                    done = private.get("terminated", False) or private.get("truncated", False)
            
            # Extract info from public state
            if "public" in observation:
                public = observation["public"]
                if isinstance(public, dict):
                    info = {
                        "boxes_on_target": public.get("boxes_on_target", 0),
                        "num_steps": public.get("num_steps", 0),
                        "max_steps": public.get("max_steps", 0),
                        "num_boxes": public.get("num_boxes", 0)
                    }
                    # Check if puzzle is solved
                    if public.get("boxes_on_target", 0) == public.get("num_boxes", 0):
                        done = True
            
            # Format observation text
            formatted_obs = ""
            for field in ["formatted_obs", "observation", "text", "state"]:
                if field in observation:
                    formatted_obs = str(observation[field])
                    break
            
            if not formatted_obs:
                formatted_obs = str(observation)
        else:
            formatted_obs = str(observation)
        
        return {
            "observation": formatted_obs,
            "reward": reward,
            "done": done,
            "info": info
        }
    
    async def _get_final_state(self, env) -> Dict[str, Any]:
        """Get final state from Sokoban environment."""
        # Get current state from environment
        if hasattr(env, 'engine') and hasattr(env.engine, 'get_current_states_for_observation'):
            priv_state, pub_state = env.engine.get_current_states_for_observation()
            
            # Convert to dictionaries
            final_state = {}
            if hasattr(priv_state, '__dict__'):
                final_state.update(priv_state.__dict__)
            if hasattr(pub_state, '__dict__'):
                final_state.update(pub_state.__dict__)
            
            return final_state
        else:
            return {}
    
    async def _cleanup_environment(self, env):
        """Clean up Sokoban environment."""
        # Terminate environment if it has a terminate method
        if hasattr(env, 'terminate'):
            await env.terminate()
    
    def _determine_success(self, final_state: Dict[str, Any], final_score: float) -> bool:
        """Determine success for Sokoban tasks."""
        # Sokoban success is when all boxes are on targets
        if "boxes_on_target" in final_state and "num_boxes" in final_state:
            return final_state["boxes_on_target"] == final_state["num_boxes"]
        
        # Fallback to positive score
        return final_score > 0 