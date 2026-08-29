import json
from pathlib import Path

from spec_creator.prompt_compiler import compile_prompt, validate_prompt_envelope

ROOT = Path(__file__).resolve().parents[1]


def _accepted():
    for line in (ROOT / "fixtures/prompt-compiler/v0.09.2/development.jsonl").read_text().splitlines():
        case = json.loads(line)
        if case["class"] == "accepted":
            return case
    raise AssertionError("accepted fixture missing")


def test_v0092_api_matches_frozen_accepted_envelope():
    case = _accepted()
    actual = compile_prompt(case["input"], root=ROOT)
    assert actual == case["expected_envelope"]
    assert validate_prompt_envelope(actual, root=ROOT) == []


def test_v0092_api_is_deterministic():
    case = _accepted()
    assert compile_prompt(case["input"], root=ROOT) == compile_prompt(case["input"], root=ROOT)
