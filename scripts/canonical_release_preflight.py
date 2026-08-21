from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path
from typing import Any


TAG_PATTERN = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")


class PreflightError(RuntimeError):
    pass


def _git(repo_root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise PreflightError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_file(repo_root: Path, source_sha: str, path: str) -> bytes:
    return _git(repo_root, "show", f"{source_sha}:{path}")


def _canonical_source_archive(repo_root: Path, source_sha: str) -> bytes:
    entries = _git(repo_root, "ls-tree", "-rz", "--full-tree", source_sha).split(b"\0")
    blobs: list[tuple[str, str, str]] = []
    for entry in entries:
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, object_type, object_sha = metadata.decode("ascii").split()
        if object_type == "blob":
            blobs.append(
                (mode, object_sha, raw_path.decode("utf-8", errors="surrogateescape"))
            )

    batch_input = "".join(f"{object_sha}\n" for _, object_sha, _ in blobs).encode("ascii")
    batch_output = _git_with_input(repo_root, batch_input, "cat-file", "--batch")
    batch_reader = io.BytesIO(batch_output)
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w", format=tarfile.GNU_FORMAT) as archive:
        for mode, object_sha, path in blobs:
            header = batch_reader.readline().decode("ascii").strip().split()
            if len(header) != 3 or header[0] != object_sha or header[1] != "blob":
                raise PreflightError(f"unexpected Git batch response for {path}")
            content = batch_reader.read(int(header[2]))
            if batch_reader.read(1) != b"\n":
                raise PreflightError(f"malformed Git batch response for {path}")
            info = tarfile.TarInfo(path)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            if mode == "120000":
                info.type = tarfile.SYMTYPE
                info.mode = 0o777
                info.linkname = content.decode("utf-8", errors="surrogateescape")
                archive.addfile(info)
            else:
                info.mode = 0o755 if mode == "100755" else 0o644
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
    return output.getvalue()


def _git_with_input(repo_root: Path, data: bytes, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=repo_root, input=data, check=False, capture_output=True
    )
    if result.returncode != 0:
        raise PreflightError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def manifest_identity_sha256(manifest: dict[str, Any]) -> str:
    identity = copy.deepcopy(manifest)
    identity.pop("manifest", None)
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256(encoded)


def build_evidence(repo_root: Path, source_sha: str) -> dict[str, Any]:
    resolved_sha = _git(repo_root, "rev-parse", f"{source_sha}^{{commit}}").decode().strip()
    archive = _canonical_source_archive(repo_root, resolved_sha)
    pyproject = _git_file(repo_root, resolved_sha, "pyproject.toml")
    package_lock = _git_file(repo_root, resolved_sha, "ui/invomatch-ui/package-lock.json")
    ci_workflow = _git_file(repo_root, resolved_sha, ".github/workflows/ci.yml")
    version = tomllib.loads(pyproject.decode("utf-8"))["project"]["version"]
    return {
        "source_sha": resolved_sha,
        "version": version,
        "tag": f"v{version}",
        "source_archive_sha256": _sha256(archive),
        "source_archive_size_bytes": len(archive),
        "dependency_lock_sha256": _sha256(package_lock),
        "validation_workflow_sha256": _sha256(ci_workflow),
    }


def validate_manifest(repo_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != "invomatch.canonical_release_subject.v1":
        raise PreflightError("unsupported release-subject manifest schema")
    if manifest.get("repository") != "ahabibian/InvoMatch":
        raise PreflightError("repository identity mismatch")

    evidence = build_evidence(repo_root, manifest["source"]["sha"])
    expected = {
        "version": manifest["release"]["version"],
        "tag": manifest["release"]["tag"],
        "source_archive_sha256": manifest["package"]["sha256"],
        "source_archive_size_bytes": manifest["package"]["size_bytes"],
        "dependency_lock_sha256": manifest["dependencies"]["frontend_lock_sha256"],
        "validation_workflow_sha256": manifest["configuration"]["ci_workflow_sha256"],
    }
    for field, expected_value in expected.items():
        if evidence[field] != expected_value:
            raise PreflightError(
                f"{field} mismatch: expected {expected_value!r}, got {evidence[field]!r}"
            )
    if evidence["source_sha"] != manifest["source"]["sha"]:
        raise PreflightError("source SHA mismatch")
    if not TAG_PATTERN.fullmatch(evidence["tag"]):
        raise PreflightError("release tag does not match the canonical vMAJOR.MINOR.PATCH syntax")
    if manifest["package"]["format"] != "deterministic-git-tree-tar-v1":
        raise PreflightError("unsupported package format")
    if manifest["action"]["category"] != "github-release-with-tag-if-absent":
        raise PreflightError("action category mismatch")
    if manifest["action"].get("requires_preexisting_tag") is not False:
        raise PreflightError("pre-existing tag policy mismatch")
    if manifest["action"].get("creates_tag_if_absent") is not True:
        raise PreflightError("tag-if-absent action mismatch")
    if manifest["action"].get("target_commitish") != evidence["source_sha"]:
        raise PreflightError("target_commitish mismatch")
    if manifest_identity_sha256(manifest) != manifest["manifest"]["identity_sha256"]:
        raise PreflightError("manifest identity digest mismatch")
    return evidence


def validate_repository_state(manifest: dict[str, Any], state: dict[str, Any]) -> str:
    tag = manifest["release"]["tag"]
    source_sha = manifest["source"]["sha"]
    tags = state.get("tags", {})
    releases = state.get("releases", {})

    if tag in tags and tags[tag] != source_sha:
        raise PreflightError(f"existing tag {tag} targets a conflicting source SHA")
    if tag not in releases:
        return "ready-for-fresh-authorization-review"
    if tag not in tags:
        raise PreflightError(f"existing GitHub Release {tag} has no matching tag evidence")
    if releases[tag].get("target_sha") != source_sha:
        raise PreflightError(f"existing GitHub Release {tag} targets a conflicting source SHA")
    if releases[tag].get("manifest_identity_sha256") != manifest["manifest"]["identity_sha256"]:
        raise PreflightError(f"existing GitHub Release {tag} has conflicting manifest evidence")
    return "exact-replay-already-complete"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Non-mutating canonical release preflight")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--repository-state", type=Path)
    args = parser.parse_args(argv)

    try:
        manifest = _load_json(args.manifest)
        evidence = validate_manifest(args.repo_root.resolve(), manifest)
        result = "subject-identity-verified"
        if args.repository_state is not None:
            result = validate_repository_state(manifest, _load_json(args.repository_state))
    except (KeyError, json.JSONDecodeError, OSError, PreflightError) as exc:
        print(f"PREFLIGHT_BLOCKED: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"result": result, "evidence": evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
