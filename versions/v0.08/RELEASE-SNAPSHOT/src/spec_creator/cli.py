from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .lint_evaluator import evaluate_v004_corpus
from .linter import lint_file
from .models import canonical_contract_hash
from .validator import validate_workspace
from .trace_evaluator import evaluate_v005_corpus
from .traceability import analyze_impact, load_graph, validate_graph
from .ambiguity import analyze_ambiguity_file
from .ambiguity_evaluator import evaluate_v0061_corpus, preflight_ambiguity_corpus
from .package_manifest import write_package_manifest
from .discovery import plan_discovery_file
from .discovery_evaluator import evaluate_v007_corpus, preflight_discovery_corpus
from .task_compiler import compile_project_file, validate_compiled_graph
from .task_execution import replay_task_events_file
from .task_compiler_evaluator import evaluate_v008_corpus


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="spec-creator", description="Validate and lint Spec Creator workspaces/specifications.")
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="Validate a Spec Creator workspace.")
    v.add_argument("path", nargs="?", default=".")
    v.add_argument("--json", action="store_true", dest="json_output")
    v.add_argument("--no-package-manifest", action="store_true", help="Skip root PACKAGE-MANIFEST validation during in-progress development.")

    l = sub.add_parser("lint", help="Lint a Markdown specification.")
    l.add_argument("file")
    l.add_argument("--json", action="store_true", dest="json_output")
    l.add_argument("--approved-decision", action="append", default=[], dest="approved_decisions")

    e = sub.add_parser("evaluate-lint-corpus", help="Evaluate the frozen v0.04 lint corpus.")
    e.add_argument("path", nargs="?", default=".")
    e.add_argument("--json", action="store_true", dest="json_output")

    tv = sub.add_parser("trace-validate", help="Validate a v0.05 traceability graph JSON file.")
    tv.add_argument("file")
    tv.add_argument("--json", action="store_true", dest="json_output")

    ti = sub.add_parser("trace-impact", help="Compute upstream/downstream impact for graph node IDs.")
    ti.add_argument("file")
    ti.add_argument("seed", nargs="+")
    ti.add_argument("--json", action="store_true", dest="json_output")

    te = sub.add_parser("evaluate-trace-corpus", help="Evaluate the frozen v0.05 traceability corpus.")
    te.add_argument("path", nargs="?", default=".")
    te.add_argument("--json", action="store_true", dest="json_output")


    a = sub.add_parser("ambiguity", help="Analyze a Markdown specification for v0.06.1 ambiguity candidates.")
    a.add_argument("file")
    a.add_argument("--trace-graph", dest="trace_graph")
    a.add_argument("--json", action="store_true", dest="json_output")

    ae = sub.add_parser("evaluate-ambiguity-corpus", help="Evaluate the frozen v0.06.1 ambiguity corpus.")
    ae.add_argument("path", nargs="?", default=".")
    ae.add_argument("--json", action="store_true", dest="json_output")

    ap = sub.add_parser("preflight-ambiguity-corpus", help="Validate embedded trace graphs in an ambiguity corpus before freeze.")
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true", dest="json_output")


    d = sub.add_parser("discovery", help="Build a v0.07 adaptive discovery plan from a Markdown specification.")
    d.add_argument("file")
    d.add_argument("--profile", dest="profile")
    d.add_argument("--trace-graph", dest="trace_graph")
    d.add_argument("--json", action="store_true", dest="json_output")

    de = sub.add_parser("evaluate-discovery-corpus", help="Evaluate the frozen v0.07 adaptive discovery corpus.")
    de.add_argument("path", nargs="?", default=".")
    de.add_argument("--json", action="store_true", dest="json_output")

    dp = sub.add_parser("preflight-discovery-corpus", help="Run promoted-parent checks over a discovery corpus.")
    dp.add_argument("file")
    dp.add_argument("--json", action="store_true", dest="json_output")

    tc = sub.add_parser("task-compile", help="Compile a v0.08 normalized task project into a deterministic task graph.")
    tc.add_argument("file")
    tc.add_argument("--json", action="store_true", dest="json_output")

    tcv = sub.add_parser("task-graph-validate", help="Validate a compiled v0.08 task graph.")
    tcv.add_argument("file")
    tcv.add_argument("--json", action="store_true", dest="json_output")

    trp = sub.add_parser("task-replay", help="Replay append-only task execution events against an immutable compiled task graph.")
    trp.add_argument("graph")
    trp.add_argument("events")
    trp.add_argument("--json", action="store_true", dest="json_output")

    tce = sub.add_parser("evaluate-task-compiler-corpus", help="Evaluate the frozen v0.08 Task Compiler and execution corpora.")
    tce.add_argument("path", nargs="?", default=".")
    tce.add_argument("--json", action="store_true", dest="json_output")

    sp = sub.add_parser("seal-package", help="Generate the final top-level package manifest after release evidence is complete.")
    sp.add_argument("path", nargs="?", default=".")
    sp.add_argument("--release-version", required=True)
    sp.add_argument("--release-status", required=True)
    sp.add_argument("--generated-at-utc", required=True)

    h = sub.add_parser("hash-contract", help="Calculate canonical frozen-contract SHA-256.")
    h.add_argument("file")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)




    if args.command == "task-compile":
        payload = compile_project_file(args.file)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload.get("status") == "compiled" else 1

    if args.command == "task-graph-validate":
        try:
            obj = json.loads(Path(args.file).read_text(encoding="utf-8"))
            diagnostics = validate_compiled_graph(obj)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        payload = {"ok": not diagnostics, "diagnostics": diagnostics}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if not diagnostics else 1

    if args.command == "task-replay":
        try:
            payload = replay_task_events_file(args.graph, args.events)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload.get("ok") else 1

    if args.command == "evaluate-task-compiler-corpus":
        try:
            payload = evaluate_v008_corpus(args.path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(payload if args.json_output else {"counts": payload["counts"], "metrics": payload["metrics"], "hash_checks": payload["hash_checks"]}, indent=2, sort_keys=True))
        m = payload["metrics"]
        ok = (
            all(payload["hash_checks"].values())
            and m["accepted_task_graph_exact_match_rate"] >= 0.95
            and m["heldout_task_graph_exact_match_rate"] >= 0.95
            and m["negative_case_classification_accuracy"] == 1.0
            and m["dependency_provenance_accuracy"] == 1.0
            and m["critical_ready_task_trace_completeness_rate"] == 1.0
            and m["parallelization_decision_accuracy"] == 1.0
            and m["unresolved_decision_escape_count"] == 0
            and m["unsafe_parallelization_count"] == 0
            and m["oversized_ready_task_count"] == 0
            and m["dependency_cycle_escape_count"] == 0
            and m["invented_dependency_count"] == 0
            and m["execution_stream_exact_match_rate"] == 1.0
            and m["invalid_execution_escape_count"] == 0
            and m["deterministic_repeat_rate"] == 1.0
        )
        return 0 if ok else 1

    if args.command == "discovery":
        try:
            plan = plan_discovery_file(args.file, profile_path=args.profile, trace_graph_path=args.trace_graph)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        payload = plan.as_dict()
        if args.json_output:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for q in payload["questions"]:
                print(f"ASK {q['group_id']} score={q['information_value']} — {q['question']}")
            print(f"PASS: {payload['summary']['question_batches']} question batch(es) from {payload['summary']['baseline_questions']} baseline question(s)")
        return 0

    if args.command == "evaluate-discovery-corpus":
        try:
            result = evaluate_v007_corpus(args.path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json_output:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(json.dumps({"counts": result["counts"], "metrics": result["metrics"]}, indent=2, sort_keys=True))
        m = result["metrics"]
        ok = (
            m["owner_question_reduction_rate"] >= 0.40
            and m["information_value_top_selection_accuracy"] >= 0.95
            and m["heldout_action_exact_match_rate"] >= 0.95
            and m["safe_inference_exact_match_rate"] == 1.0
            and m["unsafe_default_count"] == 0
            and m["critical_ambiguity_escape_count"] == 0
            and m["dependency_frontier_accuracy"] == 1.0
            and m["provenance_completeness_rate"] == 1.0
            and m["unnecessary_question_rate"] <= 0.05
            and m["rework_proxy_error_count"] == 0
            and m["parent_preflight_rate"] == 1.0
        )
        return 0 if ok else 1

    if args.command == "preflight-discovery-corpus":
        try:
            result = preflight_discovery_corpus(args.file)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1

    if args.command == "ambiguity":
        try:
            report = analyze_ambiguity_file(args.file, trace_graph_path=args.trace_graph)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        payload = report.as_dict()
        if args.json_output:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for finding in payload["findings"]:
                q = f" question={finding.get('question')!r}" if finding.get("question") else ""
                print(f"{finding['severity'].upper()} {finding['code']} {finding['block_id']}:{finding['line']} — {finding['span']!r} disposition={finding['disposition']} score={finding['priority_score']}{q}")
            print(f"PASS: {payload['summary']['findings']} finding(s), {payload['summary']['questions']} question(s)")
        return 0

    if args.command == "evaluate-ambiguity-corpus":
        try:
            result = evaluate_v0061_corpus(args.path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json_output:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(json.dumps({"counts": result["counts"], "metrics": result["metrics"]}, indent=2, sort_keys=True))
        m = result["metrics"]
        ok = (
            m["defect_case_detection_rate"] >= 0.95
            and m["clean_case_acceptance_rate"] >= 0.95
            and m["decision_needed_classification_accuracy"] >= 0.95
            and m["governed_default_question_count"] == 0
            and m["priority_top_question_accuracy"] >= 0.90
            and m["implementation_time_clarification_reduction_proxy_rate"] >= 0.80
            and m["unnecessary_question_rate"] <= 0.05
            and m["critical_ambiguity_escape_count"] == 0
        )
        return 0 if ok else 1

    if args.command == "preflight-ambiguity-corpus":
        try:
            result = preflight_ambiguity_corpus(args.file)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1

    if args.command == "seal-package":
        try:
            path = write_package_manifest(args.path, release_version=args.release_version, release_status=args.release_status, generated_at_utc=args.generated_at_utc)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(path)
        return 0

    if args.command == "trace-validate":
        try:
            report = validate_graph(load_graph(args.file))
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        payload = report.as_dict()
        if args.json_output:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for d in sorted(report.diagnostics):
                print(f"{d.severity.upper()} {d.code} — {d.message}")
            print(f"{'PASS' if report.ok else 'FAIL'}: {len(report.errors)} error(s)")
        return 0 if report.ok else 1

    if args.command == "trace-impact":
        try:
            result = analyze_impact(load_graph(args.file), args.seed)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        payload = result.as_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if result.ok else 1

    if args.command == "evaluate-trace-corpus":
        try:
            result = evaluate_v005_corpus(args.path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json_output:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(json.dumps({"counts": result["counts"], "metrics": result["metrics"]}, indent=2, sort_keys=True))
        m = result["metrics"]
        ok = (
            m["invalid_graph_detection_rate"] == 1.0
            and m["valid_graph_acceptance_rate"] == 1.0
            and m["critical_traceability_coverage_rate"] == 1.0
            and m["impact_analysis_exact_match_rate"] == 1.0
            and m["diagnostic_code_precision"] == 1.0
            and m["valid_graph_false_positive_count"] == 0
        )
        return 0 if ok else 1

    if args.command == "hash-contract":
        try:
            obj = json.loads(Path(args.file).read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(canonical_contract_hash(obj))
        return 0

    if args.command == "lint":
        try:
            report = lint_file(args.file, approved_decisions=args.approved_decisions)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json_output:
            print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
        else:
            for finding in report.findings:
                state = "SUPPRESSED" if finding.suppressed else finding.severity.upper()
                related = f" related_line={finding.related_line}" if finding.related_line is not None else ""
                print(f"{state} {finding.rule_id} {args.file}:{finding.line}:{finding.column} — {finding.span!r}: {finding.rationale}{related}")
            print(f"{'PASS' if report.ok else 'FAIL'}: {len(report.unsuppressed)} unsuppressed finding(s), {sum(1 for f in report.findings if f.suppressed)} suppressed")
        return 0 if report.ok else 1

    if args.command == "evaluate-lint-corpus":
        try:
            result = evaluate_v004_corpus(args.path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json_output:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(json.dumps({"counts": result["counts"], "metrics": result["metrics"], "per_rule_precision": result["per_rule_precision"]}, indent=2, sort_keys=True))
        targets = result["metrics"]
        ok = (
            targets["defect_case_detection_rate"] == 1.0
            and targets["clean_case_acceptance_rate"] == 1.0
            and targets["finding_precision"] == 1.0
            and targets["diagnostic_completeness_rate"] == 1.0
            and targets["minimum_per_rule_precision"] == 1.0
            and targets["clean_false_positive_count"] == 0
        )
        return 0 if ok else 1

    report = validate_workspace(args.path, validate_package_manifest=not args.no_package_manifest)
    if args.json_output:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        for issue in sorted(report.issues):
            where = f"{issue.artifact}:{issue.line}" if issue.line else issue.artifact
            print(f"{issue.severity.upper()} {issue.code} {where} — {issue.message}")
        print(f"{'PASS' if report.ok else 'FAIL'}: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
