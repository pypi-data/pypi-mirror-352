"""
Clean ReAct agent implementation for the evaluation framework.

Environment-agnostic ReAct agent that can work across different environments.
"""

import json
from typing import Union, Dict, Any, List, Optional
from .base import BaseAgent


class ReActAgent(BaseAgent):
    """Clean ReAct agent implementation."""
    
    def __init__(self, model_name: str = "gpt-4.1-nano", max_turns: int = 50):
        super().__init__(model_name)
        self.max_turns = max_turns
        self.turn_count = 0
        self._llm = None
    
    async def _get_llm(self):
        """Lazy load LLM to avoid import issues."""
        if self._llm is None:
            try:
                from synth_ai.zyk import LM
                self._llm = LM(
                    model_name=self.model_name, 
                    formatting_model_name=self.model_name,
                    temperature=0.0
                )
            except ImportError:
                raise ImportError(
                    "ReAct agent requires synth_ai.zyk package for LLM functionality"
                )
        return self._llm
    
    async def reset(self) -> None:
        """Reset agent state for a new episode."""
        await super().reset()
        self.turn_count = 0
    
    async def step(self, observation: str) -> Union[str, Dict[str, Any]]:
        """Take a ReAct step given an observation."""
        if self.is_terminated:
            return {"action": "terminate", "reason": "Already terminated"}
        
        self.turn_count += 1
        self.add_to_history("observation", observation)
        
        # Check turn limit
        if self.turn_count >= self.max_turns:
            self.request_termination("Maximum turns reached")
            return {"action": "terminate", "reason": "Maximum turns reached"}
        
        # Get LLM
        llm = await self._get_llm()
        
        # Build prompt
        prompt = self._build_react_prompt(observation)
        
        try:
            # Get response from LLM with tools
            tools = self._get_available_tools()
            
            response = await llm.respond_async(
                system_message=self._get_system_message(),
                user_message=prompt,
                tools=tools
            )
            
            # Parse response and extract action
            action = self._parse_response(response)
            self.add_to_history("action", action)
            
            return action
            
        except Exception as e:
            self.request_termination(f"Error in LLM response: {e}")
            return {"action": "terminate", "reason": f"Error: {e}"}
    
    def _build_react_prompt(self, observation: str) -> str:
        """Build ReAct prompt with history."""
        prompt_parts = []
        
        # Add recent history
        for entry in self.history[-10:]:  # Last 10 entries
            if entry["type"] == "observation":
                prompt_parts.append(f"OBSERVATION: {entry['content']}")
            elif entry["type"] == "action":
                action_str = json.dumps(entry["content"]) if isinstance(entry["content"], dict) else str(entry["content"])
                prompt_parts.append(f"ACTION: {action_str}")
        
        # Add current observation
        prompt_parts.append(f"OBSERVATION: {observation}")
        
        # Add reasoning prompt
        prompt_parts.append(
            "Based on the observation and history, think step by step about what to do next. "
            "Then use one of the available tools to take an action."
        )
        
        return "\n\n".join(prompt_parts)
    
    def _get_system_message(self) -> str:
        """Get system message for the agent."""
        return (
            "You are a helpful assistant that can interact with environments to solve tasks. "
            "Use the available tools to take actions. Think through your reasoning step by step. "
            "When you believe the task is complete or you're stuck, use the terminate tool."
        )
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for the agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "interact",
                    "description": "Interact with the environment by taking an action",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The action to take (environment-specific)"
                            },
                            "reasoning": {
                                "type": "string", 
                                "description": "Your reasoning for taking this action"
                            }
                        },
                        "required": ["action", "reasoning"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "terminate",
                    "description": "Terminate the episode",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Reason for termination"
                            }
                        },
                        "required": ["reason"]
                    }
                }
            }
        ]
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse LLM response and extract action."""
        # Check if response has tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]  # Take first tool call
            
            # Handle both dict and object formats
            if isinstance(tool_call, dict):
                function_name = tool_call['function']['name']
                function_arguments = tool_call['function']['arguments']
            else:
                function_name = tool_call.function.name
                function_arguments = tool_call.function.arguments
            
            try:
                args = json.loads(function_arguments)
            except json.JSONDecodeError:
                args = {"error": "Failed to parse tool arguments"}
            
            if function_name == "terminate":
                self.request_termination(args.get("reason", "Termination requested"))
                return {"action": "terminate", "reason": args.get("reason", "Termination requested")}
            elif function_name == "interact":
                return {
                    "action": args.get("action", "no_action"),
                    "reasoning": args.get("reasoning", "No reasoning provided")
                }
        
        # Fallback: try to extract action from response content
        if hasattr(response, 'content'):
            content = response.content.lower()
            if "terminate" in content or "stop" in content or "done" in content:
                self.request_termination("Termination indicated in response")
                return {"action": "terminate", "reason": "Termination indicated in response"}
        
        # Default action if parsing fails
        return {"action": "no_action", "reasoning": "Failed to parse response"}


class SimpleCrafterAgent(ReActAgent):
    """Crafter-specific ReAct agent with knowledge of Crafter actions."""
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get Crafter-specific tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "crafter_action",
                    "description": "Take a Crafter action",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Crafter action name (e.g., 'move_up', 'place_stone', 'do')",
                                "enum": [
                                    "noop", "move_left", "move_right", "move_up", "move_down",
                                    "do", "sleep", "place_stone", "place_table", "place_furnace",
                                    "place_plant", "make_wood_pickaxe", "make_stone_pickaxe",
                                    "make_iron_pickaxe", "make_wood_sword", "make_stone_sword",
                                    "make_iron_sword"
                                ]
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Your reasoning for this action"
                            }
                        },
                        "required": ["action", "reasoning"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "terminate",
                    "description": "Terminate the episode",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Reason for termination"
                            }
                        },
                        "required": ["reason"]
                    }
                }
            }
        ]
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse response for Crafter actions."""
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            
            # Handle both dict and object formats
            if isinstance(tool_call, dict):
                function_name = tool_call['function']['name']
                function_arguments = tool_call['function']['arguments']
            else:
                function_name = tool_call.function.name
                function_arguments = tool_call.function.arguments
            
            try:
                args = json.loads(function_arguments)
            except json.JSONDecodeError:
                args = {"action": "noop", "reasoning": "Failed to parse arguments"}
            
            if function_name == "terminate":
                self.request_termination(args.get("reason", "Termination requested"))
                return {"action": "terminate", "reason": args.get("reason", "Termination requested")}
            elif function_name == "crafter_action":
                return {
                    "action": args.get("action", "noop"),
                    "reasoning": args.get("reasoning", "No reasoning provided")
                }
        
        # Fallback
        return {"action": "noop", "reasoning": "Failed to parse response"} 


class SimpleSokobanAgent(ReActAgent):
    """Sokoban-specific ReAct agent with knowledge of Sokoban actions."""
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get Sokoban-specific tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "sokoban_action",
                    "description": "Take a Sokoban action",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "integer",
                                "description": "Sokoban action number: 1=Up, 2=Down, 3=Left, 4=Right",
                                "enum": [1, 2, 3, 4]
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Your reasoning for this action"
                            }
                        },
                        "required": ["action", "reasoning"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "terminate",
                    "description": "Terminate the episode",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Reason for termination"
                            }
                        },
                        "required": ["reason"]
                    }
                }
            }
        ]
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse response for Sokoban actions."""
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            
            # Handle both dict and object formats
            if isinstance(tool_call, dict):
                function_name = tool_call['function']['name']
                function_arguments = tool_call['function']['arguments']
            else:
                function_name = tool_call.function.name
                function_arguments = tool_call.function.arguments
            
            try:
                args = json.loads(function_arguments)
            except json.JSONDecodeError:
                args = {"action": 1, "reasoning": "Failed to parse arguments"}
            
            if function_name == "terminate":
                self.request_termination(args.get("reason", "Termination requested"))
                return {"action": "terminate", "reason": args.get("reason", "Termination requested")}
            elif function_name == "sokoban_action":
                return {
                    "action": args.get("action", 1),  # Default to up
                    "reasoning": args.get("reasoning", "No reasoning provided")
                }
        
        # Fallback
        return {"action": 1, "reasoning": "Failed to parse response"}  # Default to up
    
    def _get_system_message(self) -> str:
        """Get Sokoban-specific system message."""
        return (
            "You are playing Sokoban, a puzzle game where you push boxes onto target locations. "
            "The grid shows: # (walls), _ (floor), O (targets), X (boxes), P (player), √ (box on target), S (player on target). "
            "Your goal is to push all boxes (X) onto targets (O) to win. "
            "You can move up (1), down (2), left (3), or right (4). "
            "Think strategically - boxes can only be pushed, not pulled, so avoid trapping them. "
            "Use the sokoban_action tool to move, and terminate when done or stuck."
        ) 