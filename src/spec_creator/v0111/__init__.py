"""Spec Creator v0.11.1 lifecycle and execution architecture."""
from .lifecycle import LifecycleResolutionError, derive_next_action
from .execution_architecture import (
    ArchitectureError,
    analyze_fixture,
    build_execution_plan,
    derive_effective_edges,
    invalidated_tasks,
)
__all__=["LifecycleResolutionError","derive_next_action","ArchitectureError","analyze_fixture","build_execution_plan","derive_effective_edges","invalidated_tasks"]
