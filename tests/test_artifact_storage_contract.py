from __future__ import annotations

from invomatch.services.storage.base import (
    ArtifactStorage,
    DownloadHandle,
    DownloadMode,
    StoredArtifactRef,
)


def test_artifact_storage_is_abstract() -> None:
    try:
        ArtifactStorage()  # type: ignore[abstract]
        instantiated = True
    except TypeError:
        instantiated = False

    assert instantiated is False


def test_stored_artifact_ref_shape() -> None:
    ref = StoredArtifactRef(
        backend="local",
        key="exports/run_123/art_001.json",
        size=128,
    )

    assert ref.backend == "local"
    assert ref.key == "exports/run_123/art_001.json"
    assert ref.size == 128


def test_download_handle_shape_for_direct_stream() -> None:
    handle = DownloadHandle(
        mode=DownloadMode.DIRECT_STREAM,
        url=None,
    )

    assert handle.mode == DownloadMode.DIRECT_STREAM
    assert handle.url is None


def test_download_handle_shape_for_redirect() -> None:
    handle = DownloadHandle(
        mode=DownloadMode.REDIRECT_URL,
        url="https://example.test/download/art_001",
    )

    assert handle.mode == DownloadMode.REDIRECT_URL
    assert handle.url == "https://example.test/download/art_001"