from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import BinaryIO


class DownloadMode(StrEnum):
    DIRECT_STREAM = "DIRECT_STREAM"
    REDIRECT_URL = "REDIRECT_URL"


@dataclass(frozen=True)
class StoredArtifactRef:
    backend: str
    key: str
    size: int | None = None


@dataclass(frozen=True)
class DownloadHandle:
    mode: DownloadMode
    url: str | None = None


class ArtifactStorage(ABC):
    @abstractmethod
    def save_bytes(
        self,
        key: str,
        content: bytes,
        content_type: str,
    ) -> StoredArtifactRef:
        raise NotImplementedError

    @abstractmethod
    def open_read(self, key: str) -> BinaryIO:
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_download_handle(self, key: str) -> DownloadHandle:
        raise NotImplementedError