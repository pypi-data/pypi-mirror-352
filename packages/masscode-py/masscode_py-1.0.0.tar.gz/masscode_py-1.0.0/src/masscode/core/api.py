from contextlib import contextmanager
import logging
from time import sleep
import typing
import requests
from typing import Any, Literal

from masscode.core.discovery import MasscodeDiscovery
from masscode.core.i import IDB
from masscode.model.db import DB, Folder, Snippet, Tag
from masscode.utils import load_json, generate_id
from masscode.utils.proc import kill_masscode_1, is_port_in_use, detach_open


class MasscodeApi(IDB):
    """API client for massCode database."""

    API_URL = "http://localhost:3033"
    WAIT_START = 3
    __change_happened = False

    @property
    def db(self) -> DB:
        """Get the current database state."""
        self.__change_happened = False
        if self._db is None:
            self._db = {
                "folders": self.folders(),
                "snippets": self.snippets(),
                "tags": self.tags(),
            }
        return self._db

    @property
    def tags(self) -> list[Tag]:
        """Get all tags."""
        return self._handle_request("get", "tags")

    @property
    def snippets(self) -> list[Snippet]:
        """Get all snippets."""
        return self._handle_request("get", "snippets")

    @property
    def folders(self) -> list[Folder]:
        """Get all folders."""
        return self._handle_request("get", "folders")

    def start_masscode(self) -> None:
        """Start the massCode application."""
        MasscodeDiscovery.exe
        if is_port_in_use(3033):
            logging.info("Port 3033 is already in use.")
            return
        detach_open(MasscodeDiscovery.exe)
        sleep(self.WAIT_START)

    def kill_masscode(self) -> None:
        """Kill the massCode application."""
        kill_masscode_1()
        self._db = None  # Clear cache

    def _handle_request(
        self,
        method: Literal["get", "post", "put", "delete", "patch"],
        path: str,
        data: Any = None,
        params: dict[str, Any] = {},
    ) -> Any:
        """Handle API requests.

        Args:
            method: HTTP method to use
            path: API endpoint path
            data: Optional data to send
            params: Optional query parameters

        Returns:
            Response data

        Raises:
            Exception: If request fails
        """
        MasscodeDiscovery.exe
        logging.debug(f"Request: {method.upper()} {path}")

        match method:
            case "get":
                method_func = requests.get
            case "post":
                method_func = requests.post
                self.__change_happened = True
            case "put":
                method_func = requests.put
                self.__change_happened = True
            case "delete":
                method_func = requests.delete
                self.__change_happened = True
            case "patch":
                method_func = requests.patch
                self.__change_happened = True
            case _:
                raise ValueError(f"Invalid method: {method}")

        response = method_func(f"{self.API_URL}/{path}", json=data, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")

    # CRUD Operations
    def create_folder(self, **kwargs: typing.Unpack[Folder]) -> Folder:
        """Create a new folder."""
        if "id" not in kwargs:
            kwargs["id"] = generate_id()
        folder = Folder(**kwargs)
        return self._handle_request("post", "folders", folder)

    def create_snippet(self, **kwargs: typing.Unpack[Snippet]) -> Snippet:
        """Create a new snippet."""
        if "id" not in kwargs:
            kwargs["id"] = generate_id()
        snippet = Snippet(**kwargs)
        return self._handle_request("post", "snippets", snippet)

    def create_tag(self, **kwargs: typing.Unpack[Tag]) -> Tag:
        """Create a new tag."""
        if "id" not in kwargs:
            kwargs["id"] = generate_id()
        tag = Tag(**kwargs)
        return self._handle_request("post", "tags", tag)

    def update_folder(self, folder: Folder) -> Folder:
        """Update an existing folder."""
        return self._handle_request("put", f"folders/{folder['id']}", folder)

    def update_snippet(self, snippet: Snippet) -> Snippet:
        """Update an existing snippet."""
        return self._handle_request("put", f"snippets/{snippet['id']}", snippet)

    def update_tag(self, tag: Tag) -> Tag:
        """Update an existing tag."""
        return self._handle_request("put", f"tags/{tag['id']}", tag)

    def delete_folder(self, folder_id: str) -> None:
        """Delete a folder."""
        self._handle_request("delete", f"folders/{folder_id}")

    def delete_snippet(self, snippet_id: str) -> None:
        """Delete a snippet."""
        self._handle_request("delete", f"snippets/{snippet_id}")

    def delete_tag(self, tag_id: str) -> None:
        """Delete a tag."""
        self._handle_request("delete", f"tags/{tag_id}")

    def get_folder(self, id: str) -> Folder:
        """Get a folder by ID."""
        return self._handle_request("get", f"folders/{id}")

    def get_snippet(self, id: str) -> Snippet:
        """Get a snippet by ID."""
        return self._handle_request("get", f"snippets/{id}")

    def get_tag(self, id: str) -> Tag:
        """Get a tag by ID."""
        return self._handle_request("get", f"tags/{id}")
