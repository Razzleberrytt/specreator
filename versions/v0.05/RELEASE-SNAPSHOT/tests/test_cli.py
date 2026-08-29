from __future__ import annotations

import json
from spec_creator.cli import main


def test_cli_validate_json_pass(valid_workspace, capsys):
    rc = main(["validate", str(valid_workspace), "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["ok"] is True


def test_cli_validate_failure_exit(valid_workspace, helpers, capsys):
    p = valid_workspace / "evaluation/events.jsonl"
    p.write_text("{broken:\n", encoding="utf-8")
    rc = main(["validate", str(valid_workspace)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "MALFORMED_JSONL" in out


def test_cli_hash_contract(valid_workspace, capsys):
    p = valid_workspace / "versions/v0.03/FROZEN-RELEASE-CONTRACT.json"
    rc = main(["hash-contract", str(p)])
    output = capsys.readouterr().out.strip()
    contract = json.loads(p.read_text(encoding="utf-8"))
    assert rc == 0
    assert output == contract["contract_hash"]


def test_cli_lint_json_failure(tmp_path, capsys):
    p = tmp_path / "spec.md"
    p.write_text("The service must be fast.\n", encoding="utf-8")
    rc = main(["lint", str(p), "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["ok"] is False
    assert out["findings"][0]["rule_id"] == "LINT-001"


def test_cli_lint_clean_pass(tmp_path, capsys):
    p = tmp_path / "spec.md"
    p.write_text("The endpoint must return within 250 ms at p95.\n", encoding="utf-8")
    rc = main(["lint", str(p)])
    assert rc == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_lint_approved_suppression_pass(tmp_path, capsys):
    p = tmp_path / "spec.md"
    p.write_text("Lint-Suppress: LINT-001 decision=DEC-9001\nThe service must be fast.\n", encoding="utf-8")
    rc = main(["lint", str(p), "--approved-decision", "DEC-9001"])
    assert rc == 0
    assert "SUPPRESSED LINT-001" in capsys.readouterr().out


def test_cli_evaluate_frozen_corpus_pass(capsys):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    rc = main(["evaluate-lint-corpus", str(root)])
    out = capsys.readouterr().out
    assert rc == 0
    assert '"defect_case_detection_rate": 1.0' in out
