from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3

FORMAT_VERSION = 1
METADATA_NAME = "pilot-state-backup.json"


class PilotStateError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def verify_state(root: Path) -> dict[str, object]:
    root = root.resolve()
    if not root.is_dir():
        raise PilotStateError(f"state root does not exist: {root}")
    sqlite_files = sorted(root.rglob("*.sqlite3"))
    if not sqlite_files:
        raise PilotStateError("state root contains no SQLite databases")
    for path in sqlite_files:
        try:
            with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
                result = connection.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.Error as exc:
            raise PilotStateError(f"SQLite integrity check failed for {path.name}: {exc}") from exc
        if result is None or result[0] != "ok":
            raise PilotStateError(f"SQLite integrity check failed for {path.name}: {result}")
    return {
        "sqlite_files": [path.relative_to(root).as_posix() for path in sqlite_files],
        "file_count": len(_relative_files(root)),
    }


def create_backup(
    state_root: Path,
    bundle: Path,
    *,
    application_version: str,
    source_commit_sha: str,
    environment: str,
) -> Path:
    state_root = state_root.resolve()
    bundle = bundle.resolve()
    if bundle.exists():
        raise PilotStateError(f"backup destination already exists: {bundle}")
    if state_root == bundle or state_root in bundle.parents:
        raise PilotStateError("backup destination must be outside the active state root")
    integrity = verify_state(state_root)
    payload_root = bundle / "state"
    payload_root.parent.mkdir(parents=True, exist_ok=False)
    shutil.copytree(state_root, payload_root)
    verify_state(payload_root)
    files = {
        path.relative_to(payload_root).as_posix(): _sha256(path)
        for path in _relative_files(payload_root)
    }
    metadata = {
        "format_version": FORMAT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "application_version": application_version,
        "source_commit_sha": source_commit_sha,
        "environment": environment,
        "source_state_root": str(state_root),
        "integrity": integrity,
        "files": files,
        "secrets_included": False,
    }
    (bundle / METADATA_NAME).write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return bundle


def _validate_bundle(bundle: Path) -> tuple[dict[str, object], Path]:
    metadata_path = bundle / METADATA_NAME
    payload_root = bundle / "state"
    if not metadata_path.is_file() or not payload_root.is_dir():
        raise PilotStateError("backup metadata or state payload is missing")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PilotStateError("backup metadata is invalid") from exc
    if metadata.get("format_version") != FORMAT_VERSION:
        raise PilotStateError("unsupported backup format version")
    files = metadata.get("files")
    if not isinstance(files, dict) or not files:
        raise PilotStateError("backup file inventory is invalid")
    actual = {
        path.relative_to(payload_root).as_posix(): _sha256(path)
        for path in _relative_files(payload_root)
    }
    if actual != files:
        raise PilotStateError("backup content hash verification failed")
    verify_state(payload_root)
    return metadata, payload_root


def restore_backup(bundle: Path, target_root: Path) -> Path:
    bundle = bundle.resolve()
    target_root = target_root.resolve()
    _, payload_root = _validate_bundle(bundle)
    if target_root.exists() and any(target_root.iterdir()):
        raise PilotStateError(f"restore target is not empty: {target_root}")
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(payload_root, target_root, dirs_exist_ok=True)
    verify_state(target_root)
    return target_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Quiesced InvoMatch pilot state operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--state-root", type=Path, required=True)
    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("--state-root", type=Path, required=True)
    backup_parser.add_argument("--bundle", type=Path, required=True)
    backup_parser.add_argument("--application-version", required=True)
    backup_parser.add_argument("--source-commit-sha", required=True)
    backup_parser.add_argument("--environment", required=True)
    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("--bundle", type=Path, required=True)
    restore_parser.add_argument("--target-root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "verify":
        result = verify_state(args.state_root)
    elif args.command == "backup":
        result = {"bundle": str(create_backup(
            args.state_root, args.bundle,
            application_version=args.application_version,
            source_commit_sha=args.source_commit_sha,
            environment=args.environment,
        ))}
    else:
        result = {"target_root": str(restore_backup(args.bundle, args.target_root))}
    print(json.dumps({"status": "ok", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
