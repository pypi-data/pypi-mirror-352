"""
test_factorio_environment.py - Unit tests for Factorio Learning Environment

Tests the FactorioEnvironment integration including initialization, 
code execution, and state management.
"""

import asyncio
import json
from typing import Dict, Any
from uuid import uuid4
import pytest
from unittest.mock import Mock, patch

# App imports
from examples.factorio_le.environment import FactorioEnvironment
from examples.factorio_le.engine import FactorioEngineSnapshot
from examples.factorio_le.taskset import (
    FactorioTaskInstanceMetadata, 
    FactorioTaskInstance,
)
from environment.tools import EnvToolCall
from tasks.core import TaskInstance, Impetus, Intent

# Test fixture for basic Factorio task
BASIC_TASK_CONFIG = {
    "scenario": "lab",
    "max_steps": 50,
    "seed": 42,
    "rcon_host": "localhost",
    "rcon_port": 27015,
    "rcon_password": "factorio",
    "auto_start": False,  # Don't auto-start server in tests
}

class MockRCON:
    """Mock RCON client for testing"""
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.connected = True
        self.command_responses = {
            '/sc game.player.surface.find_entities()': '[{"name": "player", "position": {"x": 0, "y": 0}}]',
            '/sc game.player.get_main_inventory().get_contents()': '{"iron-plate": 10, "copper-plate": 5}',
            '/sc game.player.force.item_production_statistics.output_counts': '{"iron-plate": 100, "copper-plate": 50}',
        }
    
    def connect(self):
        return True
    
    def send_command(self, command):
        return self.command_responses.get(command, "Command executed successfully")
    
    def close(self):
        self.connected = False

def create_test_task_instance() -> FactorioTaskInstance:
    """Create a test task instance for Factorio"""
    meta = FactorioTaskInstanceMetadata(
        scenario="lab",
        difficulty="basic",
        max_steps=50,
        objectives=["Test basic operations"],
        seed=42,
    )
    
    return FactorioTaskInstance(
        id=uuid4(),
        impetus=Impetus(instructions="Test Factorio environment functionality"),
        intent=Intent(rubric={}, gold_trajectories=None, gold_state_diff={}),
        metadata=meta,
        config=BASIC_TASK_CONFIG,
        is_reproducible=True,
        initial_engine_snapshot=None,
    )

@pytest.mark.asyncio
async def test_environment_initialization():
    """Test basic environment initialization"""
    task_instance = create_test_task_instance()
    
    # Mock the RCON connection
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        
        # Initialize the environment
        obs = await env.initialize()
        
        # Check that we get an observation
        assert obs is not None
        if isinstance(obs, dict):
            assert "output" in obs or "step" in obs or "scenario" in obs

@pytest.mark.asyncio
async def test_environment_code_execution():
    """Test executing Python code in the environment"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        await env.initialize()
        
        # Test simple print statement
        code_call = EnvToolCall(
            tool="execute_code",
            args={"code": "print('Hello, Factorio!')"}
        )
        
        obs = await env.step(code_call)
        assert obs is not None
        
        if isinstance(obs, dict):
            output = obs.get("output", "")
            assert "Hello, Factorio!" in output

@pytest.mark.asyncio 
async def test_environment_tool_functions():
    """Test that Factorio API tools are available in code execution"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        await env.initialize()
        
        # Test using a tool function
        code_call = EnvToolCall(
            tool="execute_code", 
            args={"code": "inventory = get_inventory(); print(f'Inventory: {inventory}')"}
        )
        
        obs = await env.step(code_call)
        assert obs is not None
        
        if isinstance(obs, dict):
            output = obs.get("output", "")
            assert "Inventory:" in output

@pytest.mark.asyncio
async def test_environment_error_handling():
    """Test environment handles code errors gracefully"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        await env.initialize()
        
        # Test code with syntax error
        code_call = EnvToolCall(
            tool="execute_code",
            args={"code": "invalid syntax here!!!"}
        )
        
        obs = await env.step(code_call)
        assert obs is not None
        
        # Should get error information
        if isinstance(obs, dict):
            output = obs.get("output", "")
            assert len(output) > 0  # Should have some error output

@pytest.mark.asyncio
async def test_environment_state_persistence():
    """Test that variables persist across code executions"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        await env.initialize()
        
        # Set a variable
        code_call1 = EnvToolCall(
            tool="execute_code",
            args={"code": "my_variable = 42"}
        )
        await env.step(code_call1)
        
        # Use the variable
        code_call2 = EnvToolCall(
            tool="execute_code",
            args={"code": "print(f'Variable value: {my_variable}')"}
        )
        obs = await env.step(code_call2)
        
        if isinstance(obs, dict):
            output = obs.get("output", "")
            assert "Variable value: 42" in output

@pytest.mark.asyncio
async def test_environment_serialization():
    """Test environment state serialization and deserialization"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        await env.initialize()
        
        # Take a step
        code_call = EnvToolCall(
            tool="execute_code",
            args={"code": "test_var = 'serialization_test'"}
        )
        await env.step(code_call)
        
        # Serialize
        snapshot = await env._serialize_engine()
        assert isinstance(snapshot, FactorioEngineSnapshot)
        
        # Check snapshot contains expected data
        assert snapshot.scenario_name == "lab"
        assert snapshot.step_count >= 1

@pytest.mark.asyncio
async def test_environment_termination():
    """Test environment termination"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        await env.initialize()
        
        # Terminate environment
        obs = await env.terminate()
        assert obs is not None
        
        if isinstance(obs, dict):
            assert obs.get("terminated") == True

@pytest.mark.asyncio
async def test_environment_checkpoint():
    """Test environment checkpointing"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        await env.initialize()
        
        # Take a step
        code_call = EnvToolCall(
            tool="execute_code",
            args={"code": "checkpoint_var = 'test'"}
        )
        await env.step(code_call)
        
        # Create checkpoint
        checkpoint_obs = await env.checkpoint()
        assert checkpoint_obs is not None
        
        if isinstance(checkpoint_obs, dict):
            assert "engine_snapshot_data" in checkpoint_obs

@pytest.mark.asyncio 
async def test_tool_validation():
    """Test tool call validation"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        env = FactorioEnvironment(task_instance)
        
        # Test valid tool call
        valid_call = {"tool": "execute_code", "args": {"code": "print('test')"}}
        validated = env.validate_tool_calls(valid_call)
        assert validated.tool == "execute_code"
        assert validated.args["code"] == "print('test')"
        
        # Test invalid tool
        with pytest.raises(ValueError, match="Unknown tool"):
            invalid_call = {"tool": "invalid_tool", "args": {}}
            env.validate_tool_calls(invalid_call)

if __name__ == "__main__":
    asyncio.run(test_environment_initialization())
    asyncio.run(test_environment_code_execution())
    asyncio.run(test_environment_tool_functions())
    asyncio.run(test_environment_error_handling())
    asyncio.run(test_environment_state_persistence())
    asyncio.run(test_environment_serialization())
    asyncio.run(test_environment_termination())
    asyncio.run(test_environment_checkpoint())
    asyncio.run(test_tool_validation())
    print("All tests passed!")