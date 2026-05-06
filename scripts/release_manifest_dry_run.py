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
        "source_identity": identity,
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
