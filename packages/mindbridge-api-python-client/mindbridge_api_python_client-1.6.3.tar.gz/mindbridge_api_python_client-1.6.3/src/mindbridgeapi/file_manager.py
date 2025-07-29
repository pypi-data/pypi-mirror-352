#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import (
    ItemAlreadyExistsError,
    ItemError,
    ItemNotFoundError,
    ParameterError,
)
from mindbridgeapi.file_manager_item import FileManagerItem, FileManagerType

if TYPE_CHECKING:
    from collections.abc import Generator
    from os import PathLike
    from mindbridgeapi.chunked_file_item import ChunkedFileItem

logger = logging.getLogger(__name__)


@dataclass
class FileManager(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/file-manager"

    def mkdir(self, item: FileManagerItem) -> FileManagerItem:
        if getattr(item, "id", None) is not None and item.id is not None:
            raise ItemAlreadyExistsError(item.id)

        url = self.base_url
        resp_dict = super()._create(url=url, json=item.create_json)

        return FileManagerItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> FileManagerItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return FileManagerItem.model_validate(resp_dict)

    def update(self, item: FileManagerItem) -> FileManagerItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        return FileManagerItem.model_validate(resp_dict)

    def get(
        self, json: Optional[dict[str, Any]] = None
    ) -> "Generator[FileManagerItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"

        for resp_dict in super()._get(url=url, json=json):
            yield FileManagerItem.model_validate(resp_dict)

    def delete(self, item: FileManagerItem) -> None:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        super()._delete(url=url)

    def upload(
        self, input_item: FileManagerItem, input_file: Union[str, "PathLike[Any]"]
    ) -> FileManagerItem:
        input_file_path = Path(input_file)

        if not input_file_path.is_file():
            raise ParameterError(
                parameter_name="input_file_path",
                details=f"{input_file_path} is not a file.",
            )

        if not input_item.name:
            input_item.name = input_file_path.stem

        if not input_item.extension and input_file_path.suffix:
            input_item.extension = input_file_path.suffix[1:]

        chunk_size = 50 * 2**20  # 50 MB
        file_size = input_file_path.stat().st_size
        if file_size <= 0:
            raise ParameterError(
                parameter_name="input_file_path",
                details=f"File size of {file_size} is too small",
            )

        number_of_parts = file_size // chunk_size
        if file_size % chunk_size > 0:
            number_of_parts += 1

        file_name = input_item.filename

        logger.info(
            "Preparing to upload a file with %i chunks, using a size of %i bytes",
            number_of_parts,
            chunk_size,
        )

        if number_of_parts <= 1:
            logger.info(
                'Using the "Create File Manager File From Multipart File" method'
            )
            url = f"{self.base_url}/import"

            with input_file_path.open("rb") as open_file:
                upload_bytes = open_file.read()

            files: dict[str, Any] = {
                "fileManagerFile": (None, input_item.create_body, "application/json"),
                "file": (file_name, upload_bytes),
            }

            logger.info(
                "upload with fileManagerFile data as %s", input_item.create_body
            )

            resp_dict = self._upload(url=url, files=files)

            return FileManagerItem.model_validate(resp_dict)

        logger.info('Using the "Chunked Files" method')
        chunked_file = self.server.chunked_files.upload(input_file_path)

        return self.import_from_chunked(chunked_file, input_item)

    def download(
        self, input_item: FileManagerItem, output_file: Union[str, "PathLike[Any]"]
    ) -> Path:
        if getattr(input_item, "id", None) is None:
            raise ItemNotFoundError

        if FileManagerType(input_item.type) == FileManagerType.DIRECTORY:
            msg = f"Unexpected value of {input_item.type} for type."
            raise ItemError(msg)

        output_file_path = Path(output_file)

        output_file_path = output_file_path.expanduser()

        if output_file_path.is_dir():
            output_file_path /= input_item.filename
        elif output_file_path.exists():
            logger.info("%s already exists, will be overwritten", output_file_path)
        elif output_file_path.parent.is_dir():
            logger.info("%s will be created", output_file_path)
        else:
            raise ParameterError(
                parameter_name="output_file",
                details=f"{output_file_path} is not a valid download location",
            )

        url = f"{self.base_url}/{input_item.id}/export"

        return super()._download(url=url, output_path=output_file_path)

    def import_from_chunked(
        self, chunked_file_item: "ChunkedFileItem", file_manager_item: FileManagerItem
    ) -> FileManagerItem:
        if getattr(chunked_file_item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/import-from-chunked/{chunked_file_item.id}"

        resp_dict = super()._create(url=url, json=file_manager_item.create_json)

        return FileManagerItem.model_validate(resp_dict)
