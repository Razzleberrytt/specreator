"""Spec Creator v0.05 executable validation, lint, and traceability layer."""
__version__ = "0.5.0"

from .validator import validate_workspace, validate_contract_hash
from .linter import lint_text, lint_file, Finding, LintReport
from .models import ValidationIssue, ValidationReport
from .traceability import validate_graph, analyze_impact, parse_graph, TraceabilityReport, ImpactReport

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
]
