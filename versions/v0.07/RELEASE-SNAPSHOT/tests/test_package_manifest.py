from pathlib import Path
import json

from spec_creator.package_manifest import write_package_manifest
from spec_creator.validator import validate_workspace


def test_generated_package_manifest_matches_final_workspace(tmp_path):
    (tmp_path / "README.md").write_text("hello\n")
    write_package_manifest(tmp_path, release_version="x", release_status="test", generated_at_utc="2026-08-24T00:00:00Z")
    report = validate_workspace(tmp_path, validate_package_manifest=True)
    # A minimal temp workspace has no governance artifacts, but package-manifest validation itself is clean.
    assert not [i for i in report.issues if i.code.startswith("PACKAGE_MANIFEST_")]
    (tmp_path / "README.md").write_text("changed\n")
    report = validate_workspace(tmp_path, validate_package_manifest=True)
    assert any(i.code == "PACKAGE_MANIFEST_HASH_MISMATCH" for i in report.issues)
