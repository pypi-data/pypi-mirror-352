from typing import TypedDict, List, Literal, Union


class EditorPreferences(TypedDict):
    wrap: bool
    fontFamily: str
    fontSize: int
    tabSize: int
    trailingComma: Literal["none", "es5", "all"]
    semi: bool
    singleQuote: bool
    highlightLine: bool
    highlightGutter: bool
    matchBrackets: bool


class ScreenshotPreferences(TypedDict):
    background: bool
    gradient: List[str]
    darkMode: bool
    width: int


class MarkdownPreferences(TypedDict):
    presentationScale: float
    codeRenderer: Literal["highlight.js", "prism"]


class Preferences(TypedDict):
    """Main preferences structure for massCode application."""

    storagePath: str
    backupPath: str
    theme: str
    editor: EditorPreferences
    screenshot: ScreenshotPreferences
    markdown: MarkdownPreferences
    language: str


class WindowBounds(TypedDict):
    x: int
    y: int
    width: int
    height: int


class App(TypedDict):
    """Application state and window preferences."""

    bounds: WindowBounds
    sidebarWidth: int
    snippetListWidth: int
    sort: Literal["updatedAt", "createdAt", "name"]
    hideSubfolderSnippets: bool
    compactMode: bool
    dateInstallation: int  # Unix timestamp in milliseconds
    version: str
    nextSupportNotice: int  # Unix timestamp in milliseconds
    prevRemoteNotice: int  # Unix timestamp in milliseconds


__all__ = ["Preferences", "App"]
