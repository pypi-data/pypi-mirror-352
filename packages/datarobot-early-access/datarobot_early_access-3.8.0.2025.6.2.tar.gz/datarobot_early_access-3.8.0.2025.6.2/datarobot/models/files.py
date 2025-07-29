#  Copyright 2025 DataRobot, Inc. and its affiliates.
#
#  All rights reserved.
#
#  DataRobot, Inc. Confidential.
#
#  This is unpublished proprietary source code of DataRobot, Inc.
#  and its affiliates.
#
#  The copyright notice above does not evidence any actual or intended
#  publication of such source code.
from datetime import datetime
from io import IOBase
from typing import Dict, List, Optional, Type

import dateutil
import trafaret as t

from datarobot._compat import Int, String
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.utils import assert_single_parameter
from datarobot.utils.waiters import wait_for_async_resolution

_files_schema = t.Dict(
    {
        t.Key("id"): String,
        t.Key("name"): String,
        t.Key("description", optional=True): t.Or(String, t.Null),
        t.Key("type"): String,
        t.Key("tags"): t.List(String),
        t.Key("num_files"): Int(),
        t.Key("from_archive"): t.Bool(),
        t.Key("created_at"): t.Call(dateutil.parser.parse),
        t.Key("created_by", optional=True): t.Or(String, t.Null),
    }
)


class File(APIObject):
    """
    Represents a file in the DataRobot catalog.

    This class provides functionality to interact with files stored in the DataRobot catalog,
    including retrieving and updating file information and downloading file contents.

    Attributes
    ----------
    id: str
        The unique identifier for the file.
    name: str
        The name of the file.
    type: str
        The type of file.
    tags: List[str]
        A list of tags associated with the file.
    num_files: int
        The number of files in the archive (if the file is an archive).
    from_archive: bool
        Whether the file was extracted from an archive.
    created_at: datetime
        A timestamp from when the file was created.
    created_by: str
        The username of the user who created the file.
    description: Optional[str]
        An optional description of the file.
    """

    _converter = _files_schema.allow_extra("*")
    _path = "files/"

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        tags: List[str],
        num_files: int,
        from_archive: bool,
        created_at: datetime,
        created_by: str,
        description: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.tags = tags
        self.num_files = num_files
        self.from_archive = from_archive
        self.created_at = created_at
        self.created_by = created_by
        self.description = description

    @classmethod
    def get(cls: Type["File"], file_id: str) -> "File":
        """Get information about a file.

        Parameters
        ----------
        file_id: str
            the id of the file

        Returns
        -------
        file: File
            the queried file
        """

        path = f"catalogItems/{file_id}/"
        return cls.from_location(path)

    def download(self, file_path: Optional[str] = None, filelike: Optional[IOBase] = None) -> None:
        """
        Retrieves uploaded file contents.
        Writes it to either the file or a file-like object that can write bytes.

        Only one of file_path or filelike can be provided. If a file-like object is
        provided, the user is responsible for closing it when they are done.

        The user must also have permission to download data.

        Parameters
        ----------
        file_path: Optional[str]
            The destination to write the file to.
        filelike: Optional[IOBase]
            A file-like object to write to.  The object must be able to write bytes. The user is
            responsible for closing the object.

        Returns
        -------
        None
        """
        assert_single_parameter(("filelike", "file_path"), filelike, file_path)

        response = self._client.post(f"{self._path}{self.id}/downloads/", stream=True)
        if file_path:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1000):
                    f.write(chunk)
        if filelike:
            for chunk in response.iter_content(chunk_size=1000):
                filelike.write(chunk)

    @classmethod
    def create_from_url(cls, url: str, max_wait: int = DEFAULT_MAX_WAIT) -> "File":
        """
        Create a new file in the DataRobot catalog from a URL.

        This method uploads a file from a given URL to the DataRobot catalog. The method will wait
        for the upload to complete before returning.

        Parameters
        ----------
        url: str
            The URL of the file to upload. Must be accessible by the DataRobot server.
        max_wait: Optional[int]
            Maximum time in seconds to wait for the upload to complete. Defaults to DEFAULT_MAX_WAIT.

        Returns
        -------
        File
            The newly created file object.

        Raises
        ------
        AsyncTimeoutError
            If the upload takes longer than max_wait seconds.
        """
        endpoint = f"{cls._path}/fromURL/"
        payload: Dict[str, str] = {"url": url}

        response = cls._client.post(endpoint, data=payload)
        new_file_location = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait
        )
        new_file = cls.from_location(new_file_location)
        return new_file
