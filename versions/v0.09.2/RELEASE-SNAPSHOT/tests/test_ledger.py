import json
from pathlib import Path
import pytest

from spec_creator.ledger import append_jsonl_records_validated


def test_validated_append_rejects_schema_invalid_records_before_write(tmp_path):
    path = tmp_path / "records.jsonl"
    path.write_bytes(b'{"id":"old","value":"ok"}\n')
    before = path.read_bytes()
    schema = {
        "$schema":"https://json-schema.org/draft/2020-12/schema",
        "type":"object",
        "required":["id","value"],
        "properties":{"id":{"type":"string"},"value":{"type":"string"}},
        "additionalProperties":False,
    }
    with pytest.raises(ValueError, match="schema validation failed before append"):
        append_jsonl_records_validated(path, [{"id":"new","wrong":1}], schema=schema, primary_id_field="id")
    assert path.read_bytes() == before


def test_validated_append_rejects_duplicate_existing_id_before_write(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_bytes(b'{"id":"EVT-1","value":"old"}\n')
    before = path.read_bytes()
    schema = {
        "$schema":"https://json-schema.org/draft/2020-12/schema",
        "type":"object",
        "required":["id","value"],
        "properties":{"id":{"type":"string"},"value":{"type":"string"}},
        "additionalProperties":False,
    }
    with pytest.raises(ValueError, match="duplicate id EVT-1"):
        append_jsonl_records_validated(path, [{"id":"EVT-1","value":"new"}], schema=schema, primary_id_field="id")
    assert path.read_bytes() == before
