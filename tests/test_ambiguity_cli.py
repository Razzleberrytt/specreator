import json
from pathlib import Path
from spec_creator.cli import main


def test_ambiguity_cli(tmp_path, capsys):
    p = tmp_path / "spec.md"
    p.write_text("### REQ-X\nRequirement: The operation must complete quickly.\nCritical: true\nAcceptance: explicit.\nVerify: x\n")
    assert main(["ambiguity", str(p), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["findings"][0]["code"] == "AMB-002"


def test_invalid_trace_graph_returns_nonzero(tmp_path, capsys):
    p = tmp_path / "spec.md"; p.write_text("### REQ-X\nRequirement: Select storage.\nCritical: true\nOptions: storage = A | B\nAcceptance: explicit.\nVerify: x\n")
    g = tmp_path / "g.json"; g.write_text('{"graph_id":"bad","schema_version":"1.0","nodes":[],"edges":[]}')
    assert main(["ambiguity", str(p), "--trace-graph", str(g), "--json"]) == 1
    assert "invalid traceability graph" in capsys.readouterr().err
