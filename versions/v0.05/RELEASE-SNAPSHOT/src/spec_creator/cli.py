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

    h = sub.add_parser("hash-contract", help="Calculate canonical frozen-contract SHA-256.")
    h.add_argument("file")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)


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
