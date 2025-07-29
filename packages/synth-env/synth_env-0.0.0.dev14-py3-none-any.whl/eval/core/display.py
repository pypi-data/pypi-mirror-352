"""
Beautiful display utilities using Rich for progress tracking and results.

Provides rich progress bars, tables, and formatted output for evaluation results.
"""

import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
        MofNCompleteColumn,
    )
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.align import Align
    from rich import box
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback console
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

from .types import EvalResult, FilterCriteria


class BeautifulDisplay:
    """Beautiful display manager using Rich library."""
    
    def __init__(self, console: Optional[Console] = None):
        if RICH_AVAILABLE:
            self.console = console or Console()
            self.rich_enabled = True
        else:
            self.console = Console()
            self.rich_enabled = False
    
    def create_progress_bar(self) -> Optional['Progress']:
        """Create a Rich progress bar if available."""
        if not self.rich_enabled:
            return None
        
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        )
    
    def display_header(self, title: str, description: str):
        """Display beautiful evaluation header."""
        if self.rich_enabled:
            panel = Panel.fit(
                f"[bold blue]{title}[/bold blue]\n[dim]{description}[/dim]",
                border_style="blue"
            )
            self.console.print("\n")
            self.console.print(panel)
        else:
            self.console.print(f"\n=== {title} ===")
            self.console.print(description)
    
    def display_filter_summary(
        self, 
        original_count: int, 
        filtered_count: int, 
        criteria: FilterCriteria
    ):
        """Display filtering summary."""
        if self.rich_enabled:
            # Create filtering criteria table
            filter_table = Table(title="🔍 Filtering Criteria", box=box.ROUNDED)
            filter_table.add_column("Criterion", style="cyan")
            filter_table.add_column("Value", style="yellow")
            
            # Token range
            if criteria.token_range != (0, float('inf')):
                token_display = f"{criteria.token_range[0]:,} - {criteria.token_range[1]:,}"
                if criteria.token_range[1] == float('inf'):
                    token_display = f"{criteria.token_range[0]:,}+"
                filter_table.add_row("Token Range", token_display)
            
            # Difficulty levels
            if criteria.difficulty_levels:
                diff_display = ", ".join(str(d.value) for d in criteria.difficulty_levels)
                filter_table.add_row("Difficulty", diff_display)
            
            # Max instances
            if criteria.max_instances:
                filter_table.add_row("Max Instances", str(criteria.max_instances))
            
            # Create results summary
            results_table = Table(title="📊 Filtering Results", box=box.ROUNDED)
            results_table.add_column("Metric", style="cyan")
            results_table.add_column("Count", style="green", justify="right")
            
            results_table.add_row("Original Instances", str(original_count))
            results_table.add_row("Filtered Instances", str(filtered_count))
            reduction_pct = (1 - filtered_count/original_count)*100 if original_count > 0 else 0
            results_table.add_row("Reduction", f"{reduction_pct:.1f}%")
            
            # Display both tables
            columns = Columns([filter_table, results_table], equal=True, expand=True)
            panel = Panel(columns, title="[bold blue]Data Filtering Summary[/bold blue]", border_style="blue")
            self.console.print(panel)
        else:
            self.console.print(f"\nFiltering: {original_count} → {filtered_count} instances")
    
    def display_results_table(self, results: List[EvalResult]):
        """Display beautiful results table."""
        if not results:
            self.console.print("❌ No results to display!")
            return
        
        if self.rich_enabled:
            self._display_rich_results(results)
        else:
            self._display_simple_results(results)
    
    def _display_rich_results(self, results: List[EvalResult]):
        """Display results using Rich tables."""
        # Group results by model
        models = list(set(r.model_name for r in results))
        
        # Create main results table
        table = Table(title="📊 Evaluation Results", box=box.ROUNDED)
        table.add_column("Model", style="cyan", width=15)
        table.add_column("Instances", justify="center", width=10)
        table.add_column("Success Rate", justify="center", width=12)
        table.add_column("Avg Score", justify="center", width=10)
        table.add_column("Avg Steps", justify="center", width=10)
        table.add_column("Avg Duration", justify="center", width=12)
        
        for model in sorted(models):
            model_results = [r for r in results if r.model_name == model]
            
            # Calculate metrics
            success_rate = sum(1 for r in model_results if r.success) / len(model_results)
            avg_score = sum(r.final_score for r in model_results) / len(model_results)
            avg_steps = sum(r.steps_taken for r in model_results) / len(model_results)
            avg_duration = sum(r.duration_seconds for r in model_results) / len(model_results)
            
            # Style the success rate
            success_style = "green" if success_rate > 0.8 else "yellow" if success_rate > 0.5 else "red"
            
            table.add_row(
                model,
                str(len(model_results)),
                f"[{success_style}]{success_rate:.1%}[/{success_style}]",
                f"{avg_score:.3f}",
                f"{avg_steps:.1f}",
                f"{avg_duration:.1f}s"
            )
        
        self.console.print("\n")
        self.console.print(table)
    
    def _display_simple_results(self, results: List[EvalResult]):
        """Display results using simple text formatting."""
        models = list(set(r.model_name for r in results))
        
        self.console.print("\n=== Evaluation Results ===")
        
        for model in sorted(models):
            model_results = [r for r in results if r.model_name == model]
            
            success_rate = sum(1 for r in model_results if r.success) / len(model_results)
            avg_score = sum(r.final_score for r in model_results) / len(model_results)
            avg_steps = sum(r.steps_taken for r in model_results) / len(model_results)
            avg_duration = sum(r.duration_seconds for r in model_results) / len(model_results)
            
            self.console.print(f"\n{model}:")
            self.console.print(f"  Instances: {len(model_results)}")
            self.console.print(f"  Success Rate: {success_rate:.1%}")
            self.console.print(f"  Avg Score: {avg_score:.3f}")
            self.console.print(f"  Avg Steps: {avg_steps:.1f}")
            self.console.print(f"  Avg Duration: {avg_duration:.1f}s")
    
    def save_results(self, results: List[EvalResult], output_file: str):
        """Save results to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            result_dict = {
                "run_id": result.run_id,
                "model_name": result.model_name,
                "instance_id": result.instance_id,
                "task_description": result.task_description,
                "success": result.success,
                "final_score": result.final_score,
                "steps_taken": result.steps_taken,
                "duration_seconds": result.duration_seconds,
                "error_message": result.error_message,
                "metadata": result.metadata
            }
            serializable_results.append(result_dict)
        
        with open(output_path, "w") as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        if self.rich_enabled:
            self.console.print(f"\n💾 [green]Results saved to {output_file}[/green]")
        else:
            self.console.print(f"\nResults saved to {output_file}")
    
    def print_status(self, message: str, style: str = ""):
        """Print status message with optional styling."""
        if self.rich_enabled and style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)
    
    def print_error(self, message: str):
        """Print error message."""
        if self.rich_enabled:
            self.console.print(f"[red]❌ {message}[/red]")
        else:
            self.console.print(f"ERROR: {message}")
    
    def print_success(self, message: str):
        """Print success message."""
        if self.rich_enabled:
            self.console.print(f"[green]✅ {message}[/green]")
        else:
            self.console.print(f"SUCCESS: {message}")
    
    def print_warning(self, message: str):
        """Print warning message."""
        if self.rich_enabled:
            self.console.print(f"[yellow]⚠️  {message}[/yellow]")
        else:
            self.console.print(f"WARNING: {message}")


# Convenience function for creating display instance
def create_display() -> BeautifulDisplay:
    """Create a BeautifulDisplay instance."""
    return BeautifulDisplay() 