"""
Main evaluator for running beautiful evaluations on v1 environments.

Simple, clean evaluation that relies entirely on environment reward signals.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Type
from dataclasses import asdict

from .types import (
    EvalResult, 
    EvalConfig, 
    FilterCriteria, 
    EnvironmentAdapter, 
    Agent, 
    TaskInstance
)
from .display import BeautifulDisplay


class Evaluator:
    """Beautiful evaluator for v1 environments."""
    
    def __init__(
        self, 
        adapter: EnvironmentAdapter,
        agent_class: Type[Agent],
        display: Optional[BeautifulDisplay] = None
    ):
        self.adapter = adapter
        self.agent_class = agent_class
        self.display = display or BeautifulDisplay()
    
    async def run_evaluation(
        self, 
        config: EvalConfig,
        criteria: Optional[FilterCriteria] = None
    ) -> List[EvalResult]:
        """Run comprehensive evaluation with beautiful progress tracking."""
        
        # Display header
        self.display.display_header(
            "🧪 Beautiful Environment Evaluation",
            "Clean, async evaluation with progress tracking"
        )
        
        # Load and filter instances
        self.display.print_status("🔍 Loading and filtering instances...", "blue")
        
        if criteria is None:
            criteria = FilterCriteria()
        
        all_instances = await self.adapter.load_instances(FilterCriteria())  # Load all first
        filtered_instances = await self.adapter.load_instances(criteria)
        
        if not filtered_instances:
            self.display.print_error("No instances match the filtering criteria!")
            return []
        
        # Display filtering summary
        self.display.display_filter_summary(
            len(all_instances), 
            len(filtered_instances), 
            criteria
        )
        
        # Run evaluations
        total_evaluations = len(config.models) * len(filtered_instances)
        self.display.print_status(
            f"🚀 Running {total_evaluations} evaluations...", 
            "green"
        )
        
        results = []
        
        if config.enable_progress_tracking:
            progress = self.display.create_progress_bar()
            if progress:
                with progress:
                    results = await self._run_with_progress(
                        config, filtered_instances, progress
                    )
            else:
                results = await self._run_without_progress(config, filtered_instances)
        else:
            results = await self._run_without_progress(config, filtered_instances)
        
        # Display results
        if config.display_results:
            self.display.display_results_table(results)
        
        # Save results
        if config.save_results:
            output_file = config.output_file or f"eval_results_{int(time.time())}.json"
            self.display.save_results(results, output_file)
        
        self.display.print_success(
            f"Completed {len(results)}/{total_evaluations} evaluations"
        )
        
        return results
    
    async def _run_with_progress(
        self, 
        config: EvalConfig, 
        instances: List[TaskInstance],
        progress
    ) -> List[EvalResult]:
        """Run evaluations with Rich progress tracking."""
        
        # Create tasks for each model-instance combination
        eval_tasks = []
        progress_tasks = []
        
        for model_name in config.models:
            for instance in instances:
                task_id = progress.add_task(
                    f"[cyan]{model_name}[/cyan] - {instance.instance_id}", 
                    total=config.max_steps_per_episode
                )
                progress_tasks.append(task_id)
                
                eval_task = self._run_single_evaluation(
                    model_name, instance, config, progress, task_id
                )
                eval_tasks.append(eval_task)
        
        # Run with concurrency limit
        results = []
        semaphore = asyncio.Semaphore(config.concurrent_limit)
        
        async def run_with_semaphore(task):
            async with semaphore:
                return await task
        
        completed_tasks = await asyncio.gather(
            *[run_with_semaphore(task) for task in eval_tasks],
            return_exceptions=True
        )
        
        # Filter out exceptions
        for result in completed_tasks:
            if isinstance(result, EvalResult):
                results.append(result)
            elif isinstance(result, Exception):
                self.display.print_error(f"Evaluation failed: {result}")
        
        return results
    
    async def _run_without_progress(
        self, 
        config: EvalConfig, 
        instances: List[TaskInstance]
    ) -> List[EvalResult]:
        """Run evaluations without progress tracking."""
        
        eval_tasks = []
        
        for model_name in config.models:
            for instance in instances:
                eval_task = self._run_single_evaluation(
                    model_name, instance, config
                )
                eval_tasks.append(eval_task)
        
        # Run with concurrency limit
        semaphore = asyncio.Semaphore(config.concurrent_limit)
        
        async def run_with_semaphore(task):
            async with semaphore:
                return await task
        
        completed_tasks = await asyncio.gather(
            *[run_with_semaphore(task) for task in eval_tasks],
            return_exceptions=True
        )
        
        # Filter out exceptions
        results = []
        for result in completed_tasks:
            if isinstance(result, EvalResult):
                results.append(result)
            elif isinstance(result, Exception):
                self.display.print_error(f"Evaluation failed: {result}")
        
        return results
    
    async def _run_single_evaluation(
        self,
        model_name: str,
        instance: TaskInstance,
        config: EvalConfig,
        progress=None,
        task_id=None
    ) -> EvalResult:
        """Run a single evaluation episode."""
        
        run_id = f"{model_name}_{instance.instance_id}"
        start_time = time.time()
        
        # Initialize result
        result = EvalResult(
            run_id=run_id,
            model_name=model_name,
            instance_id=instance.instance_id,
            task_description=instance.description,
            success=False,
            final_score=0.0,
            steps_taken=0,
            duration_seconds=0.0,
            metadata={
                "token_count": self.adapter.estimate_token_count(instance)
            }
        )
        
        try:
            # Update progress
            if progress and task_id is not None:
                progress.update(task_id, description=f"[cyan]{model_name}[/cyan] - Starting...")
            
            # Create agent
            agent = self.agent_class(model_name=model_name)
            
            # Run episode through adapter
            result = await self.adapter.run_episode(
                instance, 
                agent, 
                max_steps=config.max_steps_per_episode
            )
            
            # Update basic info that might not be set by adapter
            result.run_id = run_id
            result.model_name = model_name
            result.duration_seconds = time.time() - start_time
            
            # Update progress to completion
            if progress and task_id is not None:
                progress.update(
                    task_id, 
                    description=f"[green]{model_name}[/green] - ✓ Complete",
                    completed=result.steps_taken,
                    total=max(result.steps_taken, 1)  # Avoid division by zero
                )
            
        except asyncio.TimeoutError:
            result.error_message = f"Timeout after {config.timeout_seconds}s"
            result.duration_seconds = time.time() - start_time
            
            if progress and task_id is not None:
                progress.update(
                    task_id, 
                    description=f"[yellow]{model_name}[/yellow] - ⏰ Timeout"
                )
                
        except Exception as e:
            result.error_message = str(e)
            result.duration_seconds = time.time() - start_time
            
            if progress and task_id is not None:
                progress.update(
                    task_id, 
                    description=f"[red]{model_name}[/red] - ✗ Failed"
                )
        
        return result


# Convenience function
def create_evaluator(
    adapter: EnvironmentAdapter, 
    agent_class: Type[Agent]
) -> Evaluator:
    """Create an Evaluator instance."""
    return Evaluator(adapter, agent_class) 