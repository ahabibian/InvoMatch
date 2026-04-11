from __future__ import annotations


class FileDecoder:
    def decode(self, content_bytes: bytes) -> str:
        return content_bytes.decode("utf-8", errors="strict")