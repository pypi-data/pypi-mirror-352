#!/usr/bin/env python3
"""
Evaluation with Achievement Tracking

This script runs both Crafter and Sokoban evaluations with detailed achievement tracking.
"""

import asyncio
from typing import Dict, Any, List

from eval.core.evaluator import Evaluator
from eval.core.types import EvalConfig
from eval.core.filters import create_limit_filter
from eval.adapters.crafter import CrafterAdapter
from eval.adapters.sokoban import SokobanAdapter
from eval.agents.react import SimpleCrafterAgent, SimpleSokobanAgent


async def run_evaluation_with_achievements(
    env_name: str,
    adapter,
    agent_class,
    model: str = "gpt-4.1-mini",
    max_instances: int = 3,
    max_steps: int = 30
):
    """Run evaluation and show detailed achievement tracking."""
    
    print(f"\n🎮 === {env_name} Evaluation with {model} ===")
    
    # Create configuration
    config = EvalConfig(
        models=[model],
        max_steps_per_episode=max_steps,
        concurrent_limit=1,  # Sequential for clearer output
        timeout_seconds=300.0,
        save_results=True,
        output_file=f"{env_name.lower()}_achievements_{model.replace('.', '_')}.json"
    )
    
    # Create filtering criteria
    criteria = create_limit_filter(max_instances)
    
    # Create evaluator
    evaluator = Evaluator(
        adapter=adapter,
        agent_class=agent_class
    )
    
    try:
        # Run evaluation
        results = await evaluator.run_evaluation(config, criteria)
        
        print(f"\n🎉 {env_name} evaluation complete! Processed {len(results)} runs.")
        
        # Detailed results analysis
        total_score = 0
        total_steps = 0
        successes = 0
        
        print(f"\n📋 Detailed Results:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"\nRun {i}: {status}")
            print(f"  Instance: {result.instance_id}")
            print(f"  Score: {result.final_score:.3f}")
            print(f"  Steps: {result.steps_taken}")
            print(f"  Duration: {result.duration_seconds:.1f}s")
            
            # Show environment-specific achievements
            if env_name == "Crafter":
                # Look for achievement info in metadata or reward breakdown
                achievements_unlocked = result.metadata.get("achievements_unlocked", 0)
                achievements_status = result.metadata.get("achievements_status", {})
                
                # Also check the last step's info for achievements
                if result.reward_breakdown:
                    last_step_info = result.reward_breakdown[-1].get("info", {})
                    if "achievements_unlocked" in last_step_info:
                        achievements_unlocked = last_step_info["achievements_unlocked"]
                    if "achievements_status" in last_step_info:
                        achievements_status = last_step_info["achievements_status"]
                
                print(f"  🏆 Achievements: {achievements_unlocked}/22")
                
                if achievements_unlocked > 0 and achievements_status:
                    unlocked = [name for name, achieved in achievements_status.items() if achieved]
                    print(f"  🎯 Unlocked: {', '.join(unlocked[:5])}")  # Show first 5
            
            elif env_name == "Sokoban":
                if result.success:
                    print(f"  🎯 Puzzle solved!")
                else:
                    print(f"  📦 Puzzle not completed")
            
            # Track totals
            total_score += result.final_score
            total_steps += result.steps_taken
            if result.success:
                successes += 1
        
        # Summary statistics
        if results:
            avg_score = total_score / len(results)
            avg_steps = total_steps / len(results)
            success_rate = successes / len(results)
            
            print(f"\n📊 Summary Statistics:")
            print(f"  Success Rate: {success_rate:.1%} ({successes}/{len(results)})")
            print(f"  Average Score: {avg_score:.3f}")
            print(f"  Average Steps: {avg_steps:.1f}")
            
            if env_name == "Crafter":
                total_achievements = 0
                for result in results:
                    # Check metadata first
                    achievements = result.metadata.get("achievements_unlocked", 0)
                    # Check last step info if not in metadata
                    if achievements == 0 and result.reward_breakdown:
                        last_step_info = result.reward_breakdown[-1].get("info", {})
                        achievements = last_step_info.get("achievements_unlocked", 0)
                    total_achievements += achievements
                
                print(f"  Total Achievements: {total_achievements}")
                print(f"  Avg Achievements: {total_achievements / len(results):.1f}")
        
        return results
        
    except Exception as e:
        print(f"❌ {env_name} evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return []


async def main():
    """Run evaluations for both environments."""
    
    print("🚀 Starting Achievement-Focused Evaluations")
    print("=" * 60)
    
    # Test with both models
    models = ["gpt-4.1-mini", "gpt-4.1-nano"]
    
    for model in models:
        print(f"\n🤖 Testing with {model}")
        print("=" * 40)
        
        # Crafter evaluation
        crafter_results = await run_evaluation_with_achievements(
            "Crafter",
            CrafterAdapter(),
            SimpleCrafterAgent,
            model=model,
            max_instances=3,
            max_steps=50  # Give more steps for Crafter
        )
        
        # Sokoban evaluation  
        sokoban_results = await run_evaluation_with_achievements(
            "Sokoban",
            SokobanAdapter(),
            SimpleSokobanAgent,
            model=model,
            max_instances=3,
            max_steps=30  # Sokoban puzzles should be solvable in fewer steps
        )
        
        # Compare results
        print(f"\n🔄 Model Comparison for {model}:")
        print(f"  Crafter: {len([r for r in crafter_results if r.success])}/{len(crafter_results)} success")
        print(f"  Sokoban: {len([r for r in sokoban_results if r.success])}/{len(sokoban_results)} success")
    
    print(f"\n🎯 All evaluations complete!")


if __name__ == "__main__":
    asyncio.run(main()) 