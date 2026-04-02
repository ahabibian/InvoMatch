from __future__ import annotations

from pathlib import Path

import pytest

from invomatch.services.storage.base import DownloadMode
from invomatch.services.storage.local_storage import LocalArtifactStorage


def test_local_artifact_storage_save_and_exists_and_read(tmp_path: Path) -> None:
    storage = LocalArtifactStorage(root_directory=tmp_path / "exports")
    key = "exports/run_123/art_001.json"
    content = b'{"ok": true}'

    ref = storage.save_bytes(
        key=key,
        content=content,
        content_type="application/json",
    )

    assert ref.backend == "local"
    assert ref.key == key
    assert ref.size == len(content)
    assert storage.exists(key) is True

    with storage.open_read(key) as handle:
        loaded = handle.read()

    assert loaded == content


def test_local_artifact_storage_delete(tmp_path: Path) -> None:
    storage = LocalArtifactStorage(root_directory=tmp_path / "exports")
    key = "exports/run_123/art_002.json"

    storage.save_bytes(
        key=key,
        content=b"abc",
        content_type="application/json",
    )
    assert storage.exists(key) is True

    storage.delete(key)
    assert storage.exists(key) is False


def test_local_artifact_storage_build_download_handle_is_direct_stream(
    tmp_path: Path,
) -> None:
    storage = LocalArtifactStorage(root_directory=tmp_path / "exports")

    handle = storage.build_download_handle("exports/run_123/art_003.json")

    assert handle.mode == DownloadMode.DIRECT_STREAM
    assert handle.url is None


def test_local_artifact_storage_rejects_blank_key(tmp_path: Path) -> None:
    storage = LocalArtifactStorage(root_directory=tmp_path / "exports")

    with pytest.raises(ValueError):
        storage.save_bytes(
            key="   ",
            content=b"abc",
            content_type="application/json",
        )


def test_local_artifact_storage_rejects_absolute_key(tmp_path: Path) -> None:
    storage = LocalArtifactStorage(root_directory=tmp_path / "exports")

    with pytest.raises(ValueError):
        storage.exists("/absolute/path.json")


def test_local_artifact_storage_rejects_path_escape(tmp_path: Path) -> None:
    storage = LocalArtifactStorage(root_directory=tmp_path / "exports")

    with pytest.raises(ValueError):
        storage.save_bytes(
            key="../outside.json",
            content=b"abc",
            content_type="application/json",
        )