import json
from pathlib import Path

from spec_creator.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_prompt_compile_cli_json(tmp_path, capsys):
    case = next(json.loads(line) for line in (ROOT / "fixtures/prompt-compiler/v0.09.2/development.jsonl").read_text().splitlines() if json.loads(line)["class"] == "accepted")
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(case["input"]))
    assert main(["prompt-compile", str(input_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == case["expected_envelope"]


def test_prompt_evaluator_cli_defaults_to_v0092(capsys):
    assert main(["evaluate-prompt-compiler-corpus", str(ROOT), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["candidate_version"] == "0.09.2"
    assert payload["metrics"]["negative_case_classification_accuracy"] == 1.0
