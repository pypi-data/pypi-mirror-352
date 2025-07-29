"""Factorio Learning Environment TaskSet

This module defines task instances for the Factorio Learning Environment,
including different scenarios and difficulty levels.
"""

from tasks.core import (
    Task,
    TaskInstance,
    TaskInstanceMetadata,
    TaskInstanceMetadataFilter,
    TaskInstanceSet,
)
from uuid import uuid4, UUID
from tasks.core import SplitInfo, Impetus, Intent
from dataclasses import dataclass, asdict, fields
from typing import Dict, Any, List
import os

factorio_task = Task(
    global_premises="Factorio factory automation and resource management",
    global_constraints="Must use provided Python API to interact with the game world",
    global_objectives="Automate production lines and optimize resource throughput",
    shared_env_params={},
)

# Configuration parameters
NUM_INSTANCES_PER_SCENARIO = 5
SEED_START = 42

SCENARIO_CONFIGS = {
    "lab_basic": {
        "scenario": "lab",
        "max_steps": 100,
        "difficulty": "basic",
        "description": "Learn basic Factorio operations: mining, crafting, building",
        "impetus_prompt": """You are in a basic Factorio lab scenario. Your goal is to learn the fundamental operations:
1. Use get_entities() to see what's available in the world
2. Use get_inventory() to check your starting items
3. Try placing a burner-mining-drill on an ore patch with place_entity()
4. Experiment with crafting basic items using craft_item()

Available functions:
- get_entities(): List entities in the world
- place_entity(entity_name, x, y, direction=0): Place an entity
- craft_item(item_name, count=1): Craft items
- get_inventory(): Get your inventory contents
- get_production_stats(): Get production statistics
- move_to(x, y): Move to position""",
        "objectives": ["Place a mining drill", "Craft basic items", "Explore the world"],
    },
    "lab_intermediate": {
        "scenario": "lab",
        "max_steps": 200,
        "difficulty": "intermediate", 
        "description": "Build a simple automation setup",
        "impetus_prompt": """You are in an intermediate Factorio lab scenario. Your goal is to create a basic automation setup:
1. Set up mining operations for both iron and copper ore
2. Build furnaces to smelt ore into plates
3. Create a simple assembly line for basic components
4. Automate the production of iron gears and copper cables

Focus on building a sustainable production chain that can operate continuously.""",
        "objectives": ["Setup mining and smelting", "Build assembly line", "Automate basic production"],
    },
    "lab_advanced": {
        "scenario": "lab", 
        "max_steps": 500,
        "difficulty": "advanced",
        "description": "Create complex automation with multiple production chains",
        "impetus_prompt": """You are in an advanced Factorio lab scenario. Your goal is to create sophisticated automation:
1. Build complex production chains for electronic circuits
2. Implement inserters and belts for automated transport
3. Create multiple parallel production lines
4. Optimize for maximum throughput and efficiency
5. Work towards producing science packs

This requires advanced planning and understanding of Factorio's automation systems.""",
        "objectives": ["Complex production chains", "Automated transport", "Science pack production"],
    },
    "open_world_exploration": {
        "scenario": "open_world",
        "max_steps": 300,
        "difficulty": "exploration",
        "description": "Explore and establish initial base in open world",
        "impetus_prompt": """You are in an open-world Factorio scenario. Your goal is exploration and base establishment:
1. Explore the world to find resource patches
2. Establish a main base location
3. Set up initial mining and production
4. Plan for expansion and growth
5. Handle the challenges of an unrestricted environment

You have complete freedom to choose your strategy and approach.""",
        "objectives": ["Explore the world", "Establish base", "Plan expansion"],
    },
    "open_world_scale": {
        "scenario": "open_world",
        "max_steps": 1000,
        "difficulty": "scaling",
        "description": "Scale up operations in open world environment",
        "impetus_prompt": """You are in an open-world Factorio scenario focused on scaling operations:
1. Build large-scale mining operations
2. Create massive production facilities
3. Implement efficient logistics networks
4. Optimize for high-throughput production
5. Work towards launching a rocket

This is a test of your ability to manage complex, large-scale automation systems.""",
        "objectives": ["Large-scale mining", "Massive production", "Rocket launch"],
    },
}

@dataclass
class FactorioTaskInstanceMetadata(TaskInstanceMetadata):
    scenario: str
    difficulty: str
    max_steps: int
    objectives: List[str]
    seed: int
    
@dataclass 
class FactorioTaskInstance(TaskInstance):
    async def serialize(self) -> dict:
        data = asdict(self)
        if "id" in data and isinstance(data["id"], UUID):
            data["id"] = str(data["id"])
        if "intent" in data and data["intent"] is not None:
            if "deterministic_eval_functions" in data["intent"]:
                data["intent"]["deterministic_eval_functions"] = []
        return data

    @classmethod
    async def deserialize(cls, data: dict) -> "FactorioTaskInstance":
        """Gracefully accept non-UUID ids"""
        if "id" in data:
            try:
                data["id"] = UUID(str(data["id"]))
            except (ValueError, TypeError, AttributeError):
                pass  # keep original string

        if "impetus" in data and isinstance(data["impetus"], dict):
            data["impetus"] = Impetus(**data["impetus"])

        if "intent" in data and isinstance(data["intent"], dict):
            intent_data = data["intent"]
            intent_data["deterministic_eval_functions"] = []
            if (
                "gold_trajectories" in intent_data
                and intent_data["gold_trajectories"] is not None
            ):
                pass
            data["intent"] = Intent(**intent_data)

        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = FactorioTaskInstanceMetadata(**data["metadata"])

        constructor_field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in constructor_field_names}

        return cls(**filtered_data)

async def create_factorio_taskset() -> TaskInstanceSet:
    """Generate Factorio task instances wrapped in a TaskInstanceSet."""
    instances = []
    current_seed = SEED_START

    for scenario_name, config in SCENARIO_CONFIGS.items():
        for i in range(NUM_INSTANCES_PER_SCENARIO):
            instance_id = uuid4()
            
            impetus = Impetus(instructions=config["impetus_prompt"])
            intent = Intent(
                rubric={
                    "objectives": config["objectives"],
                    "scenario": config["scenario"],
                    "difficulty": config["difficulty"]
                },
                gold_trajectories=None,
                gold_state_diff={},
            )
            metadata = FactorioTaskInstanceMetadata(
                scenario=config["scenario"],
                difficulty=config["difficulty"], 
                max_steps=config["max_steps"],
                objectives=config["objectives"],
                seed=current_seed,
            )

            # Create task instance config for the engine
            task_config = {
                "scenario": config["scenario"],
                "max_steps": config["max_steps"],
                "seed": current_seed,
                "rcon_host": "localhost",
                "rcon_port": 27015,
                "rcon_password": "factorio",
                "auto_start": True,
            }

            task_instance = FactorioTaskInstance(
                id=instance_id,
                impetus=impetus,
                intent=intent,
                metadata=metadata,
                config=task_config,
                is_reproducible=True,
                initial_engine_snapshot=None,
            )
            instances.append(task_instance)
            current_seed += 1

    # Define filters for dataset splits
    class ScenarioFilter(TaskInstanceMetadataFilter):
        def __init__(self, scenario):
            self.scenario = scenario

        def __call__(self, instance):
            if hasattr(instance.metadata, "scenario"):
                return instance.metadata.scenario == self.scenario
            return False

    class DifficultyFilter(TaskInstanceMetadataFilter):
        def __init__(self, difficulty):
            self.difficulty = difficulty

        def __call__(self, instance):
            if hasattr(instance.metadata, "difficulty"):
                return instance.metadata.difficulty == self.difficulty
            return False

    # Split: validation = lab scenarios, test = basic difficulty, rest = train
    val_filter = ScenarioFilter("lab")
    test_filter = DifficultyFilter("basic")
    
    val_ids = {inst.id for inst in instances if val_filter(inst)}
    # Remove anything already tagged as validation from test
    test_ids = {
        inst.id for inst in instances if test_filter(inst) and inst.id not in val_ids
    }
    
    split_info = SplitInfo(
        val_instance_ids=val_ids,
        test_instance_ids=test_ids,
        _is_split_defined=True,
    )

    return TaskInstanceSet(
        name="Factorio Learning Environment TaskSet",
        description="Code-execution based tasks for factory automation in Factorio.",
        instances=instances,
        split_info=split_info,
    )

# Example usage
if __name__ == "__main__":
    import asyncio, json
    
    NUM_INSTANCES_PER_SCENARIO = 2  # Reduce for testing
    OUTPUT_FILE_PATH = "dataset/instances.json"

    async def main():
        taskset = await create_factorio_taskset()

        serialized = await asyncio.gather(
            *(inst.serialize() for inst in taskset.instances)
        )

        output_dir = os.path.dirname(OUTPUT_FILE_PATH)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(OUTPUT_FILE_PATH, "w") as f:
            json.dump(serialized, f, indent=2)
        print(f"Serialized {len(serialized)} instances to {OUTPUT_FILE_PATH}")

        # Test deserialization
        with open(OUTPUT_FILE_PATH, "r") as f:
            read_serialized_data = json.load(f)

        deserialized = await asyncio.gather(
            *(FactorioTaskInstance.deserialize(data) for data in read_serialized_data)
        )
        print(f"Deserialized {len(deserialized)} instances.")

        if any(inst is None for inst in deserialized):
            print("Error: Deserialization returned None for some instances.")
            return

        # Print split information
        val_ids = taskset.split_info.val_instance_ids
        test_ids = taskset.split_info.test_instance_ids
        all_ids = {inst.id for inst in deserialized}
        train_ids = all_ids - val_ids - test_ids

        train = [inst for inst in deserialized if inst.id in train_ids]
        val = [inst for inst in deserialized if inst.id in val_ids]
        test = [inst for inst in deserialized if inst.id in test_ids]

        print(f"Train set ({len(train)} instances)")
        print(f"Val set ({len(val)} instances)")  
        print(f"Test set ({len(test)} instances)")
        
        # Print scenario breakdown
        scenarios = {}
        for inst in deserialized:
            scenario = inst.metadata.scenario
            scenarios[scenario] = scenarios.get(scenario, 0) + 1
        print(f"Scenarios: {scenarios}")

    asyncio.run(main())