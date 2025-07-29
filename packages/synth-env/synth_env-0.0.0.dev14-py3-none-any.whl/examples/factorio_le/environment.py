"""FactorioEnvironment — StatefulEnvironment wrapper for Factorio Learning Environment.

This environment provides a tool-based interface where agents can execute Python code
as actions in the Factorio world.
"""

from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel
import dataclasses

from examples.factorio_le.engine import (
    FactorioEngine,
    FactorioObservationCallable,
    FactorioPrivateState,
    FactorioPublicState,
    FactorioEngineSnapshot
)
from environment.shared_engine import GetObservationCallable, InternalObservation
from reproducibility.core import ReproducibleEnvironment
from stateful.core import StatefulEnvironment
from tasks.core import TaskInstance
from environment.tools import AbstractTool, EnvToolCall, ToolResult, TOOL_REGISTRY, register_tool

# --- Tool Definition ---

class FactorioCodeInput(BaseModel):
    """Input schema for executing Python code in Factorio"""
    code: str

class FactorioCodeTool(AbstractTool):
    """Tool for executing Python code in the Factorio environment"""
    name = "execute_code"
    description = "Executes Python code in the Factorio environment. The code can call Factorio API functions."
    call_schema = FactorioCodeInput
    result_schema = ToolResult

    def __init__(self, engine: FactorioEngine):
        self.engine = engine

    async def __call__(self, call: EnvToolCall) -> ToolResult:
        try:
            validated_args = self.call_schema(**call.args)
            priv_state, pub_state = await self.engine._step_engine(validated_args.code)
            return ToolResult(
                ok=True,
                payload={
                    "public": dataclasses.asdict(pub_state),
                    "private": dataclasses.asdict(priv_state),
                }
            )
        except Exception as e:
            # Create error state
            error_pub_state = FactorioPublicState(
                scenario_name=self.engine.scenario_name,
                step_count=self.engine.step_count,
                max_steps=self.engine.max_steps,
                last_code_output="",
                last_error_output=f"Tool execution error: {str(e)}",
                production_metrics={},
                is_server_running=False,
                error_info=str(e)
            )
            return ToolResult(
                ok=False,
                error=str(e),
                payload={"public": dataclasses.asdict(error_pub_state)},
            )

class FactorioEnvironment(StatefulEnvironment, ReproducibleEnvironment[FactorioEngine]):
    """Environment wrapper for the Factorio Learning Environment"""
    
    def __init__(
        self,
        task_instance: TaskInstance,
        custom_step_obs: Optional[GetObservationCallable] = None,
    ):
        self.name = "Factorio"
        self.task_instance = task_instance
        self.custom_step_observation_callable = custom_step_obs or FactorioObservationCallable()
        self.engine: FactorioEngine = FactorioEngine(task_instance)

        # Register the code execution tool
        self._code_tool = FactorioCodeTool(self.engine)
        if self._code_tool.name not in TOOL_REGISTRY:
            register_tool(self._code_tool)

    async def initialize(self) -> InternalObservation:
        """Initialize the environment and return initial observation"""
        priv, pub = await self.engine._reset_engine()
        return await self._to_observation(priv, pub, self.custom_step_observation_callable)

    async def terminate(self) -> InternalObservation:
        """Terminate the environment and return final observation"""
        # Get current state
        try:
            priv = FactorioPrivateState(
                reward_last_step=0.0,
                total_reward_episode=self.engine._total_reward,
                terminated=True,
                truncated=False,
                rcon_connected=False
            )
            pub = FactorioPublicState(
                scenario_name=self.engine.scenario_name,
                step_count=self.engine.step_count,
                max_steps=self.engine.max_steps,
                last_code_output="Environment terminated.",
                last_error_output="",
                production_metrics=self.engine.production_metrics.copy(),
                is_server_running=False
            )
        except Exception:
            # Fallback if engine state is corrupted
            priv = FactorioPrivateState(
                reward_last_step=0.0,
                total_reward_episode=0.0,
                terminated=True,
                truncated=False,
                rcon_connected=False
            )
            pub = FactorioPublicState(
                scenario_name="unknown",
                step_count=0,
                max_steps=1000,
                last_code_output="Environment terminated.",
                last_error_output="",
                production_metrics={},
                is_server_running=False
            )

        # Clean up resources
        self.engine.close()
        
        obs_dict = {"terminated": True, "message": "Factorio environment terminated."}
        return await self._to_observation(priv, pub, self.custom_step_observation_callable, extra_obs=obs_dict)

    def validate_tool_calls(self, tool_calls: Union[EnvToolCall, List[Dict[str, Any]], List[List[Dict[str, Any]]], Dict[str, Any]]) -> EnvToolCall:
        """Validate and normalize tool calls to a single EnvToolCall"""
        raw_call_data: Dict[str, Any]
        
        if isinstance(tool_calls, list):
            if not tool_calls:
                raise ValueError("Received empty list of tool calls.")
            first_item = tool_calls[0]
            if isinstance(first_item, list):
                if not first_item:
                    raise ValueError("Received empty inner list of tool calls.")
                raw_call_data = first_item[0]
            elif isinstance(first_item, dict):
                raw_call_data = first_item
            elif isinstance(first_item, EnvToolCall):
                agent_call = first_item
                if agent_call.tool != "execute_code":
                    raise ValueError(f"Unknown tool: {agent_call.tool}. Expected 'execute_code'.")
                return agent_call
            else:
                raise TypeError(f"Unexpected type in tool_calls list: {type(first_item)}")
        elif isinstance(tool_calls, dict):
            raw_call_data = tool_calls
        elif isinstance(tool_calls, EnvToolCall):
            if tool_calls.tool != "execute_code":
                raise ValueError(f"Unknown tool: {tool_calls.tool}. Expected 'execute_code'.")
            return tool_calls
        else:
            raise TypeError(f"Unexpected type for tool_calls: {type(tool_calls)}")

        if not isinstance(raw_call_data, dict):
            raise TypeError(f"Processed call data is not a dict: {type(raw_call_data)}")

        # Convert dict to EnvToolCall instance
        tool_name = raw_call_data.get("tool")
        tool_args = raw_call_data.get("args", {})
        if tool_name != "execute_code":
            raise ValueError(f"Unknown tool: {tool_name}. Expected 'execute_code'.")
        
        agent_call = EnvToolCall(tool=tool_name, args=tool_args)
        return agent_call

    async def step(self, tool_calls: Union[EnvToolCall, List[Dict[str, Any]], List[List[Dict[str, Any]]], Dict[str, Any]]) -> InternalObservation:
        """Execute a step with the given tool calls"""
        agent_call = self.validate_tool_calls(tool_calls)
        tool_result: ToolResult = await self._code_tool(agent_call)

        payload_dict = tool_result.payload
        if not tool_result.ok or not isinstance(payload_dict, dict):
            # Create error state
            priv_state = FactorioPrivateState(
                reward_last_step=-1.0,  # Penalty for error
                total_reward_episode=self.engine._total_reward,
                terminated=False,
                truncated=False,
                rcon_connected=False
            )
            pub_state = FactorioPublicState(
                scenario_name=self.engine.scenario_name,
                step_count=self.engine.step_count,
                max_steps=self.engine.max_steps,
                last_code_output="",
                last_error_output=tool_result.error or "Unknown error",
                production_metrics={},
                is_server_running=False,
                error_info=tool_result.error
            )
        else:
            # Extract states from successful tool result
            priv_dict = payload_dict.get("private")
            pub_dict = payload_dict.get("public")

            if priv_dict is None or pub_dict is None:
                # Fallback if payload structure is unexpected
                priv_state = FactorioPrivateState(
                    reward_last_step=0.0,
                    total_reward_episode=self.engine._total_reward,
                    terminated=False,
                    truncated=False,
                    rcon_connected=False
                )
                pub_state = FactorioPublicState(
                    scenario_name=self.engine.scenario_name,
                    step_count=self.engine.step_count,
                    max_steps=self.engine.max_steps,
                    last_code_output="Invalid tool result",
                    last_error_output="",
                    production_metrics={},
                    is_server_running=False,
                    error_info="Invalid tool result payload"
                )
            else:
                priv_state = FactorioPrivateState(**priv_dict)
                pub_state = FactorioPublicState(**pub_dict)
                if tool_result.error and hasattr(pub_state, 'error_info'):
                    pub_state.error_info = tool_result.error
        
        return await self._to_observation(priv_state, pub_state, self.custom_step_observation_callable)

    async def checkpoint(self) -> InternalObservation:
        """Create a checkpoint of the current environment state"""
        engine_snapshot: FactorioEngineSnapshot = await self.engine._serialize_engine()
        
        # Get current states for observation
        try:
            priv = FactorioPrivateState(
                reward_last_step=0.0,
                total_reward_episode=self.engine._total_reward,
                terminated=False,
                truncated=False,
                rcon_connected=self.engine.rcon_client.connected if self.engine.rcon_client else False
            )
            pub = FactorioPublicState(
                scenario_name=self.engine.scenario_name,
                step_count=self.engine.step_count,
                max_steps=self.engine.max_steps,
                last_code_output="Checkpoint created",
                last_error_output="",
                production_metrics=self.engine.production_metrics.copy(),
                is_server_running=self.engine.rcon_client.connected if self.engine.rcon_client else False
            )
        except Exception:
            # Fallback state
            priv = FactorioPrivateState(
                reward_last_step=0.0,
                total_reward_episode=0.0,
                terminated=False,
                truncated=False,
                rcon_connected=False
            )
            pub = FactorioPublicState(
                scenario_name="unknown",
                step_count=0,
                max_steps=1000,
                last_code_output="Checkpoint created",
                last_error_output="",
                production_metrics={},
                is_server_running=False
            )
        
        obs_data = await self._to_observation(priv, pub, self.custom_step_observation_callable)
        if isinstance(obs_data, dict):
            obs_data["engine_snapshot_data"] = engine_snapshot.model_dump()
        return obs_data

    async def _to_observation(
        self, 
        priv: FactorioPrivateState, 
        pub: FactorioPublicState,
        obs_cb: Optional[GetObservationCallable],
        extra_obs: Optional[Dict[str, Any]] = None
    ) -> InternalObservation:
        """Convert private and public states to observation"""
        active_obs_cb = obs_cb or FactorioObservationCallable()
        observation = await active_obs_cb.get_observation(pub, priv)
        if extra_obs and isinstance(observation, dict):
            observation.update(extra_obs)
        return observation

    async def _serialize_engine(self) -> FactorioEngineSnapshot:
        """Serialize the engine for reproducibility"""
        return await self.engine._serialize_engine()

    @classmethod
    async def _deserialize_engine(cls, snapshot: FactorioEngineSnapshot, task_instance: TaskInstance) -> "FactorioEnvironment":
        """Deserialize engine from snapshot"""
        eng = await FactorioEngine._deserialize_engine(snapshot, task_instance)
        env = cls(task_instance)
        env.engine = eng
        return env