"""
Beautiful Evaluation Framework for v1 Environments

This package provides a clean, reusable evaluation framework inspired by 
beautiful evaluation patterns. Features include:

- Rich progress tracking
- Pluggable verification systems  
- Environment-agnostic design
- Async evaluation with concurrency
- Beautiful result display and export

Example usage:
    from eval.core.evaluator import Evaluator
    from eval.adapters.crafter import CrafterAdapter
    
    evaluator = Evaluator(adapter=CrafterAdapter())
    results = await evaluator.run_evaluation(config)
"""

__version__ = "1.0.0" 