from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_PATH = Path(
    "output/local/release_manifest_dry_run/package_manifest_preview.json"
)

DOCUMENTATION_REFERENCES = {
    "release_pipeline": "docs/architecture/EPIC_32_RELEASE_PIPELINE.md",
    "package_manifest_contract": "docs/architecture/RELEASE_ARTIFACT_PACKAGE_MANIFEST.md",
    "evidence_index": "docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md",
    "dry_run_contract": "docs/architecture/PACKAGE_MANIFEST_DRY_RUN_CONTRACT.md",
}

EXPECTED_MANIFEST_FIELDS = [
    "package_identity",
    "source_identity",
    "evidence_reference",
    "included_components",
    "excluded_components",
    "build_environment_assumptions",
    "reproducibility_notes",
    "non_deployment_boundary",
]

NON_DEPLOYMENT_BOUNDARY = {
    "creates_package_archive": False,
    "publishes_artifacts": False,
    "creates_docker_image": False,
    "creates_git_tag": False,
    "creates_github_release": False,
    "deploys": False,
    "modifies_ci": False,
    "writes_release_state_to_database": False,
    "promotes_environment": False,
}

PACKAGE_IDENTITY_PREVIEW = {
    "package_id": "preview-not-created",
    "package_name": "InvoMatch Release Package Manifest Preview",
    "package_type": "dry-run-preview",
    "package_manifest_version": 1,
    "package_created_at": "not-created-in-dry-run",
    "release_candidate_id": "preview-only",
    "release_identity": {
        "release_name": "preview-only",
        "release_channel": "local-dry-run",
        "release_version": "not-assigned-in-dry-run",
    },
    "package_status": "preview",
}

EVIDENCE_REFERENCE_PREVIEW = {
    "evidence_index_path": DOCUMENTATION_REFERENCES["evidence_index"],
    "evidence_index_version": 1,
    "validation_status": "not-executed-by-dry-run",
    "validation_summary_reference": "not-created-by-dry-run",
    "validation_executed_at": "not-executed-by-dry-run",
    "validation_scope": [
        "manifest-content-contract-preview",
    ],
    "evidence_included_in_package": [],
    "evidence_referenced_only": [
        DOCUMENTATION_REFERENCES["evidence_index"],
    ],
}

INCLUDED_COMPONENTS_PREVIEW = {
    "backend_source": {
        "included": True,
        "path": "src/",
        "preview_only": True,
    },
    "backend_tests": {
        "included": True,
        "path": "tests/",
        "preview_only": True,
    },
    "frontend_source": {
        "included": True,
        "path": "ui/invomatch-ui/src/",
        "preview_only": True,
    },
    "architecture_documentation": {
        "included": True,
        "path": "docs/architecture/",
        "preview_only": True,
    },
    "release_evidence_index": {
        "included": True,
        "path": DOCUMENTATION_REFERENCES["evidence_index"],
        "preview_only": True,
    },
    "package_manifest_contract": {
        "included": True,
        "path": DOCUMENTATION_REFERENCES["package_manifest_contract"],
        "preview_only": True,
    },
}

EXCLUDED_COMPONENTS_PREVIEW = {
    "local_runtime_databases": {
        "excluded": True,
        "examples": [
            "output/local/reconciliation_runs.sqlite3",
            "output/local/review_store.sqlite3",
            "output/local/exports/export_artifacts.sqlite3",
        ],
    },
    "local_preview_outputs": {
        "excluded": True,
        "examples": [
            DEFAULT_OUTPUT_PATH.as_posix(),
        ],
    },
    "dependency_caches": {
        "excluded": True,
        "examples": [
            ".venv/",
            "node_modules/",
            ".pytest_tmp/",
        ],
    },
    "deployment_artifacts": {
        "excluded": True,
        "examples": [
            "Docker images",
            "environment promotion records",
            "deployment credentials",
        ],
    },
    "public_release_objects": {
        "excluded": True,
        "examples": [
            "GitHub Releases",
            "semantic version tags",
        ],
    },
}

BUILD_ENVIRONMENT_ASSUMPTIONS_PREVIEW = {
    "operating_system_family": "Windows-compatible",
    "shell": "PowerShell",
    "python_version": "repo-local-validation-runtime",
    "node_version": "repo-local-validation-runtime",
    "npm_version": "repo-local-validation-runtime",
    "package_manager_assumptions": {
        "python": "pip",
        "frontend": "npm",
    },
    "environment_variables_required": [
        "PYTHONPATH=src",
    ],
    "external_services_required": [],
    "database_assumptions": {
        "runtime_database_creation": "local-only",
        "packaged_database_state": "excluded",
    },
}

REPRODUCIBILITY_NOTES_PREVIEW = {
    "reproducible_from_commit": True,
    "validation_reproducibility": "command-based",
    "generated_artifact_reproducibility": "not-applicable-in-dry-run",
    "local_machine_dependency_notes": [
        "Dry-run preview records source identity but does not create a release package.",
        "Local runtime databases and generated outputs are excluded from the package boundary preview.",
    ],
    "known_non_reproducible_items": [
        "local absolute paths",
        "machine-specific caches",
        "execution timestamps outside this deterministic preview",
    ],
}


class ReleaseManifestDryRunError(RuntimeError):
    """Raised when a dry-run manifest preview cannot be generated safely."""


def _run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise ReleaseManifestDryRunError(
            f"Failed to read git metadata using git {' '.join(args)}: {stderr}"
        )

    return result.stdout.strip()


def read_source_identity(repo_root: Path) -> dict[str, Any]:
    branch = _run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit_sha = _run_git(repo_root, ["rev-parse", "HEAD"])
    status = _run_git(repo_root, ["status", "--porcelain"])

    return {
        "branch": branch,
        "commit_sha": commit_sha,
        "working_tree_clean": status == "",
    }


def build_manifest_preview(
    repo_root: Path,
    source_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    identity = source_identity or read_source_identity(repo_root)

    return {
        "schema_version": "invomatch.package_manifest_dry_run.v1",
        "dry_run": True,
        "package_status": "preview",
        "package_identity": PACKAGE_IDENTITY_PREVIEW,
        "source_identity": identity,
        "evidence_reference": EVIDENCE_REFERENCE_PREVIEW,
        "included_components": INCLUDED_COMPONENTS_PREVIEW,
        "excluded_components": EXCLUDED_COMPONENTS_PREVIEW,
        "build_environment_assumptions": BUILD_ENVIRONMENT_ASSUMPTIONS_PREVIEW,
        "reproducibility_notes": REPRODUCIBILITY_NOTES_PREVIEW,
        "documentation_references": DOCUMENTATION_REFERENCES,
        "expected_manifest_fields": EXPECTED_MANIFEST_FIELDS,
        "non_deployment_boundary": NON_DEPLOYMENT_BOUNDARY,
    }


def write_manifest_preview(manifest: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a local-only dry-run package manifest preview. "
            "This does not create packages, publish artifacts, tag releases, "
            "deploy, modify CI, or write release state."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--write-preview",
        action="store_true",
        help=(
            "Write the preview to the local non-release output path. "
            "Without this flag, the preview is printed to stdout only."
        ),
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Local preview output path used with --write-preview.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest = build_manifest_preview(repo_root)

    if args.write_preview:
        output_path = write_manifest_preview(manifest, repo_root / args.output)
        print(f"Wrote dry-run package manifest preview to {output_path}")
    else:
        print(json.dumps(manifest, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
