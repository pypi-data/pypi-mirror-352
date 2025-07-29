"""
test_factorio_taskset.py - Unit tests for Factorio taskset

Tests task instance creation, serialization, and taskset generation.
"""

import asyncio
import pytest
from uuid import UUID

from examples.factorio_le.taskset import (
    create_factorio_taskset,
    FactorioTaskInstance,
    FactorioTaskInstanceMetadata,
    SCENARIO_CONFIGS,
)
from tasks.core import TaskInstanceSet, Impetus, Intent

@pytest.mark.asyncio
async def test_create_taskset():
    """Test basic taskset creation"""
    taskset = await create_factorio_taskset()
    
    assert isinstance(taskset, TaskInstanceSet)
    assert taskset.name == "Factorio Learning Environment TaskSet"
    assert len(taskset.instances) > 0
    
    # Check that we have instances for all scenarios
    scenarios = set()
    for instance in taskset.instances:
        scenarios.add(instance.metadata.scenario)
    
    expected_scenarios = {"lab", "open_world"}
    assert expected_scenarios.issubset(scenarios)

@pytest.mark.asyncio
async def test_task_instance_creation():
    """Test individual task instance properties"""
    taskset = await create_factorio_taskset()
    instance = taskset.instances[0]
    
    assert isinstance(instance, FactorioTaskInstance)
    assert isinstance(instance.id, UUID)
    assert isinstance(instance.impetus, Impetus)
    assert isinstance(instance.intent, Intent)
    assert isinstance(instance.metadata, FactorioTaskInstanceMetadata)
    
    # Check metadata fields
    assert hasattr(instance.metadata, 'scenario')
    assert hasattr(instance.metadata, 'difficulty')
    assert hasattr(instance.metadata, 'max_steps')
    assert hasattr(instance.metadata, 'objectives')
    assert hasattr(instance.metadata, 'seed')
    
    # Check config exists
    assert hasattr(instance, 'config')
    assert isinstance(instance.config, dict)
    assert 'scenario' in instance.config
    assert 'max_steps' in instance.config

@pytest.mark.asyncio
async def test_scenario_coverage():
    """Test that all defined scenarios are included"""
    taskset = await create_factorio_taskset()
    
    # Count instances per scenario
    scenario_counts = {}
    for instance in taskset.instances:
        scenario = instance.metadata.scenario
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
    
    # Should have instances for both lab and open_world scenarios
    assert 'lab' in scenario_counts
    assert 'open_world' in scenario_counts
    assert scenario_counts['lab'] > 0
    assert scenario_counts['open_world'] > 0

@pytest.mark.asyncio
async def test_difficulty_levels():
    """Test that different difficulty levels are represented"""
    taskset = await create_factorio_taskset()
    
    difficulties = set()
    for instance in taskset.instances:
        difficulties.add(instance.metadata.difficulty)
    
    # Should have multiple difficulty levels
    expected_difficulties = {"basic", "intermediate", "advanced", "exploration", "scaling"}
    assert len(difficulties.intersection(expected_difficulties)) > 1

@pytest.mark.asyncio
async def test_task_serialization():
    """Test task instance serialization and deserialization"""
    taskset = await create_factorio_taskset()
    instance = taskset.instances[0]
    
    # Serialize
    serialized = await instance.serialize()
    assert isinstance(serialized, dict)
    assert 'id' in serialized
    assert 'impetus' in serialized
    assert 'intent' in serialized
    assert 'metadata' in serialized
    
    # Deserialize
    deserialized = await FactorioTaskInstance.deserialize(serialized)
    assert isinstance(deserialized, FactorioTaskInstance)
    assert deserialized.metadata.scenario == instance.metadata.scenario
    assert deserialized.metadata.difficulty == instance.metadata.difficulty

@pytest.mark.asyncio
async def test_split_info():
    """Test dataset split information"""
    taskset = await create_factorio_taskset()
    split_info = taskset.split_info
    
    assert split_info._is_split_defined
    assert len(split_info.val_instance_ids) > 0
    assert len(split_info.test_instance_ids) > 0
    
    # Check that validation set contains lab scenarios
    val_instances = [inst for inst in taskset.instances if inst.id in split_info.val_instance_ids]
    val_scenarios = {inst.metadata.scenario for inst in val_instances}
    assert 'lab' in val_scenarios
    
    # Check that test set contains basic difficulty
    test_instances = [inst for inst in taskset.instances if inst.id in split_info.test_instance_ids]
    test_difficulties = {inst.metadata.difficulty for inst in test_instances}
    assert 'basic' in test_difficulties

@pytest.mark.asyncio
async def test_config_consistency():
    """Test that configs are consistent with metadata"""
    taskset = await create_factorio_taskset()
    
    for instance in taskset.instances:
        # Config scenario should match metadata scenario
        assert instance.config['scenario'] == instance.metadata.scenario
        assert instance.config['max_steps'] == instance.metadata.max_steps
        
        # Should have required config fields
        required_fields = ['scenario', 'max_steps', 'rcon_host', 'rcon_port', 'rcon_password']
        for field in required_fields:
            assert field in instance.config

def test_scenario_configs():
    """Test that scenario configurations are well-formed"""
    for scenario_name, config in SCENARIO_CONFIGS.items():
        assert 'scenario' in config
        assert 'max_steps' in config
        assert 'difficulty' in config
        assert 'description' in config
        assert 'impetus_prompt' in config
        assert 'objectives' in config
        
        assert isinstance(config['max_steps'], int)
        assert config['max_steps'] > 0
        assert isinstance(config['objectives'], list)
        assert len(config['objectives']) > 0

@pytest.mark.asyncio
async def test_unique_seeds():
    """Test that each instance has a unique seed"""
    taskset = await create_factorio_taskset()
    
    seeds = set()
    for instance in taskset.instances:
        seed = instance.metadata.seed
        assert seed not in seeds, f"Duplicate seed found: {seed}"
        seeds.add(seed)

@pytest.mark.asyncio
async def test_impetus_instructions():
    """Test that impetus instructions are meaningful"""
    taskset = await create_factorio_taskset()
    
    for instance in taskset.instances:
        instructions = instance.impetus.instructions
        assert isinstance(instructions, str)
        assert len(instructions) > 50  # Should be substantial instructions
        assert 'Factorio' in instructions
        
        # Should contain some expected keywords based on scenario
        if instance.metadata.scenario == 'lab':
            assert any(word in instructions.lower() for word in ['basic', 'craft', 'mining', 'automation'])
        elif instance.metadata.scenario == 'open_world':
            assert any(word in instructions.lower() for word in ['explore', 'base', 'world', 'establish'])

@pytest.mark.asyncio
async def test_reproducibility_flags():
    """Test that instances are marked as reproducible"""
    taskset = await create_factorio_taskset()
    
    for instance in taskset.instances:
        assert instance.is_reproducible == True

if __name__ == "__main__":
    asyncio.run(test_create_taskset())
    asyncio.run(test_task_instance_creation())
    asyncio.run(test_scenario_coverage())
    asyncio.run(test_difficulty_levels())
    asyncio.run(test_task_serialization())
    asyncio.run(test_split_info())
    asyncio.run(test_config_consistency())
    test_scenario_configs()
    asyncio.run(test_unique_seeds())
    asyncio.run(test_impetus_instructions())
    asyncio.run(test_reproducibility_flags())
    print("All taskset tests passed!")