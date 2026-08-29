from __future__ import annotations

import json
from pathlib import Path

from spec_creator.cli import main


def test_discovery_cli(tmp_path, capsys):
    spec = tmp_path / "spec.md"
    spec.write_text("""### REQ-CLI-007
Requirement: Select storage.
Critical: false
Options: storage = SQLite | PostgreSQL
Acceptance: selected
Verify: cli
""")
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"profile_id":"P","project_type":"prototype","defaults":[{"block_id":"REQ-CLI-007","ambiguity_code":"AMB-001","span":"storage","value":"SQLite","risk":"low","reversible":True,"auto_apply":True,"provenance":"owner_intake","source_ref":"CLI-IN"}]}))
    rc = main(["discovery", str(spec), "--profile", str(profile), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["actions"][0]["action"] == "infer_default"
    assert payload["summary"]["question_batches"] == 0


def test_discovery_cli_rejects_malformed_profile(tmp_path, capsys):
    spec = tmp_path / "spec.md"
    spec.write_text("### REQ-X\nRequirement: Select x.\nCritical: false\nOptions: x = a | b\nAcceptance: selected\nVerify: cli\n")
    profile = tmp_path / "bad.json"
    profile.write_text('{"profile_id":"P","project_type":"custom","question_budget":0,"defaults":[]}')
    assert main(["discovery", str(spec), "--profile", str(profile), "--json"]) == 1
    assert "question_budget" in capsys.readouterr().err
