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
