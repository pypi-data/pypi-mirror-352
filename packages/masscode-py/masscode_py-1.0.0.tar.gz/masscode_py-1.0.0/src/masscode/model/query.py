from dataclasses import dataclass
from datetime import datetime
import re
from typing import List, Optional
import typing

from masscode.core.i import IDB
from .db import Tag, Folder, Snippet, Content


@dataclass(slots=True)
class Query:
    _db: IDB | None = None

    def __post_init__(self):
        if isinstance(self.createdAt, datetime):
            self.createdAt = self.createdAt.timestamp() * 1000
        if isinstance(self.updatedAt, datetime):
            self.updatedAt = self.updatedAt.timestamp() * 1000

    def __preparent(self):
        if self.parent is not None:
            if isinstance(self.parent, dict) and all(
                key in self.parent for key in Folder.__annotations__.keys()
            ):
                self.parentId = self.parent["id"]
            elif isinstance(self.parent, FolderQuery):
                assert self._db is not None, "IDB is required"
                self.parentId = self._db.query_folder(self.parent)

    def __pretags(self):
        if self.tags is not None:
            if isinstance(self.tags, TagQuery):
                assert self._db is not None, "IDB is required"
                self.tags = self._db.query_tag(self.tags)
            if isinstance(self.tags, list) and all(
                isinstance(tag, dict)
                and all(key in tag for key in Tag.__annotations__.keys())
                for tag in self.tags
            ):
                self.tagsIds = [tag["id"] for tag in self.tags]

    def match(self, obj: typing.Any, idb: IDB | None = None) -> bool:
        pass


@dataclass(slots=True)
class TagQuery(Query):
    name: str | None = None
    query: str | None = None
    createdAt: int | datetime | None = None
    updatedAt: int | datetime | None = None
    _allowed_uncertainity: int = 0

    def match(self, tag: Tag, idb: IDB | None = None) -> bool:
        return (
            self.__matchName(tag["name"])
            and self.__matchQuery(tag)
            and self.__matchCreatedAt(tag["createdAt"])
            and self.__matchUpdatedAt(tag["updatedAt"])
        )

    def __matchQuery(self, otherDict: dict) -> bool:
        if self.query is None:
            return True

        return eval(self.query, {"x": otherDict})

    def __matchCreatedAt(self, createdAt: int) -> bool:
        if self.createdAt is None:
            return True

        return (
            self.createdAt - self._allowed_uncertainity
            <= createdAt
            <= self.createdAt + self._allowed_uncertainity
        )

    def __matchUpdatedAt(self, updatedAt: int) -> bool:
        if self.updatedAt is None:
            return True

        return (
            self.updatedAt - self._allowed_uncertainity
            <= updatedAt
            <= self.updatedAt + self._allowed_uncertainity
        )

    def __matchName(self, name: str) -> bool:
        if self.name is not None and self.name != name:
            if "*" in self.name and re.match(self.name, name):
                return True
            return False
        return True


@dataclass(slots=True)
class FolderQuery(Query):
    """Query parameters for searching folders."""

    name: str | None = None
    defaultLanguage: str | None = None
    parentId: str | None = None
    parent: typing.Union[Folder, "FolderQuery", None] = None
    isOpen: bool | None = None
    isSystem: bool | None = None
    createdAt: int | datetime | None = None
    updatedAt: int | datetime | None = None
    query: str | None = None
    _allowed_uncertainity: int = 0

    def match(self, folder: Folder, idb: IDB | None = None) -> bool:
        self._Query__preparent()

        return (
            self.__matchName(folder["name"])
            and self.__matchDefaultLanguage(folder["defaultLanguage"])
            and self.__matchParentId(folder["parentId"])
            and self.__matchIsOpen(folder["isOpen"])
            and self.__matchIsSystem(folder["isSystem"])
            and self.__matchCreatedAt(folder["createdAt"])
            and self.__matchUpdatedAt(folder["updatedAt"])
            and self.__matchQuery(folder)
        )

    def __matchName(self, name: str) -> bool:
        if self.name is None:
            return True
        if "*" in self.name:
            return bool(re.match(self.name.replace("*", ".*"), name))
        return self.name == name

    def __matchDefaultLanguage(self, language: str) -> bool:
        return self.defaultLanguage is None or self.defaultLanguage == language

    def __matchParentId(self, parentId: Optional[str]) -> bool:
        return self.parentId is None or self.parentId == parentId

    def __matchIsOpen(self, isOpen: bool) -> bool:
        return self.isOpen is None or self.isOpen == isOpen

    def __matchIsSystem(self, isSystem: bool) -> bool:
        return self.isSystem is None or self.isSystem == isSystem

    def __matchCreatedAt(self, createdAt: int) -> bool:
        if self.createdAt is None:
            return True
        return (
            self.createdAt - self._allowed_uncertainity
            <= createdAt
            <= self.createdAt + self._allowed_uncertainity
        )

    def __matchUpdatedAt(self, updatedAt: int) -> bool:
        if self.updatedAt is None:
            return True
        return (
            self.updatedAt - self._allowed_uncertainity
            <= updatedAt
            <= self.updatedAt + self._allowed_uncertainity
        )

    def __matchQuery(self, otherDict: dict) -> bool:
        if self.query is None:
            return True
        return eval(self.query, {"x": otherDict})


@dataclass(slots=True)
class SnippetQuery(Query):
    """Query parameters for searching snippets."""

    name: str | None = None
    folderId: str | None = None
    folder: typing.Union[Folder, FolderQuery, None] = None
    isDeleted: bool | None = None
    isFavorites: bool | None = None
    tagsIds: List[str] | None = None
    tags: typing.Union[List[Tag], TagQuery, None] = None
    content: List[Content] | None = None
    createdAt: int | datetime | None = None
    updatedAt: int | datetime | None = None
    query: str | None = None
    _allowed_uncertainity: int = 0

    def match(self, snippet: Snippet, idb: IDB | None = None) -> bool:
        self._Query__pretags()
        if self.folder is not None:
            if isinstance(self.folder, dict) and all(
                key in self.folder for key in Folder.__annotations__.keys()
            ):
                self.folderId = self.folder["id"]
            elif isinstance(self.folder, FolderQuery):
                assert self._db is not None, "IDB is required"
                folders = self._db.query_folder(self.folder)
                assert len(folders) >= 1, "FolderQuery must return at least one folder"
                self.folderId = folders[0]["id"]

        return (
            self.__matchName(snippet["name"])
            and self.__matchFolderId(snippet["folderId"])
            and self.__matchIsDeleted(snippet["isDeleted"])
            and self.__matchIsFavorites(snippet["isFavorites"])
            and self.__matchTagsIds(snippet["tagsIds"])
            and self.__matchContent(snippet["content"])
            and self.__matchCreatedAt(snippet["createdAt"])
            and self.__matchUpdatedAt(snippet["updatedAt"])
            and self.__matchQuery(snippet)
        )

    def __matchName(self, name: str) -> bool:
        if self.name is None:
            return True
        if "*" in self.name:
            return bool(re.match(self.name.replace("*", ".*"), name))
        return self.name == name

    def __matchFolderId(self, folderId: str) -> bool:
        return self.folderId is None or self.folderId == folderId

    def __matchIsDeleted(self, isDeleted: bool) -> bool:
        return self.isDeleted is None or self.isDeleted == isDeleted

    def __matchIsFavorites(self, isFavorites: bool) -> bool:
        return self.isFavorites is None or self.isFavorites == isFavorites

    def __matchTagsIds(self, tagsIds: List[str]) -> bool:
        if self.tagsIds is None:
            return True
        return all(tagId in tagsIds for tagId in self.tagsIds)

    def __matchContent(self, content: List[Content]) -> bool:
        if self.content is None:
            return True
        # Match if any content fragment matches all criteria
        return any(
            all(
                (fragment.get("label") == c.get("label") or c.get("label") is None)
                and (
                    fragment.get("language") == c.get("language")
                    or c.get("language") is None
                )
                and (fragment.get("value") == c.get("value") or c.get("value") is None)
                for fragment in content
            )
            for c in self.content
        )

    def __matchCreatedAt(self, createdAt: int) -> bool:
        if self.createdAt is None:
            return True
        return (
            self.createdAt - self._allowed_uncertainity
            <= createdAt
            <= self.createdAt + self._allowed_uncertainity
        )

    def __matchUpdatedAt(self, updatedAt: int) -> bool:
        if self.updatedAt is None:
            return True
        return (
            self.updatedAt - self._allowed_uncertainity
            <= updatedAt
            <= self.updatedAt + self._allowed_uncertainity
        )

    def __matchQuery(self, otherDict: dict) -> bool:
        if self.query is None:
            return True
        return eval(self.query, {"x": otherDict})


__all__ = ["TagQuery", "FolderQuery", "SnippetQuery"]
