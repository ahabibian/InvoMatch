from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "release_manifest_dry_run.py"

spec = importlib.util.spec_from_file_location("release_manifest_dry_run", SCRIPT_PATH)
assert spec is not None
release_manifest_dry_run = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(release_manifest_dry_run)


def test_manifest_preview_is_dry_run_and_preview_only() -> None:
    manifest = release_manifest_dry_run.build_manifest_preview(
        Path("."),
        source_identity={
            "branch": "main",
            "commit_sha": "abc123",
            "working_tree_clean": True,
        },
    )

    assert manifest["dry_run"] is True
    assert manifest["package_status"] == "preview"
    assert manifest["schema_version"] == "invomatch.package_manifest_dry_run.v1"


def test_manifest_preview_contains_expected_manifest_fields() -> None:
    manifest = release_manifest_dry_run.build_manifest_preview(
        Path("."),
        source_identity={
            "branch": "main",
            "commit_sha": "abc123",
            "working_tree_clean": True,
        },
    )

    expected_fields = set(manifest["expected_manifest_fields"])

    assert "package_identity" in expected_fields
    assert "source_identity" in expected_fields
    assert "evidence_reference" in expected_fields
    assert "included_components" in expected_fields
    assert "excluded_components" in expected_fields
    assert "build_environment_assumptions" in expected_fields
    assert "reproducibility_notes" in expected_fields
    assert "non_deployment_boundary" in expected_fields


def test_manifest_preview_keeps_all_non_deployment_flags_false() -> None:
    manifest = release_manifest_dry_run.build_manifest_preview(
        Path("."),
        source_identity={
            "branch": "main",
            "commit_sha": "abc123",
            "working_tree_clean": True,
        },
    )

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


def test_default_output_path_is_local_preview_not_release_artifact() -> None:
    output_path = release_manifest_dry_run.DEFAULT_OUTPUT_PATH.as_posix()

    assert output_path == "output/local/release_manifest_dry_run/package_manifest_preview.json"
    assert "release_manifest_dry_run" in output_path
    assert "artifact" not in output_path
    assert "dist" not in output_path
    assert "release" not in Path(output_path).name


def test_write_manifest_preview_writes_json_to_requested_local_path(tmp_path: Path) -> None:
    manifest = release_manifest_dry_run.build_manifest_preview(
        Path("."),
        source_identity={
            "branch": "main",
            "commit_sha": "abc123",
            "working_tree_clean": True,
        },
    )

    output_path = tmp_path / "local_preview" / "package_manifest_preview.json"

    written_path = release_manifest_dry_run.write_manifest_preview(manifest, output_path)

    assert written_path == output_path
    assert output_path.exists()
    assert '"dry_run": true' in output_path.read_text(encoding="utf-8")
    assert '"package_status": "preview"' in output_path.read_text(encoding="utf-8")
