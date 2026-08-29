from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping, Any

class LifecycleResolutionError(ValueError):
    pass

def _matches(pred: Mapping[str, Any], blockers: set[str]) -> bool:
    kind=pred.get("kind")
    if kind=="empty": return not blockers
    if kind=="nonempty": return bool(blockers)
    if kind=="contains_any": return bool(blockers.intersection(pred.get("tokens", [])))
    raise LifecycleResolutionError(f"unknown blocker predicate: {kind}")

def derive_next_action(rules_document: Mapping[str, Any], state: str, blockers: Iterable[str]) -> str:
    """Derive exactly one next action from state + blocker tokens.

    Expected answers in fixtures are deliberately not accepted as inputs.
    Lowest numeric priority wins; no match or a tied winning priority fails closed.
    """
    blocker_set=set(blockers)
    matches=[r for r in rules_document.get("rules",[]) if r.get("state")==state and _matches(r.get("blocker_predicate",{}),blocker_set)]
    if not matches:
        raise LifecycleResolutionError(f"no lifecycle rule for state={state} blockers={sorted(blocker_set)}")
    best=min(int(r["priority"]) for r in matches)
    winners=[r for r in matches if int(r["priority"])==best]
    if len(winners)!=1:
        raise LifecycleResolutionError(f"ambiguous lifecycle rules at priority {best}: {[r.get('rule_id') for r in winners]}")
    return str(winners[0]["action"])
