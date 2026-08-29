from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import copy
import hashlib
import json


@dataclass(order=True)
class ValidationIssue:
    code: str
    artifact: str
    message: str
    severity: str = "error"
    line: int | None = None

    def as_dict(self) -> dict[str, Any]:
        data = {
            "code": self.code,
            "severity": self.severity,
            "artifact": self.artifact,
            "message": self.message,
        }
        if self.line is not None:
            data["line"] = self.line
        return data


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, code: str, artifact: str, message: str, *, severity: str = "error", line: int | None = None) -> None:
        self.issues.append(ValidationIssue(code, artifact, message, severity, line))

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, Any]:
        ordered = sorted(self.issues)
        return {
            "ok": self.ok,
            "summary": {"errors": len(self.errors), "warnings": len(self.warnings), "issues": len(self.issues)},
            "issues": [i.as_dict() for i in ordered],
        }


def canonical_contract_hash(contract: dict[str, Any]) -> str:
    candidate = copy.deepcopy(contract)
    candidate.pop("contract_hash", None)
    payload = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
