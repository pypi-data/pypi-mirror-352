from masscode.core.api import MasscodeApi
from masscode.core.file import MasscodeDBFile


class Model:
    from masscode.model.db import DB, Folder, Snippet, Tag


class Query:
    from masscode.model.query import FolderQuery, SnippetQuery, TagQuery

    folder = FolderQuery
    snippet = SnippetQuery
    tag = TagQuery

    __all__ = ["folder", "snippet", "tag", "FolderQuery", "SnippetQuery", "TagQuery"]
