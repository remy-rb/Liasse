"""The Archive: the Owner's browsable folder tree, in whatever storage STORAGE_URL points to."""

import posixpath
import re
import unicodedata
from uuid import UUID

from fsspec.core import url_to_fs

INBOX = "Inbox"
ORIGINALS = ".originals"
# Characters that are unsafe on at least one of Windows, macOS, Linux, Drive or S3.
UNSAFE = re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]+')


def safe_name(name: str, fallback: str = "document") -> str:
    """Make a file or folder name safe on every filesystem Liasse may sync to."""
    name = UNSAFE.sub("-", unicodedata.normalize("NFC", name))
    name = re.sub(r"\s+", " ", name).strip(" .-")
    return name[:120].rstrip(" .-") or fallback


class Archive:
    def __init__(self, storage_url: str) -> None:
        self.fs, self.root = url_to_fs(storage_url)

    def _full(self, path: str) -> str:
        return posixpath.join(self.root, path)

    def write(self, path: str, data: bytes) -> None:
        full = self._full(path)
        self.fs.makedirs(posixpath.dirname(full), exist_ok=True)
        with self.fs.open(full, "wb") as file:
            file.write(data)

    def read(self, path: str) -> bytes:
        with self.fs.open(self._full(path), "rb") as file:
            data: bytes = file.read()
            return data

    def exists(self, path: str) -> bool:
        return bool(self.fs.exists(self._full(path)))

    def original_path(self, owner_id: UUID, document_id: UUID, filename: str) -> str:
        return posixpath.join(str(owner_id), ORIGINALS, str(document_id), safe_name(filename))

    def free_path(self, folder: str, stem: str, suffix: str) -> str:
        """A path in `folder` that isn't taken yet, adding -2, -3… to the name if needed."""
        stem = safe_name(stem)
        candidate = posixpath.join(folder, f"{stem}{suffix}")
        number = 2
        while self.exists(candidate):
            candidate = posixpath.join(folder, f"{stem}-{number}{suffix}")
            number += 1
        return candidate

    def inbox_path(self, owner_id: UUID, stem: str) -> str:
        return self.free_path(posixpath.join(str(owner_id), INBOX), stem, ".pdf")
