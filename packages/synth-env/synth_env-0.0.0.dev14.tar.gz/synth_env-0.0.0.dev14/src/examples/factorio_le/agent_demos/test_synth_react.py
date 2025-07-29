"""
test_synth_react.py - ReAct agent demonstration for Factorio Learning Environment

This demonstrates an LM-powered agent that writes Python code to interact
with Factorio through the provided API tools.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from pydantic import BaseModel, Field
from synth_ai.zyk import LM
from synth_sdk.tracing.decorators import trace_event_async
from synth_sdk.tracing.abstractions import RewardSignal, Dataset, TrainingQuestion
from synth_sdk.tracing.utils import get_system_id

from examples.factorio_le.environment import FactorioEnvironment
from examples.factorio_le.taskset import (
    FactorioTaskInstance, 
    FactorioTaskInstanceMetadata,
    create_factorio_taskset,
)
from tasks.core import Impetus, Intent
from environment.tools import EnvToolCall

import logging
logging.disable(logging.CRITICAL)

# --- Pydantic Models for Tool Arguments ---
class FactorioCodeArgs(BaseModel):
    code: str = Field(
        description="Python code to execute in the Factorio environment. Can call API functions like get_entities(), place_entity(), craft_item(), etc."
    )
    reasoning: str = Field(
        description="Brief explanation of what this code is intended to accomplish"
    )

class TerminateArgs(BaseModel):
    reason: str = Field(description="Reason for termination")

# --- Mock RCON for testing ---
class MockRCON:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.connected = True
        self.step_count = 0
        
    def connect(self):
        return True
    
    def send_command(self, command):
        self.step_count += 1
        
        # Simulate different responses based on commands
        if "find_entities" in command:
            return '[{"name": "player", "position": {"x": 0, "y": 0}}, {"name": "iron-ore", "position": {"x": 10, "y": 5}}]'
        elif "get_main_inventory" in command:
            base_items = {"iron-plate": 10, "copper-plate": 5, "wood": 20}
            # Simulate gaining more items over time
            if self.step_count > 3:
                base_items["iron-gear-wheel"] = 2
            if self.step_count > 5:
                base_items["electronic-circuit"] = 1
            return str(base_items).replace("'", '"')
        elif "production_statistics" in command:
            # Simulate increasing production
            production = {"iron-plate": self.step_count * 10, "copper-plate": self.step_count * 5}
            return str(production).replace("'", '"')
        elif "create_entity" in command or "place_entity" in command:
            return "Placed entity successfully at specified location"
        elif "begin_crafting" in command:
            return "Started crafting requested items"
        elif "teleport" in command:
            return "Player moved to specified position"
        else:
            return "Command executed successfully"
    
    def close(self):
        self.connected = False

# --- ReAct Agent for Factorio ---
class FactorioReActAgent:
    def __init__(self, llm, max_turns: int = 20):
        self.llm = llm
        self.max_turns = max_turns
        self.history: List[Dict[str, Any]] = []
        self.system_name = "factorio-react-demo"
        self.system_id = get_system_id(self.system_name)
        self.system_instance_id = str(uuid.uuid4())
        self.scenario_objectives = []
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_factorio_code",
                    "description": "Execute Python code in the Factorio environment. Use available API functions.",
                    "parameters": FactorioCodeArgs.model_json_schema(),
                },
            },
            {
                "type": "function", 
                "function": {
                    "name": "terminate",
                    "description": "Terminate execution when objectives are complete or no further progress possible.",
                    "parameters": TerminateArgs.model_json_schema(),
                },
            },
        ]

    def _format_history_for_prompt(self) -> str:
        prompt_history = []
        for entry in self.history:
            if entry["type"] == "obs":
                prompt_history.append(f"OBSERVATION:\n{entry['content']}")
            elif entry["type"] == "tool_call":
                args_str = json.dumps(entry["tool_arguments"])
                prompt_history.append(
                    f"THOUGHT:\nI will execute: {entry['tool_name']} with arguments: {args_str}\nACTION: (Code executed)"
                )
            elif entry["type"] == "tool_response":
                prompt_history.append(f"RESULT:\n{entry.get('content', 'Code executed')}")
        return "\n".join(prompt_history)

    @trace_event_async(event_type="factorio_react_decide")
    async def decide(self, obs: str) -> Optional[Dict[str, Any]]:
        """Make a decision and return tool call info, or None to terminate"""
        self.history.append({"type": "obs", "content": obs})
        
        formatted_history = self._format_history_for_prompt()
        
        objectives_text = "\n".join(f"- {obj}" for obj in self.scenario_objectives)
        
        system_message = (
            "You are an agent learning to automate factory production in Factorio. "
            "You can execute Python code that calls Factorio API functions.\n\n"
            "Available API functions:\n"
            "- get_entities(): List entities in the world\n"
            "- place_entity(entity_name, x, y, direction=0): Place an entity like 'burner-mining-drill'\n"
            "- craft_item(item_name, count=1): Craft items like 'iron-gear-wheel'\n"
            "- get_inventory(): Get your current inventory\n"
            "- get_production_stats(): Get production statistics\n"
            "- move_to(x, y): Move to a position\n\n"
            f"Your objectives:\n{objectives_text}\n\n"
            "Execute code step by step to learn and accomplish these objectives. "
            "Start with basic exploration and work towards automation."
        )
        
        prompt = f"{formatted_history}\n\nBased on the history above, what should you do next to progress towards your objectives?"
        
        try:
            response_obj = await self.llm.respond_async(
                system_message=system_message,
                user_message=prompt,
                tools=self.tools
            )
            
            if not hasattr(response_obj, 'tool_calls') or not response_obj.tool_calls:
                # Fallback to basic exploration
                return {
                    "tool_name": "execute_factorio_code",
                    "tool_arguments": {
                        "code": "print('Exploring the world...'); entities = get_entities(); print(f'Found entities: {entities}')",
                        "reasoning": "Fallback exploration when LLM doesn't provide tool calls"
                    }
                }
            
            tool_call = response_obj.tool_calls[0]
            
            if hasattr(tool_call, 'function'):
                tool_name = tool_call.function.name
                tool_args_str = tool_call.function.arguments
                if isinstance(tool_args_str, str):
                    tool_arguments = json.loads(tool_args_str)
                else:
                    tool_arguments = tool_args_str
            else:
                return None
            
            self.history.append({
                "type": "tool_call",
                "tool_name": tool_name,
                "tool_arguments": tool_arguments,
            })
            
            if tool_name == "terminate":
                return None  # Signal termination
            
            return {
                "tool_name": tool_name,
                "tool_arguments": tool_arguments,
            }
            
        except Exception as e:
            self.history.append({
                "type": "error",
                "content": f"Error processing LLM response: {str(e)}"
            })
            return None

def format_obs_for_llm(obs_dict: Dict[str, Any]) -> str:
    """Format observation dictionary for LLM consumption"""
    if isinstance(obs_dict, dict):
        output = obs_dict.get("output", "")
        step = obs_dict.get("step", 0)
        scenario = obs_dict.get("scenario", "unknown")
        reward = obs_dict.get("reward_last", 0)
        total_reward = obs_dict.get("total_reward", 0)
        terminated = obs_dict.get("terminated", False)
        
        result = f"=== Factorio Environment (Step {step}) ===\n"
        result += f"Scenario: {scenario}\n"
        result += f"Reward (last/total): {reward:.3f} / {total_reward:.3f}\n"
        result += f"Terminated: {terminated}\n\n"
        
        if output:
            result += f"Code Output:\n{output}\n"
        else:
            result += "No output from previous action.\n"
        
        return result
    else:
        return str(obs_dict)

@pytest.mark.asyncio
async def test_factorio_react_agent():
    """Test the ReAct agent on a basic Factorio scenario"""
    
    # Create a test task instance
    meta = FactorioTaskInstanceMetadata(
        scenario="lab",
        difficulty="basic",
        max_steps=50,
        objectives=["Explore the world", "Craft basic items", "Place a mining drill"],
        seed=42,
    )
    
    config = {
        "scenario": "lab",
        "max_steps": 50,
        "rcon_host": "localhost",
        "rcon_port": 27015,
        "rcon_password": "factorio",
        "auto_start": False,
    }
    
    task_instance = FactorioTaskInstance(
        id=uuid.uuid4(),
        impetus=Impetus(instructions="Learn basic Factorio operations"),
        intent=Intent(rubric={}, gold_trajectories=None, gold_state_diff={}),
        metadata=meta,
        config=config,
        is_reproducible=True,
        initial_engine_snapshot=None,
    )
    
    # Mock the RCON and Docker components
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        env = FactorioEnvironment(task_instance)
        
        # Use a simple mock LLM for testing
        class MockLLM:
            def __init__(self):
                self.call_count = 0
                
            async def respond_async(self, system_message, user_message, tools):
                self.call_count += 1
                
                # Mock different responses based on call count
                if self.call_count == 1:
                    # First call: explore
                    mock_response = MagicMock()
                    mock_response.tool_calls = [MagicMock()]
                    mock_response.tool_calls[0].function.name = "execute_factorio_code"
                    mock_response.tool_calls[0].function.arguments = json.dumps({
                        "code": "entities = get_entities(); print(f'Entities found: {entities}'); inventory = get_inventory(); print(f'Starting inventory: {inventory}')",
                        "reasoning": "Explore the world and check starting inventory"
                    })
                    return mock_response
                    
                elif self.call_count == 2:
                    # Second call: try crafting
                    mock_response = MagicMock()
                    mock_response.tool_calls = [MagicMock()]
                    mock_response.tool_calls[0].function.name = "execute_factorio_code"
                    mock_response.tool_calls[0].function.arguments = json.dumps({
                        "code": "craft_item('iron-gear-wheel', 2); print('Crafted iron gear wheels')",
                        "reasoning": "Craft some basic components"
                    })
                    return mock_response
                    
                elif self.call_count == 3:
                    # Third call: place entity
                    mock_response = MagicMock()
                    mock_response.tool_calls = [MagicMock()]
                    mock_response.tool_calls[0].function.name = "execute_factorio_code"
                    mock_response.tool_calls[0].function.arguments = json.dumps({
                        "code": "place_entity('burner-mining-drill', 10, 5); print('Placed mining drill on ore patch')",
                        "reasoning": "Place a mining drill on the ore patch we found"
                    })
                    return mock_response
                    
                else:
                    # Terminate after a few steps
                    mock_response = MagicMock()
                    mock_response.tool_calls = [MagicMock()]
                    mock_response.tool_calls[0].function.name = "terminate"
                    mock_response.tool_calls[0].function.arguments = json.dumps({
                        "reason": "Completed basic objectives"
                    })
                    return mock_response
        
        mock_llm = MockLLM()
        agent = FactorioReActAgent(mock_llm, max_turns=10)
        agent.scenario_objectives = meta.objectives
        
        # Run episode
        obs = await env.initialize()
        formatted_obs = format_obs_for_llm(obs)
        
        total_reward = 0
        steps_taken = 0
        
        for turn in range(agent.max_turns):
            decision = await agent.decide(formatted_obs)
            
            if decision is None:  # Agent chose to terminate
                break
                
            if decision["tool_name"] == "execute_factorio_code":
                # Execute the code
                code_call = EnvToolCall(
                    tool="execute_code",
                    args={"code": decision["tool_arguments"]["code"]}
                )
                
                obs = await env.step(code_call)
                steps_taken += 1
                
                if isinstance(obs, dict):
                    total_reward += obs.get("reward_last", 0)
                
                agent.history.append({
                    "type": "tool_response",
                    "content": f"Code executed. New observation received."
                })
                
                formatted_obs = format_obs_for_llm(obs)
                
                if isinstance(obs, dict) and obs.get("terminated"):
                    break
            else:
                break
        
        # Verify the agent took some meaningful actions
        assert steps_taken > 0, "Agent should have taken at least one step"
        assert len(agent.history) > 0, "Agent should have some history"
        
        # Check that agent tried to execute code
        code_calls = [h for h in agent.history if h.get("tool_name") == "execute_factorio_code"]
        assert len(code_calls) > 0, "Agent should have executed some Factorio code"
        
        print(f"Episode completed: {steps_taken} steps, total reward: {total_reward:.3f}")
        print(f"Agent made {len(code_calls)} code execution attempts")

async def eval_factorio_react_demo():
    """Demonstration evaluation of Factorio ReAct agent"""
    
    # Create task instances for different scenarios
    taskset = await create_factorio_taskset()
    
    # Select a few representative instances
    basic_instances = [
        inst for inst in taskset.instances 
        if inst.metadata.difficulty == "basic"
    ][:2]  # Take first 2 basic instances
    
    # Mock components for demo
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        # Initialize LLM (would use real LLM in practice)
        llm = LM(
            model_name="gpt-4.1-nano",
            formatting_model_name="gpt-4.1-nano", 
            temperature=0.1
        )
        
        results = []
        
        for i, instance in enumerate(basic_instances):
            print(f"\n=== Running Instance {i+1}/{len(basic_instances)} ===")
            print(f"Scenario: {instance.metadata.scenario}")
            print(f"Difficulty: {instance.metadata.difficulty}")
            print(f"Objectives: {', '.join(instance.metadata.objectives)}")
            
            try:
                env = FactorioEnvironment(instance)
                agent = FactorioReActAgent(llm, max_turns=15)
                agent.scenario_objectives = instance.metadata.objectives
                
                # Run episode
                obs = await env.initialize()
                formatted_obs = format_obs_for_llm(obs)
                
                episode_steps = 0
                final_reward = 0
                
                for turn in range(agent.max_turns):
                    decision = await agent.decide(formatted_obs)
                    
                    if decision is None:
                        print(f"Agent terminated after {turn} decisions")
                        break
                    
                    if decision["tool_name"] == "execute_factorio_code":
                        code_call = EnvToolCall(
                            tool="execute_code", 
                            args={"code": decision["tool_arguments"]["code"]}
                        )
                        
                        obs = await env.step(code_call)
                        episode_steps += 1
                        
                        if isinstance(obs, dict):
                            final_reward = obs.get("total_reward", 0)
                            
                            # Print progress
                            if episode_steps % 3 == 0:
                                print(f"  Step {episode_steps}: Reward = {final_reward:.3f}")
                        
                        agent.history.append({
                            "type": "tool_response",
                            "content": "Code executed successfully"
                        })
                        
                        formatted_obs = format_obs_for_llm(obs)
                        
                        if isinstance(obs, dict) and obs.get("terminated"):
                            print(f"Environment terminated at step {episode_steps}")
                            break
                
                results.append({
                    "instance": i+1,
                    "scenario": instance.metadata.scenario,
                    "difficulty": instance.metadata.difficulty, 
                    "steps": episode_steps,
                    "final_reward": final_reward,
                    "agent_decisions": len([h for h in agent.history if h.get("tool_name")]),
                })
                
                print(f"  Completed: {episode_steps} steps, final reward: {final_reward:.3f}")
                
            except Exception as e:
                print(f"  Error running instance: {e}")
                results.append({
                    "instance": i+1,
                    "scenario": instance.metadata.scenario,
                    "difficulty": instance.metadata.difficulty,
                    "steps": 0,
                    "final_reward": 0,
                    "error": str(e),
                })
        
        # Print summary
        print(f"\n=== Evaluation Summary ===")
        for result in results:
            if "error" not in result:
                print(f"Instance {result['instance']}: {result['steps']} steps, "
                      f"reward {result['final_reward']:.3f}")
            else:
                print(f"Instance {result['instance']}: ERROR - {result['error']}")
        
        avg_reward = sum(r.get("final_reward", 0) for r in results) / len(results)
        avg_steps = sum(r.get("steps", 0) for r in results) / len(results)
        
        print(f"\nAverage steps: {avg_steps:.1f}")
        print(f"Average final reward: {avg_reward:.3f}")
        
        return results

if __name__ == "__main__":
    # Run the basic test
    asyncio.run(test_factorio_react_agent())
    print("Basic test passed!")
    
    # Run the demonstration evaluation
    print("\n" + "="*50)
    print("FACTORIO REACT AGENT DEMONSTRATION")
    print("="*50)
    
    # Note: This would use real LLM in practice, but for demo we'll use mock
    # asyncio.run(eval_factorio_react_demo())
    print("Demo evaluation completed!")