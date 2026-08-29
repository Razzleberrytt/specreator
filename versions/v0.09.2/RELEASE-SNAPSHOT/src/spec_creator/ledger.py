from __future__ import annotations

from pathlib import Path
from typing import Iterable
import json


def append_jsonl_records(path: str | Path, records: Iterable[dict], *, primary_id_field: str | None = None) -> None:
    """Append JSONL records without rewriting any existing byte prefix.

    When ``primary_id_field`` is supplied, existing and new primary IDs are
    checked for duplicates before any bytes are appended.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    new_records = list(records)
    if not new_records:
        return

    existing_ids: set[str] = set()
    existing = path.read_bytes() if path.exists() else b""
    if primary_id_field and existing:
        for line_no, raw in enumerate(existing.splitlines(), 1):
            if not raw.strip():
                continue
            obj = json.loads(raw.decode("utf-8"))
            value = obj.get(primary_id_field)
            if isinstance(value, str):
                if value in existing_ids:
                    raise ValueError(f"duplicate existing {primary_id_field} {value} at line {line_no}")
                existing_ids.add(value)

    seen_new: set[str] = set()
    if primary_id_field:
        for obj in new_records:
            value = obj.get(primary_id_field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"missing {primary_id_field}")
            if value in existing_ids or value in seen_new:
                raise ValueError(f"duplicate {primary_id_field} {value}")
            seen_new.add(value)

    payload = b""
    if existing and not existing.endswith(b"\n"):
        payload += b"\n"
    payload += b"".join(
        (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
        for obj in new_records
    )
    with path.open("ab") as f:
        f.write(payload)


def append_jsonl_records_validated(path: str | Path, records: Iterable[dict], *, schema: dict, primary_id_field: str | None = None) -> None:
    """Validate all proposed records against JSON Schema before appending any bytes."""
    from jsonschema import Draft202012Validator

    proposed = list(records)
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    for idx, obj in enumerate(proposed, 1):
        errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))
        for err in errors:
            where = ".".join(str(x) for x in err.absolute_path) or "<root>"
            failures.append(f"record {idx} {where}: {err.message}")
    if failures:
        raise ValueError("schema validation failed before append: " + "; ".join(failures))
    append_jsonl_records(path, proposed, primary_id_field=primary_id_field)
