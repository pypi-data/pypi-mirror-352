import os
from typing import TypeVar, Generic, Type, Any
from pathlib import Path

from masscode.utils import load_json, dump_json

T = TypeVar("T")


class JSONFileProperty(Generic[T]):
    """A property descriptor that watches a JSON file and reloads when modified.

    Example:
        class Config:
            path = "path/to/dir"  # Directory containing the JSON file
            db = JSONFileProperty[DB]("db.json", DB)
    """

    def __init__(self, filename: str, type_class: Type[T]):
        self.filename = filename
        self.type_class = type_class
        self._cache: T | None = None
        self._last_mtime: float | None = None
        self._filepath: Path | None = None

    def _get_mtime(self) -> float:
        if self._filepath is None:
            return 0.0
        try:
            return os.path.getmtime(self._filepath)
        except FileNotFoundError:
            return 0.0

    def __get__(self, obj: Any, owner: Any) -> T:
        if obj is None:
            return self  # type: ignore

        if self._filepath is None:
            self._filepath = Path(obj.path) / self.filename

        current_mtime = self._get_mtime()

        if (
            self._cache is None
            or self._last_mtime is None
            or current_mtime != self._last_mtime
        ):
            try:
                self._cache = load_json(self._filepath)  # type: ignore
                self._last_mtime = current_mtime
            except FileNotFoundError:
                self._cache = {}  # type: ignore
                self._last_mtime = 0.0

        return self._cache

    def __set__(self, obj: Any, value: T) -> None:
        if self._filepath is None:
            self._filepath = Path(obj.path) / self.filename

        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        dump_json(value, self._filepath)
        self._cache = value
        self._last_mtime = self._get_mtime()

    def __delete__(self, obj: Any) -> None:
        if self._filepath and self._filepath.exists():
            os.remove(self._filepath)
        self._cache = None
        self._last_mtime = None
