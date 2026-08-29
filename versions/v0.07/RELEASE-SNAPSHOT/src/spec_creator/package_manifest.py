from __future__ import annotations

from pathlib import Path
from typing import Iterable
import hashlib
import json

TRANSIENT_DIRS = {".pytest_cache", "__pycache__"}
TRANSIENT_SUFFIXES = {".pyc"}


def _included_file(root: Path, path: Path) -> bool:
    rel = path.relative_to(root)
    if path.name == "PACKAGE-MANIFEST.json":
        return False
    if any(part in TRANSIENT_DIRS for part in rel.parts):
        return False
    if path.suffix in TRANSIENT_SUFFIXES:
        return False
    return path.is_file()


def build_package_manifest(root: str | Path, *, release_version: str, release_status: str, generated_at_utc: str) -> dict:
    root = Path(root)
    files = []
    for path in sorted(root.rglob("*")):
        if not _included_file(root, path):
            continue
        raw = path.read_bytes()
        files.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        })
    return {
        "package": "spec-creator",
        "generated_at_utc": generated_at_utc,
        "release_version": release_version,
        "release_status": release_status,
        "files": files,
    }


def write_package_manifest(root: str | Path, *, release_version: str, release_status: str, generated_at_utc: str) -> Path:
    root = Path(root)
    manifest = build_package_manifest(root, release_version=release_version, release_status=release_status, generated_at_utc=generated_at_utc)
    path = root / "PACKAGE-MANIFEST.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path
