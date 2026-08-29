"""Spec Creator v0.08 executable specification governance and task compilation layer."""
__version__ = "0.8.0"

from .validator import validate_workspace, validate_contract_hash
from .linter import lint_text, lint_file, Finding, LintReport
from .models import ValidationIssue, ValidationReport
from .traceability import validate_graph, analyze_impact, parse_graph, TraceabilityReport, ImpactReport
from .ambiguity import analyze_ambiguity, analyze_ambiguity_file, AmbiguityReport, AmbiguityFinding
from .discovery import plan_discovery, plan_discovery_file, DiscoveryPlan, DiscoveryProfile

__all__ = [
    "validate_workspace",
    "validate_contract_hash",
    "lint_text",
    "lint_file",
    "Finding",
    "LintReport",
    "ValidationIssue",
    "ValidationReport",
    "validate_graph",
    "analyze_impact",
    "parse_graph",
    "TraceabilityReport",
    "ImpactReport",
    "analyze_ambiguity",
    "analyze_ambiguity_file",
    "AmbiguityReport",
    "AmbiguityFinding",
    "plan_discovery",
    "plan_discovery_file",
    "DiscoveryPlan",
    "DiscoveryProfile",
]

from .task_compiler import compile_project, compile_project_file, validate_compilation_project, validate_compiled_graph
from .task_execution import replay_task_events, replay_task_events_file
