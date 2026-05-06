from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "release_manifest_dry_run.py"

spec = importlib.util.spec_from_file_location("release_manifest_dry_run", SCRIPT_PATH)
assert spec is not None
release_manifest_dry_run = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(release_manifest_dry_run)


def _manifest() -> dict:
    return release_manifest_dry_run.build_manifest_preview(
        Path("."),
        source_identity={
            "branch": "main",
            "commit_sha": "abc123",
            "working_tree_clean": True,
        },
    )


def test_manifest_preview_is_dry_run_and_preview_only() -> None:
    manifest = _manifest()

    assert manifest["dry_run"] is True
    assert manifest["package_status"] == "preview"
    assert manifest["schema_version"] == "invomatch.package_manifest_dry_run.v1"
    assert manifest["package_identity"]["package_status"] == "preview"
    assert manifest["package_identity"]["package_type"] == "dry-run-preview"


def test_manifest_preview_contains_required_top_level_content_sections() -> None:
    manifest = _manifest()

    required_sections = [
        "package_identity",
        "source_identity",
        "evidence_reference",
        "included_components",
        "excluded_components",
        "build_environment_assumptions",
        "reproducibility_notes",
        "non_deployment_boundary",
    ]

    for section in required_sections:
        assert section in manifest
        assert manifest[section] not in ({}, [], None)


def test_manifest_preview_expected_manifest_fields_match_required_sections() -> None:
    manifest = _manifest()

    assert manifest["expected_manifest_fields"] == [
        "package_identity",
        "source_identity",
        "evidence_reference",
        "included_components",
        "excluded_components",
        "build_environment_assumptions",
        "reproducibility_notes",
        "non_deployment_boundary",
    ]


def test_manifest_preview_deterministic_contract_fields_are_stable() -> None:
    first = _manifest()
    second = _manifest()

    assert first == second
    assert first["package_identity"]["package_id"] == "preview-not-created"
    assert first["package_identity"]["package_created_at"] == "not-created-in-dry-run"
    assert first["evidence_reference"]["validation_status"] == "not-executed-by-dry-run"
    assert first["build_environment_assumptions"]["shell"] == "PowerShell"
    assert first["reproducibility_notes"]["generated_artifact_reproducibility"] == (
        "not-applicable-in-dry-run"
    )


def test_manifest_preview_keeps_all_non_deployment_flags_false() -> None:
    manifest = _manifest()

    boundary = manifest["non_deployment_boundary"]

    assert boundary["creates_package_archive"] is False
    assert boundary["publishes_artifacts"] is False
    assert boundary["creates_docker_image"] is False
    assert boundary["creates_git_tag"] is False
    assert boundary["creates_github_release"] is False
    assert boundary["deploys"] is False
    assert boundary["modifies_ci"] is False
    assert boundary["writes_release_state_to_database"] is False
    assert boundary["promotes_environment"] is False
    assert set(boundary.values()) == {False}


def test_manifest_preview_declares_included_and_excluded_components() -> None:
    manifest = _manifest()

    included = manifest["included_components"]
    excluded = manifest["excluded_components"]

    assert included["backend_source"]["included"] is True
    assert included["backend_tests"]["path"] == "tests/"
    assert included["frontend_source"]["path"] == "ui/invomatch-ui/src/"
    assert included["release_evidence_index"]["preview_only"] is True

    assert excluded["local_runtime_databases"]["excluded"] is True
    assert excluded["dependency_caches"]["excluded"] is True
    assert excluded["deployment_artifacts"]["excluded"] is True
    assert excluded["public_release_objects"]["excluded"] is True


def test_manifest_preview_is_json_serializable() -> None:
    manifest = _manifest()

    encoded = json.dumps(manifest, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded == manifest
    assert decoded["dry_run"] is True
    assert decoded["package_status"] == "preview"


def test_default_output_path_is_local_preview_not_release_artifact() -> None:
    output_path = release_manifest_dry_run.DEFAULT_OUTPUT_PATH.as_posix()

    assert output_path == "output/local/release_manifest_dry_run/package_manifest_preview.json"
    assert "release_manifest_dry_run" in output_path
    assert "artifact" not in output_path
    assert "dist" not in output_path
    assert "release" not in Path(output_path).name


def test_write_manifest_preview_writes_json_to_requested_local_path(tmp_path: Path) -> None:
    manifest = _manifest()

    output_path = tmp_path / "local_preview" / "package_manifest_preview.json"

    written_path = release_manifest_dry_run.write_manifest_preview(manifest, output_path)

    assert written_path == output_path
    assert output_path.exists()
    written_text = output_path.read_text(encoding="utf-8")
    assert '"dry_run": true' in written_text
    assert '"package_status": "preview"' in written_text
    assert '"package_identity"' in written_text
    assert '"included_components"' in written_text
    assert '"excluded_components"' in written_text


def test_manifest_schema_validator_accepts_current_preview() -> None:
    manifest = _manifest()

    release_manifest_dry_run.validate_manifest_preview(manifest)


def test_manifest_schema_validator_rejects_missing_top_level_section() -> None:
    manifest = copy.deepcopy(_manifest())
    del manifest["package_identity"]

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc) == (
            "manifest schema invalid: missing required field package_identity"
        )
    else:
        raise AssertionError("Expected manifest schema validation to fail")


def test_manifest_schema_validator_rejects_missing_nested_package_identity_field() -> None:
    manifest = copy.deepcopy(_manifest())
    del manifest["package_identity"]["package_type"]

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc) == (
            "manifest schema invalid: missing required field package_identity.package_type"
        )
    else:
        raise AssertionError("Expected manifest schema validation to fail")


def test_manifest_schema_validator_rejects_missing_source_identity_field() -> None:
    manifest = copy.deepcopy(_manifest())
    del manifest["source_identity"]["commit_sha"]

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc) == (
            "manifest schema invalid: missing required field source_identity.commit_sha"
        )
    else:
        raise AssertionError("Expected manifest schema validation to fail")


def test_manifest_schema_validator_rejects_missing_evidence_reference_field() -> None:
    manifest = copy.deepcopy(_manifest())
    del manifest["evidence_reference"]["validation_status"]

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc) == (
            "manifest schema invalid: missing required field "
            "evidence_reference.validation_status"
        )
    else:
        raise AssertionError("Expected manifest schema validation to fail")


def test_manifest_schema_validator_rejects_unsafe_non_deployment_boundary_flag() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["non_deployment_boundary"]["creates_package_archive"] = True

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc) == (
            "manifest schema invalid: "
            "non_deployment_boundary.creates_package_archive must be false"
        )
    else:
        raise AssertionError("Expected manifest schema validation to fail")


def test_manifest_schema_validator_rejects_wrong_dry_run_value() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["dry_run"] = False

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc) == "manifest schema invalid: dry_run must be true"
    else:
        raise AssertionError("Expected manifest schema validation to fail")


def test_manifest_schema_validator_rejects_wrong_package_status() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["package_status"] = "created"

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc) == "manifest schema invalid: package_status must be preview"
    else:
        raise AssertionError("Expected manifest schema validation to fail")


def test_manifest_schema_validator_rejects_non_json_serializable_manifest() -> None:
    manifest = _manifest()
    manifest["not_json"] = object()

    try:
        release_manifest_dry_run.validate_manifest_preview(manifest)
    except release_manifest_dry_run.ReleaseManifestDryRunError as exc:
        assert str(exc).startswith(
            "manifest schema invalid: manifest must be JSON serializable:"
        )
    else:
        raise AssertionError("Expected manifest schema validation to fail")

def test_cli_schema_failure_returns_non_zero_and_writes_stderr_only(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "should_not_exist.json"
    original_build_manifest_preview = release_manifest_dry_run.build_manifest_preview

    def invalid_manifest(repo_root: Path) -> dict:
        manifest = original_build_manifest_preview(
            repo_root,
            source_identity={
                "branch": "main",
                "commit_sha": "abc123",
                "working_tree_clean": True,
            },
        )
        manifest["dry_run"] = False
        return manifest

    monkeypatch.setattr(
        release_manifest_dry_run,
        "build_manifest_preview",
        invalid_manifest,
    )

    exit_code = release_manifest_dry_run.main(
        [
            "--repo-root",
            str(tmp_path),
            "--write-preview",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "manifest schema invalid: dry_run must be true\n"
    assert not output_path.exists()


def test_cli_valid_stdout_preview_remains_json_and_preview_only(
    capsys,
    tmp_path: Path,
) -> None:
    exit_code = release_manifest_dry_run.main(
        [
            "--repo-root",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    manifest = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert manifest["dry_run"] is True
    assert manifest["package_status"] == "preview"


def test_cli_valid_write_preview_writes_only_requested_local_file(
    capsys,
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "local_preview" / "package_manifest_preview.json"

    exit_code = release_manifest_dry_run.main(
        [
            "--repo-root",
            str(tmp_path),
            "--write-preview",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert "Wrote dry-run package manifest preview to" in captured.out
    assert output_path.exists()

    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    assert manifest["dry_run"] is True
    assert manifest["package_status"] == "preview"
