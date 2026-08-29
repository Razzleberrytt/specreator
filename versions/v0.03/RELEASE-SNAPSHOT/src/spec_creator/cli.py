from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .models import canonical_contract_hash
from .validator import validate_workspace


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="spec-creator", description="Validate Spec Creator protocol workspaces.")
    sub = p.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate", help="Validate a Spec Creator workspace.")
    v.add_argument("path", nargs="?", default=".")
    v.add_argument("--json", action="store_true", dest="json_output")
    h = sub.add_parser("hash-contract", help="Calculate canonical frozen-contract SHA-256.")
    h.add_argument("file")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "hash-contract":
        try:
            obj = json.loads(Path(args.file).read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(canonical_contract_hash(obj))
        return 0

    report = validate_workspace(args.path)
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
