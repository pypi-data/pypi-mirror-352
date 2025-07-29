# ================

from masscode.core.i import IDB
from masscode.utils.prop import JSONFileProperty
from masscode.model.db import DB, Folder, Snippet, Tag
from pathlib import Path


class MasscodeDBFile(IDB):
    """Reader for massCode database files."""

    def __init__(self, path: str):
        self.path = str(Path(path).parent)  # Directory containing the JSON file
        assert Path(path).suffix == ".json", "path must end with .json"

    _db = JSONFileProperty[DB]("db.json", DB)

    @property
    def db(self) -> DB:
        return self._db

    @property
    def tags(self) -> list[Tag]:
        return self.db["tags"]

    @property
    def snippets(self) -> list[Snippet]:
        return self.db["snippets"]

    @property
    def folders(self) -> list[Folder]:
        return self.db["folders"]
