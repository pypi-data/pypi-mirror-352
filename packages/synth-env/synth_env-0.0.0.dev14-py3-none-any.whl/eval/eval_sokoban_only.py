#!/usr/bin/env python3
"""
Quick Sokoban-only evaluation script.
"""

import asyncio
from eval.core.evaluator import Evaluator
from eval.core.types import EvalConfig, FilterCriteria
from eval.core.filters import create_limit_filter, create_difficulty_filter, combine_filters
from eval.adapters.sokoban import SokobanAdapter
from eval.agents.react import SimpleSokobanAgent

async def main():
    print("🎮 Running Sokoban Evaluation Only")
    print("=" * 50)
    
    # Create config for Sokoban only
    config = EvalConfig(
        models=["gpt-4.1-mini"],
        max_steps_per_episode=50,
        concurrent_limit=3,
        timeout_seconds=300.0,
        save_results=True,
        output_file="sokoban_simple_results.json"
    )
    
    # Create criteria - prefer easy instances
    criteria = combine_filters(
        create_difficulty_filter(["easy"]),
        create_limit_filter(3)
    )
    
    # Create evaluator
    evaluator = Evaluator(
        adapter=SokobanAdapter(),
        agent_class=SimpleSokobanAgent
    )
    
    print("🔍 Running Sokoban evaluation...")
    results = await evaluator.run_evaluation(config, criteria)
    
    print(f"\n🎯 Sokoban Results Summary")
    print("=" * 30)
    
    total_success = sum(1 for r in results if r.success)
    avg_score = sum(r.final_score for r in results) / len(results)
    avg_steps = sum(r.steps_taken for r in results) / len(results)
    
    print(f"  📊 Success Rate: {total_success}/{len(results)} ({total_success/len(results)*100:.1f}%)")
    print(f"  🎯 Average Score: {avg_score:.2f}")
    print(f"  👣 Average Steps: {avg_steps:.1f}")
    
    print(f"\n📋 Individual Results:")
    for i, result in enumerate(results, 1):
        status = "✅ SOLVED" if result.success else "❌ FAILED"
        print(f"  Run {i}: {status}")
        print(f"    Score: {result.final_score}")
        print(f"    Steps: {result.steps_taken}")
        print(f"    Duration: {result.duration_seconds:.1f}s")

if __name__ == "__main__":
    asyncio.run(main()) 