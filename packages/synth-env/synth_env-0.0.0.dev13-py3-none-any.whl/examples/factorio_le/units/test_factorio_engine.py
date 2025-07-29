"""
test_factorio_engine.py - Unit tests for FactorioEngine

Tests the core engine functionality including state management,
code execution, and RCON integration.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from examples.factorio_le.engine import (
    FactorioEngine,
    FactorioRCON,
    FactorioTools,
    FactorioEngineSnapshot,
    FactorioPublicState,
    FactorioPrivateState,
)
from examples.factorio_le.taskset import FactorioTaskInstance, FactorioTaskInstanceMetadata
from tasks.core import Impetus, Intent

def create_test_task_instance():
    """Create a minimal task instance for testing"""
    config = {
        "scenario": "lab",
        "max_steps": 100,
        "rcon_host": "localhost", 
        "rcon_port": 27015,
        "rcon_password": "test",
        "auto_start": False,
    }
    
    meta = FactorioTaskInstanceMetadata(
        scenario="lab",
        difficulty="test",
        max_steps=100,
        objectives=["test"],
        seed=42,
    )
    
    return FactorioTaskInstance(
        id=uuid4(),
        impetus=Impetus(instructions="test"),
        intent=Intent(rubric={}, gold_trajectories=None, gold_state_diff={}),
        metadata=meta,
        config=config,
        is_reproducible=True,
        initial_engine_snapshot=None,
    )

class MockRCON:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.connected = True
        self.commands_sent = []
    
    def connect(self):
        return True
    
    def send_command(self, command):
        self.commands_sent.append(command)
        # Return mock responses for different commands
        if "find_entities" in command:
            return '[{"name": "player", "position": {"x": 0, "y": 0}}]'
        elif "inventory" in command:
            return '{"iron-plate": 10, "copper-plate": 5}'
        elif "production_statistics" in command:
            return '{"iron-plate": 100}'
        else:
            return "Command executed"
    
    def close(self):
        self.connected = False

@pytest.mark.asyncio
async def test_engine_initialization():
    """Test basic engine initialization"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'):
        engine = FactorioEngine(task_instance)
        
        assert engine.scenario_name == "lab"
        assert engine.max_steps == 100
        assert engine.rcon_host == "localhost"
        assert engine.rcon_port == 27015
        assert engine.step_count == 0
        assert engine._total_reward == 0.0

@pytest.mark.asyncio 
async def test_engine_reset():
    """Test engine reset functionality"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        priv, pub = await engine._reset_engine()
        
        assert isinstance(priv, FactorioPrivateState)
        assert isinstance(pub, FactorioPublicState)
        assert priv.total_reward_episode == 0.0
        assert pub.step_count == 0
        assert pub.scenario_name == "lab"

@pytest.mark.asyncio
async def test_engine_step():
    """Test engine step execution"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        await engine._reset_engine()
        
        # Execute simple code
        code = "result = 2 + 2\nprint(f'Result: {result}')"
        priv, pub = await engine._step_engine(code)
        
        assert isinstance(priv, FactorioPrivateState)
        assert isinstance(pub, FactorioPublicState)
        assert pub.step_count == 1
        assert "Result: 4" in pub.last_code_output

@pytest.mark.asyncio
async def test_code_execution_with_error():
    """Test code execution with syntax errors"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        await engine._reset_engine()
        
        # Execute invalid code
        code = "invalid syntax!!!"
        priv, pub = await engine._step_engine(code)
        
        assert len(pub.last_error_output) > 0
        assert "SyntaxError" in pub.last_error_output

@pytest.mark.asyncio
async def test_namespace_persistence():
    """Test that variables persist across code executions"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        await engine._reset_engine()
        
        # Set a variable
        code1 = "my_var = 42"
        await engine._step_engine(code1)
        
        # Use the variable
        code2 = "print(f'Variable: {my_var}')"
        priv, pub = await engine._step_engine(code2)
        
        assert "Variable: 42" in pub.last_code_output

@pytest.mark.asyncio
async def test_factorio_tools_available():
    """Test that Factorio API tools are available in namespace"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        await engine._reset_engine()
        
        # Test calling a tool function
        code = "entities = get_entities()\nprint(f'Entities: {entities}')"
        priv, pub = await engine._step_engine(code)
        
        assert "Entities:" in pub.last_code_output

@pytest.mark.asyncio
async def test_engine_serialization():
    """Test engine state serialization"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        await engine._reset_engine()
        
        # Take a step
        await engine._step_engine("test_var = 'serialization'")
        
        # Serialize
        snapshot = await engine._serialize_engine()
        
        assert isinstance(snapshot, FactorioEngineSnapshot)
        assert snapshot.scenario_name == "lab"
        assert snapshot.step_count == 1
        assert snapshot.total_reward_snapshot == engine._total_reward

@pytest.mark.asyncio
async def test_engine_deserialization():
    """Test engine state deserialization"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        # Create and serialize an engine
        engine1 = FactorioEngine(task_instance)
        await engine1._reset_engine()
        await engine1._step_engine("test_var = 'persistence'")
        snapshot = await engine1._serialize_engine()
        
        # Deserialize to new engine
        engine2 = await FactorioEngine._deserialize_engine(snapshot, task_instance)
        
        assert engine2.step_count == engine1.step_count
        assert engine2._total_reward == engine1._total_reward
        assert engine2.scenario_name == engine1.scenario_name

def test_rcon_client():
    """Test RCON client functionality"""
    # Test initialization
    rcon = FactorioRCON("localhost", 27015, "test")
    assert rcon.host == "localhost"
    assert rcon.port == 27015
    assert rcon.password == "test"
    assert not rcon.connected

def test_factorio_tools():
    """Test Factorio tools functionality"""
    mock_rcon = MockRCON("localhost", 27015, "test")
    tools = FactorioTools(mock_rcon)
    
    # Test get_entities
    result = tools.get_entities()
    assert isinstance(result, str)
    
    # Test place_entity
    result = tools.place_entity("burner-mining-drill", 10, 10)
    assert isinstance(result, str)
    
    # Test craft_item
    result = tools.craft_item("iron-gear-wheel", 5)
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_reward_calculation():
    """Test reward calculation"""
    task_instance = create_test_task_instance()
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        await engine._reset_engine()
        
        initial_reward = engine._total_reward
        
        # Take a step (should get step penalty)
        priv, pub = await engine._step_engine("print('test')")
        
        # Reward should change (step penalty)
        assert engine._total_reward != initial_reward
        assert priv.reward_last_step < 0  # Step penalty

@pytest.mark.asyncio
async def test_termination_conditions():
    """Test termination and truncation conditions"""
    # Create task with very low max_steps for testing
    task_instance = create_test_task_instance()
    task_instance.config["max_steps"] = 2
    
    with patch('examples.factorio_le.engine.FactorioEngine._start_factorio_server'), \
         patch('examples.factorio_le.engine.FactorioRCON', MockRCON):
        
        engine = FactorioEngine(task_instance)
        engine.max_steps = 2
        await engine._reset_engine()
        
        # Take steps until truncation
        priv1, pub1 = await engine._step_engine("print('step 1')")
        assert not priv1.truncated
        
        priv2, pub2 = await engine._step_engine("print('step 2')")
        assert priv2.truncated  # Should be truncated at max_steps

if __name__ == "__main__":
    asyncio.run(test_engine_initialization())
    asyncio.run(test_engine_reset())
    asyncio.run(test_engine_step())
    asyncio.run(test_code_execution_with_error())
    asyncio.run(test_namespace_persistence())
    asyncio.run(test_factorio_tools_available())
    asyncio.run(test_engine_serialization())
    asyncio.run(test_engine_deserialization())
    test_rcon_client()
    test_factorio_tools()
    asyncio.run(test_reward_calculation())
    asyncio.run(test_termination_conditions())
    print("All engine tests passed!")