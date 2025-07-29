#!/usr/bin/env python3
"""
Beautiful Crafter Evaluation Example

This script demonstrates how to use the beautiful evaluation framework
with the Crafter Classic environment.

Usage:
    uvpm eval.examples.eval_crafter
"""

import asyncio
from typing import Dict, Any, Optional

from ..core.evaluator import Evaluator
from ..core.types import EvalConfig, FilterCriteria, DifficultyLevel
from ..core.filters import create_limit_filter, combine_filters
from ..adapters.crafter import CrafterAdapter
from ..agents.react import SimpleCrafterAgent


async def eval_crafter_simple(
    models: Optional[list] = None,
    max_instances: int = 5,
    max_steps: int = 50
) -> None:
    """Run a simple Crafter evaluation."""
    
    if models is None:
        models = ["gpt-4.1-mini"]
    
    print("🎮 Starting Beautiful Crafter Evaluation")
    
    # Create configuration
    config = EvalConfig(
        models=models,
        max_steps_per_episode=max_steps,
        concurrent_limit=2,  # Limit concurrent runs for stability
        timeout_seconds=300.0,
        save_results=True,
        output_file="crafter_eval_results.json"
    )
    
    # Create filtering criteria
    criteria = create_limit_filter(max_instances)
    
    # Create evaluator
    evaluator = Evaluator(
        adapter=CrafterAdapter(),
        agent_class=SimpleCrafterAgent
    )
    
    try:
        # Run evaluation
        results = await evaluator.run_evaluation(config, criteria)
        
        print(f"\n🎉 Evaluation complete! Processed {len(results)} runs.")
        
        # Print summary
        if results:
            success_rate = sum(1 for r in results if r.success) / len(results)
            avg_score = sum(r.final_score for r in results) / len(results)
            avg_steps = sum(r.steps_taken for r in results) / len(results)
            
            print(f"📊 Summary:")
            print(f"   Success Rate: {success_rate:.1%}")
            print(f"   Average Score: {avg_score:.2f}")
            print(f"   Average Steps: {avg_steps:.1f}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


async def eval_crafter_comprehensive(
    models: Optional[list] = None,
    max_instances: int = 20
) -> None:
    """Run a comprehensive Crafter evaluation with filtering."""
    
    if models is None:
        models = ["gpt-4.1-mini", "gpt-4.1-nano"]
    
    print("🚀 Starting Comprehensive Crafter Evaluation")
    
    # Create configuration
    config = EvalConfig(
        models=models,
        max_steps_per_episode=100,
        concurrent_limit=3,
        timeout_seconds=600.0,
        save_results=True,
        output_file="crafter_comprehensive_results.json"
    )
    
    # Create filtering criteria - limit instances but allow all difficulties
    criteria = FilterCriteria(
        max_instances=max_instances,
        # Could add token_range, difficulty_levels, etc. here
    )
    
    # Create evaluator
    evaluator = Evaluator(
        adapter=CrafterAdapter(),
        agent_class=SimpleCrafterAgent
    )
    
    try:
        # Run evaluation
        results = await evaluator.run_evaluation(config, criteria)
        
        print(f"\n🎉 Comprehensive evaluation complete!")
        
        # Detailed analysis
        if results:
            print("\n📈 Detailed Results by Model:")
            for model in config.models:
                model_results = [r for r in results if r.model_name == model]
                if model_results:
                    success_rate = sum(1 for r in model_results if r.success) / len(model_results)
                    avg_score = sum(r.final_score for r in model_results) / len(model_results)
                    avg_steps = sum(r.steps_taken for r in model_results) / len(model_results)
                    avg_duration = sum(r.duration_seconds for r in model_results) / len(model_results)
                    
                    print(f"\n{model}:")
                    print(f"  📝 Instances: {len(model_results)}")
                    print(f"  ✅ Success Rate: {success_rate:.1%}")
                    print(f"  🎯 Avg Score: {avg_score:.2f}")
                    print(f"  👣 Avg Steps: {avg_steps:.1f}")
                    print(f"  ⏱️  Avg Duration: {avg_duration:.1f}s")
                    
                    # Show some individual results
                    print(f"  📋 Sample Results:")
                    for r in model_results[:3]:  # Show first 3
                        status = "✅" if r.success else "❌"
                        print(f"    {status} {r.instance_id}: {r.final_score:.2f} score, {r.steps_taken} steps")
        
    except Exception as e:
        print(f"❌ Comprehensive evaluation failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point with different evaluation modes."""
    
    print("🎮 Beautiful Crafter Evaluation Framework")
    print("=" * 50)
    
    # Check if we have access to required packages
    try:
        from examples.crafter_classic.environment import CrafterClassicEnvironment
        print("✅ Crafter environment available")
    except ImportError:
        print("❌ Crafter environment not available - make sure you're in the right directory")
        return
    
    try:
        from synth_ai.zyk import LM
        print("✅ LLM package available")
    except ImportError:
        print("❌ LLM package not available - evaluation will fail")
        return
    
    print("\nChoose evaluation mode:")
    print("1. Simple evaluation (5 instances, 1 model)")
    print("2. Comprehensive evaluation (20 instances, 2 models)")
    print("3. Custom evaluation")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            await eval_crafter_simple()
        elif choice == "2":
            await eval_crafter_comprehensive()
        elif choice == "3":
            print("\n📝 Custom Evaluation Setup:")
            models_input = input("Models (comma-separated, default: gpt-4.1-nano): ").strip()
            models = [m.strip() for m in models_input.split(",")] if models_input else ["gpt-4.1-mini"]
            
            max_instances_input = input("Max instances (default: 10): ").strip()
            max_instances = int(max_instances_input) if max_instances_input.isdigit() else 10
            
            max_steps_input = input("Max steps per episode (default: 50): ").strip()
            max_steps = int(max_steps_input) if max_steps_input.isdigit() else 50
            
            await eval_crafter_simple(models, max_instances, max_steps)
        else:
            print("Invalid choice. Running simple evaluation as default.")
            await eval_crafter_simple()
    
    except KeyboardInterrupt:
        print("\n⚠️ Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # For direct execution
    asyncio.run(main()) 