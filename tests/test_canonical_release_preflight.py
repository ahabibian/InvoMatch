from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs/architecture/CANONICAL_RELEASE_SUBJECT_0_1_0.json"
SPEC = importlib.util.spec_from_file_location(
    "canonical_release_preflight", ROOT / "scripts/canonical_release_preflight.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_binds_exact_source_and_is_deterministic():
    manifest = _manifest()
    first = MODULE.validate_manifest(ROOT, manifest)
    second = MODULE.validate_manifest(ROOT, manifest)
    assert first == second
    assert first["source_sha"] == manifest["source"]["sha"]
    assert first["source_archive_sha256"] == manifest["package"]["sha256"]


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (("source", "sha"), "34f7171cbf05495473b4f539fe818533cbd4b62f", "mismatch"),
        (("package", "sha256"), "0" * 64, "source_archive_sha256 mismatch"),
        (("release", "version"), "9.9.9", "version mismatch"),
    ],
)
def test_manifest_mismatches_fail_preflight(path, value, message):
    manifest = _manifest()
    manifest[path[0]][path[1]] = value
    with pytest.raises(MODULE.PreflightError, match=message):
        MODULE.validate_manifest(ROOT, manifest)


def test_repository_state_requires_preexisting_tag_and_detects_conflicts():
    manifest = _manifest()
    with pytest.raises(MODULE.PreflightError, match="pre-existing tag"):
        MODULE.validate_repository_state(manifest, {"tags": {}, "releases": {}})

    conflicting = {"tags": {manifest["release"]["tag"]: "f" * 40}, "releases": {}}
    with pytest.raises(MODULE.PreflightError, match="conflicting source SHA"):
        MODULE.validate_repository_state(manifest, conflicting)


def test_repository_state_distinguishes_new_release_from_exact_replay():
    manifest = _manifest()
    tag = manifest["release"]["tag"]
    source_sha = manifest["source"]["sha"]
    fresh = {"tags": {tag: source_sha}, "releases": {}}
    assert MODULE.validate_repository_state(manifest, fresh) == "ready-for-fresh-authorization-review"

    replay = copy.deepcopy(fresh)
    replay["releases"][tag] = {
        "target_sha": source_sha,
        "manifest_identity_sha256": manifest["manifest"]["identity_sha256"],
    }
    assert MODULE.validate_repository_state(manifest, replay) == "exact-replay-already-complete"


def test_preflight_workflow_is_manual_read_only_and_non_mutating():
    workflow = (ROOT / ".github/workflows/canonical-release-preflight.yml").read_text(
        encoding="utf-8"
    )
    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "push:" not in workflow
    assert "pull_request:" not in workflow
    assert "contents: write" not in workflow
    assert "gh release create" not in workflow
