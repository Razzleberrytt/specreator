"""Spec Creator v0.07 executable validation, lint, traceability, ambiguity, and adaptive discovery layer."""
__version__ = "0.7.0"

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
