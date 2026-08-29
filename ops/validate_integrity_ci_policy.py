#!/usr/bin/env python3
"""Fail-closed policy checks for the additive integrity CI workflow."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/integrity.yml"
CONSTRAINTS = ROOT / ".github/ci-constraints.txt"

CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"
SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"
PYTHON_VERSION = "3.11.16"
RUNNER = "ubuntu-24.04"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def active_yaml_lines(text: str) -> list[str]:
    """Return nonblank workflow lines with whole-line comments removed."""
    return [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def workflow_steps(lines: list[str]) -> list[list[str]]:
    """Extract the job's active step blocks using their YAML indentation."""
    starts = [
        index
        for index, line in enumerate(lines)
        if re.match(r"^\s{6}-\s+(name|uses|run):", line)
    ]
    if not starts:
        fail("integrity workflow contains no active steps")

    steps: list[list[str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        steps.append(lines[start:end])
    return steps


def step_has_exact_line(step: list[str], pattern: str) -> bool:
    return any(re.fullmatch(pattern, line) for line in step)


def step_run_commands(step: list[str]) -> list[str]:
    """Return normalized active run commands for one workflow step.

    Supports both item form (`- run: cmd`) and mapping form (`run: cmd`), plus
    YAML block scalars. The workflow is deliberately constrained enough that a
    dependency-free parser can fail closed without interpreting general YAML.
    """
    declaration_index: int | None = None
    value: str | None = None
    for index, line in enumerate(step):
        item_match = re.fullmatch(r"\s{6}-\s+run:\s*(.*)", line)
        mapping_match = re.fullmatch(r"\s{8}run:\s*(.*)", line)
        match = item_match or mapping_match
        if match:
            if declaration_index is not None:
                fail("workflow step contains multiple run declarations")
            declaration_index = index
            value = match.group(1).strip()

    if declaration_index is None or value is None:
        return []

    if value not in {"|", "|-", "|+", ">", ">-", ">+"}:
        return [value]

    body: list[str] = []
    for line in step[declaration_index + 1 :]:
        indentation = len(line) - len(line.lstrip())
        if indentation <= 8:
            break
        body.append(line.strip())
    if not body:
        fail("run block scalar must contain executable content")
    return body


def main() -> None:
    if not WORKFLOW.is_file() or not CONSTRAINTS.is_file():
        fail("integrity workflow and CI constraints must both exist")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    active_lines = active_yaml_lines(workflow)
    active_workflow = "\n".join(active_lines)
    steps = workflow_steps(active_lines)

    required_fragments = {
        "least-privilege contents permission": "permissions:\n  contents: read",
        "pinned runner": f"runs-on: {RUNNER}",
        "pinned checkout action": f"actions/checkout@{CHECKOUT_SHA}",
        "pinned setup-python action": f"actions/setup-python@{SETUP_PYTHON_SHA}",
        "pinned Python runtime": f"python-version: '{PYTHON_VERSION}'",
        "constraints-backed cache": "cache-dependency-path: .github/ci-constraints.txt",
        "constraints-backed installation": "-c .github/ci-constraints.txt -e . pytest==9.1.1",
        "dependency consistency check": "python -m pip check",
        "control-plane validation": "python ops/validate_control_plane.py",
        "CI-policy validation": "python ops/validate_integrity_ci_policy.py",
        "frozen contract preflight": "python versions/v0.11.1/tools/frozen_contract_preflight.py",
        "workspace validation": "PYTHONPATH=src python -m spec_creator.cli validate . --no-package-manifest",
        "historical pytest": "python -m pytest -q",
        "manifest cardinality": "len(entries) != 1770",
        "package cardinality": "count != 1771",
    }
    for label, fragment in required_fragments.items():
        if fragment not in active_workflow:
            fail(f"integrity workflow lost required invariant: {label}")

    checkout_ref = f"actions/checkout@{CHECKOUT_SHA}"
    checkout_steps = [
        step
        for step in steps
        if any(re.fullmatch(rf"\s+uses:\s*{re.escape(checkout_ref)}(?:\s+#.*)?", line) for line in step)
    ]
    if len(checkout_steps) != 1:
        fail(f"integrity workflow must contain exactly one approved checkout step, found {len(checkout_steps)}")

    checkout_step = checkout_steps[0]
    with_positions = [index for index, line in enumerate(checkout_step) if re.fullmatch(r"\s{8}with:", line)]
    if len(with_positions) != 1:
        fail("checkout step must contain exactly one with mapping")
    with_index = with_positions[0]
    checkout_inputs = []
    for line in checkout_step[with_index + 1 :]:
        if re.match(r"^\s{10}\S", line):
            checkout_inputs.append(line.strip())
        elif len(line) - len(line.lstrip()) <= 8:
            break
    persist_values = [
        item.split(":", 1)[1].strip().lower()
        for item in checkout_inputs
        if item.startswith("persist-credentials:")
    ]
    if persist_values != ["false"]:
        fail("checkout must set exactly one active persist-credentials: false input")

    policy_step_indexes = [
        index
        for index, step in enumerate(steps)
        if step_run_commands(step) == ["python ops/validate_integrity_ci_policy.py"]
    ]
    if len(policy_step_indexes) != 1:
        fail("integrity workflow must contain exactly one active CI-policy validation step")

    control_plane_step_indexes = [
        index
        for index, step in enumerate(steps)
        if step_run_commands(step) == ["python ops/validate_control_plane.py"]
    ]
    if len(control_plane_step_indexes) != 1:
        fail("integrity workflow must contain exactly one active control-plane validation step")

    setup_python_ref = f"actions/setup-python@{SETUP_PYTHON_SHA}"
    setup_python_step_indexes = [
        index
        for index, step in enumerate(steps)
        if any(re.fullmatch(rf"\s+uses:\s*{re.escape(setup_python_ref)}(?:\s+#.*)?", line) for line in step)
    ]
    if len(setup_python_step_indexes) != 1:
        fail("integrity workflow must contain exactly one approved setup-python step")

    install_step_indexes = [
        index
        for index, step in enumerate(steps)
        if any("python -m pip install" in command for command in step_run_commands(step))
    ]
    if len(install_step_indexes) != 1:
        fail("integrity workflow must contain exactly one approved dependency-install step")

    policy_index = policy_step_indexes[0]
    control_index = control_plane_step_indexes[0]
    setup_index = setup_python_step_indexes[0]
    install_index = install_step_indexes[0]
    if not policy_index < control_index < setup_index < install_index:
        fail(
            "CI-policy validation and dependency-free control-plane validation must run "
            "before setup-python and package/dependency installation"
        )

    # Fail closed at the dependency-free boundary. Before control-plane
    # validation, the only executable `run:` step permitted is the policy
    # validator itself. This rejects alternate installer spellings and any
    # arbitrary shell/bootstrap execution without maintaining a denylist.
    for index, step in enumerate(steps[:control_index]):
        commands = step_run_commands(step)
        if not commands:
            continue
        if index == policy_index and commands == ["python ops/validate_integrity_ci_policy.py"]:
            continue
        fail(
            "no executable run step other than CI-policy validation may occur "
            "before dependency-free control-plane validation"
        )

    allowed_uses = {
        f"actions/checkout@{CHECKOUT_SHA}",
        f"actions/setup-python@{SETUP_PYTHON_SHA}",
    }
    observed_uses = set(re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", active_workflow))
    unexpected = sorted(observed_uses - allowed_uses)
    missing = sorted(allowed_uses - observed_uses)
    if unexpected:
        fail(f"integrity workflow contains unapproved action references: {unexpected}")
    if missing:
        fail(f"integrity workflow is missing approved action references: {missing}")

    if re.search(r"(?m)^\s*uses:\s*[^\n]+@(v\d+|main|master|latest)\b", active_workflow):
        fail("integrity workflow contains mutable action ref")

    constraint_lines = [
        line.strip()
        for line in CONSTRAINTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not constraint_lines:
        fail("CI constraints file is empty")
    invalid = [line for line in constraint_lines if not re.fullmatch(r"[A-Za-z0-9_.-]+==[^\s]+", line)]
    if invalid:
        fail(f"CI constraints must be exact name==version pins: {invalid}")
    if len(constraint_lines) != len(set(line.lower() for line in constraint_lines)):
        fail("CI constraints contain duplicate package pins")
    if "pytest==9.1.1" not in {line.lower() for line in constraint_lines}:
        fail("CI constraints must pin pytest==9.1.1")

    print(
        "PASS: integrity CI policy is credentialless, dependency-free control-plane-first, "
        "pinned, least-privilege, reproducible, and fail-closed"
    )


if __name__ == "__main__":
    main()
