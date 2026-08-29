import json
from pathlib import Path

from spec_creator.ambiguity import analyze_ambiguity

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "fixtures/ambiguity/v0.06.1/corpus.jsonl"


def rows():
    return [json.loads(x) for x in CORPUS.read_text().splitlines() if x.strip()]


def test_frozen_candidate_detection_and_diagnostics():
    for case in rows():
        if case["case_kind"] not in {"defect", "resolved", "priority", "workflow", "clean"}:
            continue
        report = analyze_ambiguity(case["document"], trace_graph=case.get("trace_graph"))
        actual = {(f.block_id, f.code): f for f in report.findings}
        for expected in case.get("expected_findings", []):
            assert (expected["block_id"], expected["code"]) in actual, case["case_id"]
        if case["case_kind"] == "clean":
            assert not report.findings, case["case_id"]


def test_decision_needed_classification():
    for case in rows():
        report = analyze_ambiguity(case["document"], trace_graph=case.get("trace_graph"))
        actual = {(f.block_id, f.code): f for f in report.findings}
        for expected in case.get("expected_findings", []):
            got = actual[(expected["block_id"], expected["code"])]
            assert got.decision_needed is expected["decision_needed"], case["case_id"]
            assert got.disposition == expected["disposition"], case["case_id"]


def test_governed_defaults_are_scoped():
    resolved = [c for c in rows() if c["case_kind"] == "resolved"]
    for case in resolved:
        report = analyze_ambiguity(case["document"])
        assert report.findings
        assert all(not f.decision_needed for f in report.findings)
        assert report.questions == []

    mismatched = """### REQ-X\nRequirement: Select persistence.\nCritical: true\nOptions: storage_backend = SQLite | PostgreSQL\nDefault: cache_backend = memory\nAcceptance: Explicit.\nVerify: x\n"""
    report = analyze_ambiguity(mismatched)
    assert report.findings[0].decision_needed is True


def test_traceability_impact_context():
    priority = next(c for c in rows() if c["case_id"] == "PRI-01")
    report = analyze_ambiguity(priority["document"], trace_graph=priority["trace_graph"])
    by = {f.block_id: f for f in report.findings if f.code == "AMB-001"}
    assert by["REQ-PRI01-A"].downstream_impact_count == 4
    assert by["REQ-PRI01-B"].downstream_impact_count == 8

    broken = dict(priority["trace_graph"])
    broken["graph_id"] = "INVALID"
    import pytest
    with pytest.raises(ValueError, match="invalid traceability graph"):
        analyze_ambiguity(priority["document"], trace_graph=broken)


def test_question_priority():
    for case in [c for c in rows() if c["case_kind"] == "priority"]:
        report = analyze_ambiguity(case["document"], trace_graph=case["trace_graph"])
        assert report.questions
        top = report.questions[0]
        assert (top.block_id, top.code) == (case["expected_top_question"]["block_id"], case["expected_top_question"]["code"])


def test_question_generation_guardrails():
    for case in rows():
        report = analyze_ambiguity(case["document"], trace_graph=case.get("trace_graph"))
        for finding in report.findings:
            if finding.decision_needed:
                assert finding.question
            else:
                assert finding.question is None


def test_pending_status_marker_does_not_flag_domain_adjective():
    clean = """### REQ-PENDING-CLEAN
Requirement: Return HTTP 204 after the queue contains zero pending records.
Critical: true
Acceptance: Response is 204 when queue depth is zero.
Verify: unit test
"""
    report = analyze_ambiguity(clean)
    assert not [f for f in report.findings if f.code == "AMB-006"]

    unresolved = """### REQ-PENDING-OPEN
Requirement: Storage encryption mode is pending.
Critical: true
Acceptance: Encryption mode is explicit.
Verify: review
"""
    report = analyze_ambiguity(unresolved)
    hits = [f for f in report.findings if f.code == "AMB-006"]
    assert len(hits) == 1
    assert hits[0].span.lower() == "pending"
