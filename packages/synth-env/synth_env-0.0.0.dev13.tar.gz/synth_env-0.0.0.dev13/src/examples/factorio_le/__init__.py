"""Factorio Learning Environment

A code-execution based environment where agents write Python code as actions
to interact with the Factorio game world through an API.

Based on the Factorio Learning Environment by Jack Hopkins et al.
"""

from .engine import FactorioEngine
from .environment import FactorioEnvironment  
from .taskset import (
    create_factorio_taskset,
    FactorioTaskInstance,
    FactorioTaskInstanceMetadata,
)

__all__ = [
    "FactorioEngine",
    "FactorioEnvironment", 
    "create_factorio_taskset",
    "FactorioTaskInstance",
    "FactorioTaskInstanceMetadata",
]