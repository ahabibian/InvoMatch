from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from invomatch.services.storage.base import (
    ArtifactStorage,
    DownloadHandle,
    DownloadMode,
    StoredArtifactRef,
)


class LocalArtifactStorage(ArtifactStorage):
    def __init__(self, root_directory: str | Path, backend_name: str = "local") -> None:
        self._root_directory = Path(root_directory)
        self._backend_name = backend_name
        self._root_directory.mkdir(parents=True, exist_ok=True)

    def save_bytes(
        self,
        key: str,
        content: bytes,
        content_type: str,
    ) -> StoredArtifactRef:
        normalized_key = self._normalize_key(key)
        target_path = self._path_for_key(normalized_key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)

        return StoredArtifactRef(
            backend=self._backend_name,
            key=normalized_key,
            size=len(content),
        )

    def open_read(self, key: str) -> BinaryIO:
        normalized_key = self._normalize_key(key)
        target_path = self._path_for_key(normalized_key)
        return target_path.open("rb")

    def exists(self, key: str) -> bool:
        normalized_key = self._normalize_key(key)
        target_path = self._path_for_key(normalized_key)
        return target_path.exists()

    def delete(self, key: str) -> None:
        normalized_key = self._normalize_key(key)
        target_path = self._path_for_key(normalized_key)
        if target_path.exists():
            target_path.unlink()

    def build_download_handle(self, key: str) -> DownloadHandle:
        self._normalize_key(key)
        return DownloadHandle(
            mode=DownloadMode.DIRECT_STREAM,
            url=None,
        )

    def _path_for_key(self, key: str) -> Path:
        candidate = (self._root_directory / key).resolve()
        root_resolved = self._root_directory.resolve()

        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError("storage key resolves outside root directory") from exc

        return candidate

    @staticmethod
    def _normalize_key(key: str) -> str:
        normalized = key.strip().replace("\\", "/")
        if not normalized:
            raise ValueError("storage key must not be blank")
        if normalized.startswith("/"):
            raise ValueError("storage key must be relative")
        return normalized