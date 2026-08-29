from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

from .linter import lint_file
from .ambiguity import analyze_ambiguity_file
from .discovery import plan_discovery_file
from .models import canonical_contract_hash
from .prompt_compiler import compile_prompt, validate_prompt_envelope

EXPECTED = {
    "contract": "e3759fb602aad1612f3d8048253f6e6b59f5c0c15d7fc6dd04b529115c0d6049",
    "approved_spec": "41081a5b76bed98c1260044fac827d01731d72fa6a158e32256a11071a6b37d1",
    "input_schema": "4365164d63f141cb0cece5e812666871d2af988369b598a2cdb7337dd82aba9c",
    "envelope_schema": "8549a36497cebe28ad01e136224fe6ed820c9d37a7922a767c1d48ec239a8d24",
    "baseline": "ecab22f1ff6b609e250dea79a7df6d2cb871e4a6dd1db54bb69dbf3d2964d7f7",
    "development_corpus": "97ed9e4009c96bc8e9333bc5ab5fe2d5720ecf3356cd1514004e7df662992836",
    "heldout_corpus": "9598dfcffe90b1d1a2f766a93e65ae9ac189982a9b866d5009238f1a70949138",
    "combined_corpus": "47925572a6a5581b1915b5d82fc62326d0082cfe82b20e03fa47c9570aa3421e",
    "parent_preflight": "1b8ec0a289e5967abb7820705688be5d93e871d08b31f2ff5ba6d176a7c0f51d",
    "schema_preflight": "b4651babc50fe561df9e6149bad7df1158ced2bb6b33e67ca9e7fc675a4314e1",
    "plan": "7a5796af9a10bfcd2dbfaf530ecfce2c75f829524344e740b45bb9b4b3c8f337",
}
PATHS = {
    "approved_spec": "versions/v0.09/SPEC-CREATOR-v0.09.md",
    "input_schema": "schemas/prompt-compilation-input-v1.schema.json",
    "envelope_schema": "schemas/prompt-envelope-v1.schema.json",
    "baseline": "fixtures/prompt-compiler/v0.09/baseline.json",
    "development_corpus": "fixtures/prompt-compiler/v0.09/development.jsonl",
    "heldout_corpus": "fixtures/prompt-compiler/v0.09/heldout.jsonl",
    "combined_corpus": "fixtures/prompt-compiler/v0.09/corpus.jsonl",
    "parent_preflight": "evaluation/v009-preregistration-preflight.json",
    "schema_preflight": "evaluation/v009-schema-preflight.json",
    "plan": "versions/v0.09/EVALUATION-PLAN.json",
    "contract": "versions/v0.09/FROZEN-RELEASE-CONTRACT.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate_v009_corpus(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    hash_checks = {name: _sha(root / PATHS[name]) == expected for name, expected in EXPECTED.items() if name != "contract"}
    contract = json.loads((root / PATHS["contract"]).read_text(encoding="utf-8"))
    hash_checks["contract"] = contract.get("contract_hash") == EXPECTED["contract"] and canonical_contract_hash(contract) == EXPECTED["contract"]

    dev = _load_jsonl(root / PATHS["development_corpus"])
    held = _load_jsonl(root / PATHS["heldout_corpus"])
    rows: list[dict[str, Any]] = []
    dev_acc = dev_exact = held_acc = held_exact = 0
    negative_total = negative_exact = 0
    baseline_missing = compiled_missing = obligation_total = 0
    scope_expansion = missing_critical = prereq_escape = owner_escape = self_cert_escape = invalid_escape = 0
    continuation_total = continuation_exact = 0
    repeat_total = repeat_exact = 0
    over_inclusion = 0
    frozen_excluded_den = 0
    output_schema_errors = 0

    for case in dev + held:
        actual = compile_prompt(case["input"], root=root)
        actual2 = compile_prompt(case["input"], root=root)
        repeat_total += 1
        repeat_exact += int(json.dumps(actual, sort_keys=True, separators=(",", ":")) == json.dumps(actual2, sort_keys=True, separators=(",", ":")))
        schema_diags = validate_prompt_envelope(actual, root=root)
        output_schema_errors += len(schema_diags)
        row = {"case_id": case["case_id"], "partition": case["partition"], "class": case["class"], "actual_status": actual.get("status"), "diagnostic_code": actual.get("diagnostics", [{}])[0].get("code") if actual.get("diagnostics") else None, "output_schema_errors": schema_diags}
        if case["class"] == "accepted":
            exact = actual == case["expected_envelope"]
            row["exact_envelope"] = exact
            if case["partition"] == "development":
                dev_acc += 1; dev_exact += int(exact)
            else:
                held_acc += 1; held_exact += int(exact)
            tokens = case["expected_obligation_tokens"]
            obligation_total += len(tokens)
            bmiss = sum(token not in case["baseline_prompt"] for token in tokens)
            cmiss = sum(token not in (actual.get("prompt_text") or "") for token in tokens)
            baseline_missing += bmiss; compiled_missing += cmiss
            row["baseline_missing_obligations"] = bmiss; row["compiled_missing_obligations"] = cmiss
            declared = set(actual.get("declared_write_scopes", [])); allowed = set(actual.get("allowed_write_scopes", []))
            scope_expansion += len(allowed - declared)
            expected = case["expected_envelope"]
            missing_critical += sum(x not in actual.get("critical_obligations", []) for x in expected["critical_obligations"])
            missing_critical += sum(x not in actual.get("completion_constraints", []) for x in expected["completion_constraints"])
            frozen_excluded_den += len(expected["excluded_context_refs"])
            over_inclusion += len(set(actual.get("included_context_refs", [])) & set(expected["excluded_context_refs"]))
            if case["prompt_kind"] == "continuation":
                continuation_total += 1
                keys = ["task_state","prerequisite_states","completed_evidence_refs","open_blockers","next_permitted_action"]
                continuation_exact += int(all(actual.get(k) == expected.get(k) for k in keys))
        else:
            negative_total += 1
            code = actual.get("diagnostics", [{}])[0].get("code") if actual.get("diagnostics") else None
            exact = actual.get("status") == case["expected_status"] and code == case["expected_diagnostic_code"]
            negative_exact += int(exact); row["negative_exact"] = exact
            defect = case.get("defect_class")
            if defect == "prerequisite_incomplete" and actual.get("status") == "compiled": prereq_escape += 1
            if defect == "owner_decision" and actual.get("status") == "compiled": owner_escape += 1
            if defect == "same_actor_verification" and actual.get("status") == "compiled": self_cert_escape += 1
            if case["expected_status"] == "invalid" and actual.get("status") == "compiled": invalid_escape += 1
        rows.append(row)

    preflight = json.loads((root / PATHS["parent_preflight"]).read_text(encoding="utf-8"))
    lint = lint_file(root / PATHS["approved_spec"])
    ambiguity_payload = analyze_ambiguity_file(root / PATHS["approved_spec"]).as_dict()
    discovery_payload = plan_discovery_file(root / PATHS["approved_spec"]).as_dict()
    spec_ok = lint.ok and ambiguity_payload["summary"]["findings"] == 0 and discovery_payload["summary"]["question_batches"] == 0
    hash_rate = sum(hash_checks.values()) / len(hash_checks) if hash_checks else None
    reduction = ((baseline_missing - compiled_missing) / baseline_missing) if baseline_missing else None
    metrics = {
        "development_prompt_envelope_exact_match_rate": dev_exact / dev_acc if dev_acc else None,
        "heldout_prompt_envelope_exact_match_rate": held_exact / held_acc if held_acc else None,
        "corrective_prompt_proxy_reduction_rate": reduction,
        "negative_case_classification_accuracy": negative_exact / negative_total if negative_total else None,
        "obligation_retention_rate": (obligation_total - compiled_missing) / obligation_total if obligation_total else None,
        "scope_expansion_count": scope_expansion,
        "missing_critical_constraint_count": missing_critical,
        "prerequisite_escape_count": prereq_escape,
        "owner_decision_escape_count": owner_escape,
        "self_certification_violation_count": self_cert_escape,
        "continuation_state_exact_match_rate": continuation_exact / continuation_total if continuation_total else None,
        "deterministic_repeat_rate": repeat_exact / repeat_total if repeat_total else None,
        "context_over_inclusion_rate": over_inclusion / frozen_excluded_den if frozen_excluded_den else None,
        "parent_preflight_rate": 1.0 if preflight.get("all_ok") and preflight.get("case_count") == 75 else 0.0,
        "v009_spec_quality_acceptance_rate": 1.0 if spec_ok else 0.0,
        "invalid_input_escape_count": invalid_escape,
        "frozen_hash_integrity_rate": hash_rate,
        "inherited_regression_pass_rate": None,
        "critical_gate_bypass_count": None,
        "missing_data_count": None,
    }
    missing = [k for k, v in metrics.items() if v is None]
    return {
        "candidate_version": "0.09",
        "hash_checks": hash_checks,
        "counts": {
            "development_cases": len(dev), "development_accepted": dev_acc, "heldout_cases": len(held), "heldout_accepted": held_acc,
            "negative_cases": negative_total, "accepted_obligation_tokens": obligation_total, "baseline_missing_obligations": baseline_missing,
            "compiled_missing_obligations": compiled_missing, "continuation_accepted_cases": continuation_total, "expected_excluded_context_refs": frozen_excluded_den,
            "output_schema_error_count": output_schema_errors,
        },
        "metrics": metrics,
        "rows": rows,
        "missing_data": missing,
        "spec_quality": {"lint_ok": lint.ok, "ambiguity_findings": ambiguity_payload["summary"]["findings"], "discovery_question_batches": discovery_payload["summary"]["question_batches"]},
    }


EXPECTED_0092 = {
    "contract": "e0f91282e131e64c8b5a6407362e889f7feaa65c161d1847048ca04a644b1888",
    "approved_spec": "fff55af89386e3750af3c86fd37f922a52e9423186a02f269997ee2a52f3a68b",
    "input_schema": "4365164d63f141cb0cece5e812666871d2af988369b598a2cdb7337dd82aba9c",
    "envelope_schema": "8549a36497cebe28ad01e136224fe6ed820c9d37a7922a767c1d48ec239a8d24",
    "baseline": "ecab22f1ff6b609e250dea79a7df6d2cb871e4a6dd1db54bb69dbf3d2964d7f7",
    "development_corpus": "d4e6b29a4891dd8af4de5474e145a2bb631ccc574ea58770db4c0018044cdd54",
    "heldout_corpus": "ac355ba31a6a818e6da36eb4695023406a01d0408b153c8ba7258bc2e4858c3a",
    "combined_corpus": "5e63cb9c90fa0f46fe876fab1b36dfc705ba0f3d4ec27dfc2fb93cc63dc6c8ec",
    "parent_preflight": "3e07a83f0440f7448603f34c85acee3ad4ba28455432e00ff09d8383fc1632fd",
    "schema_preflight": "0e2c0f1ba60b53a2596012570679c198bb8cd62a954fc11e82dec077925b390d",
    "contrast_preflight": "0ea91647d6626da4063c1d1cc15cb6746f89ce12627864ae0429f0801fb798d6",
    "prefreeze_transaction": "73e302ae7b76f9a6938eb974bd2a49781be581e70b32030bc231ad77bd1f2ddc",
    "plan": "8e0601991928641fc4559d13b96a7293df9da3a7832792c33fc74b17293350e6",
}
PATHS_0092 = {
    "approved_spec": "versions/v0.09.2/SPEC-CREATOR-v0.09.2.md",
    "input_schema": "schemas/prompt-compilation-input-v1.schema.json",
    "envelope_schema": "schemas/prompt-envelope-v1.schema.json",
    "baseline": "fixtures/prompt-compiler/v0.09.2/baseline.json",
    "development_corpus": "fixtures/prompt-compiler/v0.09.2/development.jsonl",
    "heldout_corpus": "fixtures/prompt-compiler/v0.09.2/heldout.jsonl",
    "combined_corpus": "fixtures/prompt-compiler/v0.09.2/corpus.jsonl",
    "parent_preflight": "evaluation/v0092-preregistration-preflight.json",
    "schema_preflight": "evaluation/v0092-schema-preflight.json",
    "contrast_preflight": "evaluation/v0092-benchmark-contrast-preflight.json",
    "prefreeze_transaction": "evaluation/v0092-prefreeze-transaction-final.json",
    "plan": "versions/v0.09.2/EVALUATION-PLAN.json",
    "contract": "versions/v0.09.2/FROZEN-RELEASE-CONTRACT.json",
}


def evaluate_v0092_corpus(root: str | Path = ".") -> dict[str, Any]:
    """Evaluate the immutable v0.09.2 retry corpus without imputing release-process metrics."""
    root = Path(root)
    hash_checks = {
        name: _sha(root / PATHS_0092[name]) == expected
        for name, expected in EXPECTED_0092.items()
        if name != "contract"
    }
    contract = json.loads((root / PATHS_0092["contract"]).read_text(encoding="utf-8"))
    hash_checks["contract"] = (
        contract.get("contract_hash") == EXPECTED_0092["contract"]
        and canonical_contract_hash(contract) == EXPECTED_0092["contract"]
    )

    dev = _load_jsonl(root / PATHS_0092["development_corpus"])
    held = _load_jsonl(root / PATHS_0092["heldout_corpus"])
    rows: list[dict[str, Any]] = []
    dev_acc = dev_exact = held_acc = held_exact = 0
    negative_total = negative_exact = 0
    baseline_missing = compiled_missing = obligation_total = 0
    scope_expansion = missing_critical = prereq_escape = owner_escape = self_cert_escape = invalid_escape = 0
    continuation_total = continuation_exact = 0
    repeat_total = repeat_exact = 0
    over_inclusion = 0
    frozen_excluded_den = 0
    output_schema_errors = 0

    for case in dev + held:
        actual = compile_prompt(case["input"], root=root)
        actual2 = compile_prompt(case["input"], root=root)
        repeat_total += 1
        repeat_exact += int(json.dumps(actual, sort_keys=True, separators=(",", ":")) == json.dumps(actual2, sort_keys=True, separators=(",", ":")))
        schema_diags = validate_prompt_envelope(actual, root=root)
        output_schema_errors += len(schema_diags)
        row = {
            "case_id": case["case_id"],
            "partition": case["partition"],
            "class": case["class"],
            "actual_status": actual.get("status"),
            "diagnostic_code": actual.get("diagnostics", [{}])[0].get("code") if actual.get("diagnostics") else None,
            "output_schema_errors": schema_diags,
        }
        if case["class"] == "accepted":
            exact = actual == case["expected_envelope"]
            row["exact_envelope"] = exact
            if case["partition"] == "development":
                dev_acc += 1
                dev_exact += int(exact)
            else:
                held_acc += 1
                held_exact += int(exact)
            tokens = case["expected_obligation_tokens"]
            obligation_total += len(tokens)
            bmiss = sum(token not in case["baseline_prompt"] for token in tokens)
            cmiss = sum(token not in (actual.get("prompt_text") or "") for token in tokens)
            baseline_missing += bmiss
            compiled_missing += cmiss
            row["baseline_missing_obligations"] = bmiss
            row["compiled_missing_obligations"] = cmiss
            declared = set(actual.get("declared_write_scopes", []))
            allowed = set(actual.get("allowed_write_scopes", []))
            scope_expansion += len(allowed - declared)
            expected = case["expected_envelope"]
            missing_critical += sum(x not in actual.get("critical_obligations", []) for x in expected["critical_obligations"])
            missing_critical += sum(x not in actual.get("completion_constraints", []) for x in expected["completion_constraints"])
            frozen_excluded_den += len(expected["excluded_context_refs"])
            over_inclusion += len(set(actual.get("included_context_refs", [])) & set(expected["excluded_context_refs"]))
            if case["prompt_kind"] == "continuation":
                continuation_total += 1
                keys = ["task_state", "prerequisite_states", "completed_evidence_refs", "open_blockers", "next_permitted_action"]
                continuation_exact += int(all(actual.get(k) == expected.get(k) for k in keys))
        else:
            negative_total += 1
            code = actual.get("diagnostics", [{}])[0].get("code") if actual.get("diagnostics") else None
            exact = actual.get("status") == case["expected_status"] and code == case["expected_diagnostic_code"]
            negative_exact += int(exact)
            row["negative_exact"] = exact
            defect = case.get("defect_class")
            if defect == "prerequisite_incomplete" and actual.get("status") == "compiled":
                prereq_escape += 1
            if defect == "owner_decision" and actual.get("status") == "compiled":
                owner_escape += 1
            if defect == "same_actor_verification" and actual.get("status") == "compiled":
                self_cert_escape += 1
            if case["expected_status"] == "invalid" and actual.get("status") == "compiled":
                invalid_escape += 1
        rows.append(row)

    preflight = json.loads((root / PATHS_0092["parent_preflight"]).read_text(encoding="utf-8"))
    contrast = json.loads((root / PATHS_0092["contrast_preflight"]).read_text(encoding="utf-8"))
    transaction = json.loads((root / PATHS_0092["prefreeze_transaction"]).read_text(encoding="utf-8"))
    lint = lint_file(root / PATHS_0092["approved_spec"])
    ambiguity_payload = analyze_ambiguity_file(root / PATHS_0092["approved_spec"]).as_dict()
    discovery_payload = plan_discovery_file(root / PATHS_0092["approved_spec"]).as_dict()
    spec_ok = lint.ok and ambiguity_payload["summary"]["findings"] == 0 and discovery_payload["summary"]["question_batches"] == 0
    hash_rate = sum(hash_checks.values()) / len(hash_checks) if hash_checks else None
    reduction = ((baseline_missing - compiled_missing) / baseline_missing) if baseline_missing else None
    metrics = {
        "development_prompt_envelope_exact_match_rate": dev_exact / dev_acc if dev_acc else None,
        "heldout_prompt_envelope_exact_match_rate": held_exact / held_acc if held_acc else None,
        "corrective_prompt_proxy_reduction_rate": reduction,
        "negative_case_classification_accuracy": negative_exact / negative_total if negative_total else None,
        "obligation_retention_rate": (obligation_total - compiled_missing) / obligation_total if obligation_total else None,
        "scope_expansion_count": scope_expansion,
        "missing_critical_constraint_count": missing_critical,
        "prerequisite_escape_count": prereq_escape,
        "owner_decision_escape_count": owner_escape,
        "self_certification_violation_count": self_cert_escape,
        "continuation_state_exact_match_rate": continuation_exact / continuation_total if continuation_total else None,
        "deterministic_repeat_rate": repeat_exact / repeat_total if repeat_total else None,
        "context_over_inclusion_rate": over_inclusion / frozen_excluded_den if frozen_excluded_den else None,
        "parent_preflight_rate": 1.0 if preflight.get("all_ok") and preflight.get("case_count") == 75 else 0.0,
        "v0092_spec_quality_acceptance_rate": 1.0 if spec_ok else 0.0,
        "invalid_input_escape_count": invalid_escape,
        "frozen_hash_integrity_rate": hash_rate,
        "inherited_regression_pass_rate": None,
        "critical_gate_bypass_count": None,
        "missing_data_count": None,
        "benchmark_contrast_preflight_rate": contrast.get("rate") if contrast.get("all_ok") else 0.0,
        "preregistration_precondition_pass_rate": 1.0 if transaction.get("all_ok") and all(transaction.get("checks", {}).values()) else 0.0,
    }
    missing = [k for k, v in metrics.items() if v is None]
    return {
        "candidate_version": "0.09.2",
        "contract_id": contract.get("contract_id"),
        "hash_checks": hash_checks,
        "counts": {
            "development_cases": len(dev),
            "development_accepted": dev_acc,
            "heldout_cases": len(held),
            "heldout_accepted": held_acc,
            "negative_cases": negative_total,
            "accepted_obligation_tokens": obligation_total,
            "baseline_missing_obligations": baseline_missing,
            "compiled_missing_obligations": compiled_missing,
            "continuation_accepted_cases": continuation_total,
            "expected_excluded_context_refs": frozen_excluded_den,
            "output_schema_error_count": output_schema_errors,
        },
        "metrics": metrics,
        "rows": rows,
        "missing_data": missing,
        "spec_quality": {
            "lint_ok": lint.ok,
            "ambiguity_findings": ambiguity_payload["summary"]["findings"],
            "discovery_question_batches": discovery_payload["summary"]["question_batches"],
        },
    }
