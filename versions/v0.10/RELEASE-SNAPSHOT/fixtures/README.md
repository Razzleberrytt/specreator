# v0.03 Validation Fixtures

`invalid/` contains raw parser fixtures used by the automated suite. Semantic fixtures are constructed deterministically in `tests/conftest.py` from one valid minimal workspace and then mutated one invariant at a time. This prevents unrelated fixture drift from hiding the intended failure.
