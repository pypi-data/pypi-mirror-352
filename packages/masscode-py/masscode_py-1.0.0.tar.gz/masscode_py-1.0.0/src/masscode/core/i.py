from masscode.model.db import DB, Tag, Folder, Snippet
import typing


class IDB:
    @property
    def db(self) -> DB:
        pass

    @property
    def tags(self) -> list[Tag]:
        pass

    @property
    def snippets(self) -> list[Snippet]:
        pass

    @property
    def folders(self) -> list[Folder]:
        pass

    def get_folder(
        self, id: str, default: Folder | None = None, raise_error: bool = True
    ) -> Folder | None:
        for folder in self.folders:
            if folder["id"] == id:
                return folder
        if raise_error:
            raise ValueError(f"Folder with id {id} not found")
        return default

    def get_snippet(
        self, id: str, default: Snippet | None = None, raise_error: bool = True
    ) -> Snippet | None:
        for snippet in self.snippets:
            if snippet["id"] == id:
                return snippet
        if raise_error:
            raise ValueError(f"Snippet with id {id} not found")
        return default

    def get_tag(
        self, id: str, default: Tag | None = None, raise_error: bool = True
    ) -> Tag | None:
        for tag in self.tags:
            if tag["id"] == id:
                return tag
        if raise_error:
            raise ValueError(f"Tag with id {id} not found")
        return default

    def filter_folder(self, **kwargs: typing.Unpack[Folder]) -> list[Folder]:
        return [
            folder
            for folder in self.folders
            if all(getattr(folder, key) == value for key, value in kwargs.items())
        ]

    def filter_snippet(self, **kwargs: typing.Unpack[Snippet]) -> list[Snippet]:
        return [
            snippet
            for snippet in self.snippets
            if all(getattr(snippet, key) == value for key, value in kwargs.items())
        ]

    def filter_tag(self, **kwargs: typing.Unpack[Tag]) -> list[Tag]:
        return [
            tag
            for tag in self.tags
            if all(getattr(tag, key) == value for key, value in kwargs.items())
        ]

    def query_tag(self, query, limit: int = -1) -> list[Tag]:
        query._db = self
        results = []
        for tag in self.tags:
            if query.match(tag):
                results.append(tag)
            if limit != -1 and len(results) >= limit:
                break
        return results

    def query_folder(self, query, limit: int = -1) -> list[Folder]:
        query._db = self
        results = []
        for folder in self.folders:
            if query.match(folder):
                results.append(folder)
            if limit != -1 and len(results) >= limit:
                break
        return results

    def query_snippet(self, query, limit: int = -1) -> list[Snippet]:
        query._db = self
        results = []
        for snippet in self.snippets:
            if query.match(snippet):
                results.append(snippet)
            if limit != -1 and len(results) >= limit:
                break
        return results
