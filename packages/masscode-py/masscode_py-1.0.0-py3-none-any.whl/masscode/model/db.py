from typing import TypedDict, List, Optional


class Folder(TypedDict):
    """Folder structure in the database."""

    id: str
    name: str
    defaultLanguage: str
    parentId: Optional[str]
    isOpen: bool
    isSystem: bool
    createdAt: int
    updatedAt: int


class Content(TypedDict):
    """Code snippet content fragment."""

    label: str
    language: str
    value: str


class Snippet(TypedDict):
    """Code snippet with metadata and content."""

    id: str
    name: str
    folderId: str
    isDeleted: bool
    isFavorites: bool
    tagsIds: List[str]
    content: List[Content]
    createdAt: int
    updatedAt: int
    folder: Folder  # Denormalized folder data


class Tag(TypedDict):
    """Tag for categorizing snippets."""

    id: str
    name: str
    createdAt: int
    updatedAt: int


class DB(TypedDict):
    """Root database structure."""

    folders: List[Folder]
    snippets: List[Snippet]
    tags: List[Tag]


__all__ = ["Folder", "Content", "Snippet", "Tag", "DB"]
