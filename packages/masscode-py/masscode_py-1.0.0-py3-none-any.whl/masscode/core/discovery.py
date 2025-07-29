from functools import cache, cached_property
import os
from pathlib import Path
from masscode.model.preferences import Preferences
from masscode.utils.proc import get_exe_path as _get_exe_path
from masscode.utils.prop import JSONFileProperty


class _MasscodeDiscovery:
    def __init__(self):
        self.path = Path(os.getenv("APPDATA")) / "massCode" / "v2"
        self.__exe = None

    _preferences = JSONFileProperty[Preferences]("preferences.json", Preferences)

    @property
    def preferences(self) -> Preferences:
        return self._preferences

    @property
    def dbPath(self):
        return Path(self.preferences["storagePath"]) / "db.json"

    @property
    def exe(self):
        if self.__exe is None:
            self.__exe = _get_exe_path()
        return self.__exe

    @exe.setter
    def exe(self, value):
        self.__exe = value


MasscodeDiscovery = _MasscodeDiscovery()


@cache
def get_dbpath() -> Path:
    x = MasscodeDiscovery.dbPath
    assert x.exists(), "db.json does not exist"
    return x


def set_dbpath(path: Path | str):
    if isinstance(path, str):
        path = Path(path)
    assert path.exists(), "path does not exist"
    MasscodeDiscovery.preferences["storagePath"] = str(path)


def get_exe_path() -> Path:
    return MasscodeDiscovery.exe
