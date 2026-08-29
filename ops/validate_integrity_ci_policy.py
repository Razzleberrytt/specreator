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


def main() -> None:
    if not WORKFLOW.is_file() or not CONSTRAINTS.is_file():
        fail("integrity workflow and CI constraints must both exist")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    required_fragments = {
        "least-privilege contents permission": "permissions:\n  contents: read",
        "pinned runner": f"runs-on: {RUNNER}",
        "pinned checkout action": f"actions/checkout@{CHECKOUT_SHA}",
        "credentialless checkout": "persist-credentials: false",
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
        if fragment not in workflow:
            fail(f"integrity workflow lost required invariant: {label}")

    policy_pos = workflow.find("run: python ops/validate_integrity_ci_policy.py")
    install_pos = workflow.find("python -m pip install")
    if policy_pos < 0 or install_pos < 0 or policy_pos > install_pos:
        fail("CI-policy validation must run before package/dependency installation")

    checkout_block = re.search(
        rf"uses:\s*actions/checkout@{CHECKOUT_SHA}[^\n]*\n(?P<body>(?:\s+[^\n]*\n){{1,8}})",
        workflow,
    )
    if not checkout_block or "persist-credentials: false" not in checkout_block.group("body"):
        fail("checkout must explicitly disable persisted repository credentials")

    allowed_uses = {
        f"actions/checkout@{CHECKOUT_SHA}",
        f"actions/setup-python@{SETUP_PYTHON_SHA}",
    }
    observed_uses = set(re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", workflow))
    unexpected = sorted(observed_uses - allowed_uses)
    missing = sorted(allowed_uses - observed_uses)
    if unexpected:
        fail(f"integrity workflow contains unapproved action references: {unexpected}")
    if missing:
        fail(f"integrity workflow is missing approved action references: {missing}")

    if re.search(r"(?m)^\s*uses:\s*[^\n]+@(v\d+|main|master|latest)\b", workflow):
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

    print("PASS: integrity CI policy is credentialless, pre-install, pinned, least-privilege, reproducible, and fail-closed")


if __name__ == "__main__":
    main()
