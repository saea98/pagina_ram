from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO, Protocol


class StorageBackend(Protocol):
    def save(self, stream: BinaryIO, key: str) -> None: ...

    def open(self, key: str) -> BinaryIO: ...

    def delete(self, key: str) -> None: ...

    def url(self, key: str) -> str: ...


class LocalStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    def path(self, key: str) -> Path:
        return self._resolve(key)

    def save(self, stream: BinaryIO, key: str) -> None:
        target = self._resolve(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as handle:
            while chunk := stream.read(1024 * 1024):
                handle.write(chunk)

    def open(self, key: str) -> BinaryIO:
        return self._resolve(key).open("rb")

    def delete(self, key: str) -> None:
        target = self._resolve(key)
        if target.is_file():
            target.unlink()

    def url(self, key: str) -> str:
        if key.startswith("public/"):
            return "/media/" + key.removeprefix("public/")
        return ""

    def _resolve(self, key: str) -> Path:
        if key.startswith("/") or ".." in Path(key).parts:
            raise ValueError("Clave de almacenamiento inválida.")
        target = (self.root / key).resolve()
        if not target.is_relative_to(self.root.resolve()):
            raise ValueError("Clave de almacenamiento inválida.")
        return target


def iter_chunks(stream: BinaryIO, size: int = 1024 * 1024) -> Iterator[bytes]:
    while chunk := stream.read(size):
        yield chunk
