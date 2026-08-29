from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
import json

from jsonschema import Draft202012Validator, FormatChecker

from .models import canonical_contract_hash


class FreezePreconditionError(ValueError):
    """Raised when a release freeze is attempted with any failed precondition."""


class FrozenContractValidationError(ValueError):
    """Raised when a candidate frozen contract fails schema/hash validation."""


def finalize_frozen_contract(contract: Mapping[str, Any], *, schema_path: str | Path) -> dict[str, Any]:
    """Return a hash-complete, schema-valid frozen-contract object without writing it."""
    candidate = deepcopy(dict(contract))
    candidate["contract_hash"] = ""
    candidate["contract_hash"] = canonical_contract_hash(candidate)

    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(candidate), key=lambda err: list(err.absolute_path))
    if errors:
        details = []
        for err in errors:
            where = ".".join(str(x) for x in err.absolute_path) or "<root>"
            details.append(f"{where}: {err.message}")
        raise FrozenContractValidationError("; ".join(details))
    if candidate["contract_hash"] != canonical_contract_hash(candidate):
        raise FrozenContractValidationError("contract_hash does not match canonical contract content")
    return candidate


def freeze_contract_fail_closed(
    contract: Mapping[str, Any],
    *,
    destination: str | Path,
    schema_path: str | Path,
    preconditions: Mapping[str, bool],
) -> dict[str, Any]:
    """Validate all preconditions and the contract in memory before creating the recognized path."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing frozen contract: {destination}")
    if not preconditions:
        raise FreezePreconditionError("Freeze requires an explicit non-empty precondition set")
    failed = sorted(name for name, ok in preconditions.items() if ok is not True)
    if failed:
        raise FreezePreconditionError("Failed freeze preconditions: " + ", ".join(failed))

    finalized = finalize_frozen_contract(contract, schema_path=schema_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + ".tmp")
    payload = json.dumps(finalized, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(destination)
    finally:
        if tmp.exists():
            tmp.unlink()
    return finalized
