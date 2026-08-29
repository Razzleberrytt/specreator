from __future__ import annotations

from pathlib import Path
import json

from spec_creator.cli import main


ROOT = Path(__file__).resolve().parents[1]


def _write_case(tmp_path, kind):
    rows = [json.loads(x) for x in (ROOT / "fixtures/traceability/v0.05/corpus.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    case = next(r for r in rows if r["case_kind"] == kind)
    p = tmp_path / f"{kind}.json"
    p.write_text(json.dumps(case["graph"]), encoding="utf-8")
    return p, case


def test_traceability_cli(tmp_path, capsys):
    p, _ = _write_case(tmp_path, "valid")
    assert main(["trace-validate", str(p), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True

    rows = [json.loads(x) for x in (ROOT / "fixtures/traceability/v0.05/corpus.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    bad = next(r for r in rows if r["case_kind"] == "invalid")
    bp = tmp_path / "invalid.json"
    bp.write_text(json.dumps(bad["graph"]), encoding="utf-8")
    assert main(["trace-validate", str(bp), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_traceability_impact_cli(tmp_path, capsys):
    p, case = _write_case(tmp_path, "impact")
    assert main(["trace-impact", str(p), *case["impact_seed_ids"], "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["upstream"] == case["expected_upstream"]
    assert payload["downstream"] == case["expected_downstream"]
    assert main(["trace-impact", str(p), "UNKNOWN", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_traceability_corpus_cli(capsys):
    assert main(["evaluate-trace-corpus", str(ROOT), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["metrics"]["impact_analysis_exact_match_rate"] == 1.0
