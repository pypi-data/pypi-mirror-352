"""
Filtering utilities for evaluation instances.

Provides clean filtering functions for different criteria.
"""

from typing import List, Set, Callable, Any
from .types import TaskInstance, FilterCriteria, DifficultyLevel


def apply_filters(
    instances: List[TaskInstance], 
    criteria: FilterCriteria,
    token_estimator: Callable[[TaskInstance], int] = None
) -> List[TaskInstance]:
    """Apply filtering criteria to a list of instances."""
    
    filtered = instances.copy()
    
    # Token range filter
    if token_estimator and criteria.token_range != (0, float('inf')):
        min_tokens, max_tokens = criteria.token_range
        filtered = [
            inst for inst in filtered 
            if min_tokens <= token_estimator(inst) <= max_tokens
        ]
    
    # Difficulty filter
    if criteria.difficulty_levels:
        filtered = [
            inst for inst in filtered
            if _get_difficulty(inst) in criteria.difficulty_levels
        ]
    
    # Scenario types filter
    if criteria.scenario_types:
        filtered = [
            inst for inst in filtered
            if _get_scenario_type(inst) in criteria.scenario_types
        ]
    
    # Required features filter
    if criteria.required_features:
        filtered = [
            inst for inst in filtered
            if _has_required_features(inst, criteria.required_features)
        ]
    
    # Custom filters
    for custom_filter in criteria.custom_filters:
        filtered = [inst for inst in filtered if custom_filter(inst)]
    
    # Apply instance limit
    if criteria.max_instances and len(filtered) > criteria.max_instances:
        filtered = filtered[:criteria.max_instances]
    
    return filtered


def _get_difficulty(instance: TaskInstance) -> DifficultyLevel:
    """Extract difficulty level from instance metadata."""
    metadata = instance.metadata
    
    # Check common difficulty field names
    difficulty_fields = ['difficulty', 'level', 'complexity']
    
    for field in difficulty_fields:
        if field in metadata:
            difficulty_str = str(metadata[field]).lower()
            
            # Map common values to DifficultyLevel
            if difficulty_str in ['easy', 'simple', 'basic']:
                return DifficultyLevel.EASY
            elif difficulty_str in ['medium', 'moderate', 'intermediate']:
                return DifficultyLevel.MEDIUM
            elif difficulty_str in ['hard', 'difficult', 'complex', 'advanced']:
                return DifficultyLevel.HARD
    
    return DifficultyLevel.UNKNOWN


def _get_scenario_type(instance: TaskInstance) -> str:
    """Extract scenario type from instance metadata."""
    metadata = instance.metadata
    
    # Check common scenario type field names
    scenario_fields = ['scenario_type', 'category', 'type', 'domain']
    
    for field in scenario_fields:
        if field in metadata:
            return str(metadata[field])
    
    return "unknown"


def _has_required_features(instance: TaskInstance, required_features: Set[str]) -> bool:
    """Check if instance has all required features."""
    metadata = instance.metadata
    
    # Check if all required features are present in metadata
    for feature in required_features:
        if feature not in metadata:
            return False
        
        # If feature value is boolean, check if it's True
        feature_value = metadata[feature]
        if isinstance(feature_value, bool) and not feature_value:
            return False
    
    return True


# Convenience functions for common filters

def create_token_filter(min_tokens: int = 0, max_tokens: int = float('inf')) -> FilterCriteria:
    """Create a filter for token count range."""
    return FilterCriteria(token_range=(min_tokens, max_tokens))


def create_difficulty_filter(difficulties: List[str]) -> FilterCriteria:
    """Create a filter for difficulty levels."""
    difficulty_set = set()
    for diff in difficulties:
        if hasattr(DifficultyLevel, diff.upper()):
            difficulty_set.add(getattr(DifficultyLevel, diff.upper()))
    
    return FilterCriteria(difficulty_levels=difficulty_set)


def create_scenario_filter(scenario_types: List[str]) -> FilterCriteria:
    """Create a filter for scenario types."""
    return FilterCriteria(scenario_types=set(scenario_types))


def create_limit_filter(max_instances: int) -> FilterCriteria:
    """Create a filter that limits the number of instances."""
    return FilterCriteria(max_instances=max_instances)


def combine_filters(*criteria_list: FilterCriteria) -> FilterCriteria:
    """Combine multiple filter criteria into one."""
    combined = FilterCriteria()
    
    for criteria in criteria_list:
        # Combine token ranges (take intersection)
        if criteria.token_range != (0, float('inf')):
            min_tokens = max(combined.token_range[0], criteria.token_range[0])
            max_tokens = min(combined.token_range[1], criteria.token_range[1])
            combined.token_range = (min_tokens, max_tokens)
        
        # Combine difficulty levels (take intersection)
        if criteria.difficulty_levels:
            if combined.difficulty_levels is None:
                combined.difficulty_levels = criteria.difficulty_levels.copy()
            else:
                combined.difficulty_levels &= criteria.difficulty_levels
        
        # Combine scenario types (take intersection)
        if criteria.scenario_types:
            if combined.scenario_types is None:
                combined.scenario_types = criteria.scenario_types.copy()
            else:
                combined.scenario_types &= criteria.scenario_types
        
        # Combine required features (take union)
        if criteria.required_features:
            if combined.required_features is None:
                combined.required_features = criteria.required_features.copy()
            else:
                combined.required_features |= criteria.required_features
        
        # Take minimum max_instances
        if criteria.max_instances is not None:
            if combined.max_instances is None:
                combined.max_instances = criteria.max_instances
            else:
                combined.max_instances = min(combined.max_instances, criteria.max_instances)
        
        # Combine custom filters
        combined.custom_filters.extend(criteria.custom_filters)
    
    return combined 