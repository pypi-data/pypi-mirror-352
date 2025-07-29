#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, Optional
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.async_results import AsyncResults
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.exceptions import ItemError, ItemNotFoundError, ParameterError
from mindbridgeapi.generated_pydantic_model.model import (
    ApiDataTableExportRequest,
    ApiDataTableQuerySortOrder,
    ApiDataTableRead,
    Direction,
    Type4 as DataTableColumnType,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@dataclass
class DataTables(BaseSet):
    def __post_init__(self) -> None:
        self.async_result_set = AsyncResults(server=self.server)

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/data-tables"

    def get_by_id(self, id: str) -> ApiDataTableRead:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return ApiDataTableRead.model_validate(resp_dict)

    def get(
        self, json: Optional[dict[str, Any]] = None
    ) -> "Generator[ApiDataTableRead, None, None]":
        mb_query_dict = _convert_json_query(json, required_key="analysisId")

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=mb_query_dict):
            yield ApiDataTableRead.model_validate(resp_dict)

    @staticmethod
    def _export_get_fields(
        input_item: ApiDataTableRead, fields: Optional[list[str]] = None
    ) -> list[str]:
        if fields:
            return fields

        if input_item.columns is None:
            msg = f"{input_item.columns=}."
            raise ItemError(msg)

        """
        "KEYWORD_SEARCH columns can't be included in data table exports. Attempting to
            select them as part of fields will cause the export request to fail.".
            Similarly fields that are filter only can't be included as fields.
        """
        return [
            x.field
            for x in input_item.columns
            if x.type != DataTableColumnType.KEYWORD_SEARCH
            and x.field is not None
            and not x.filter_only
        ]

    @staticmethod
    def _export_get_sort(
        input_item: ApiDataTableRead,
        sort_direction: Optional[Direction] = None,
        sort_field: Optional[str] = None,
    ) -> Optional[ApiDataTableQuerySortOrder]:
        if sort_field is not None and not isinstance(sort_field, str):
            raise ParameterError(
                parameter_name="sort_field", details="Not provided as str."
            )

        if sort_field is None and input_item.logical_name == "gl_journal_lines":
            sort_field = "rowid"
        elif sort_field is None and input_item.logical_name == "gl_journal_tx":
            sort_field = "txid"

        if not sort_field:
            return None

        if sort_direction is None:
            sort_direction = Direction.ASC

        try:
            sort_direction = Direction(sort_direction)
        except ValueError as err:
            raise ParameterError(
                parameter_name="sort_direction", details="Not a valid Direction."
            ) from err

        return ApiDataTableQuerySortOrder(direction=sort_direction, field=sort_field)

    def export(  # noqa: PLR0913
        self,
        input_item: ApiDataTableRead,
        fields: Optional[list[str]] = None,
        query: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
        sort_direction: Optional[Direction] = None,
        sort_field: Optional[str] = None,
    ) -> AsyncResultItem:
        if getattr(input_item, "id", None) is None:
            raise ItemNotFoundError

        fields = self._export_get_fields(input_item=input_item, fields=fields)

        url = f"{self.base_url}/{input_item.id}/export"
        data_table_export_request = ApiDataTableExportRequest(
            fields=fields,
            limit=limit,
            sort=self._export_get_sort(
                input_item=input_item,
                sort_direction=sort_direction,
                sort_field=sort_field,
            ),
        )

        json = data_table_export_request.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
        json["query"] = _convert_json_query(query)

        resp_dict = super()._create(url=url, json=json)

        return AsyncResultItem.model_validate(resp_dict)

    def wait_for_export(
        self, async_result: AsyncResultItem, max_wait_minutes: int = (24 * 60)
    ) -> None:
        """Wait for the async result for the data table export to complete.

        Waits, at most the minutes specified, for the async result to be COMPLETE and
        raises and error if any error

        Args:
            async_result (AsyncResultItem): Async result to check
            max_wait_minutes (int): Maximum minutes to wait (default: `24 * 60`)

        Raises:
            ItemError: If not a DATA_TABLE_EXPORT
        """
        if async_result.type != AsyncResultType.DATA_TABLE_EXPORT:
            msg = f"{async_result.type=}."
            raise ItemError(msg)

        self.async_result_set._wait_for_async_result(
            async_result=async_result,
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=10,
        )

    def download(
        self, async_result: AsyncResultItem, output_file_path: "Path"
    ) -> "Path":
        if async_result.id is None:
            raise ItemNotFoundError

        async_result = self.server.async_results.get_by_id(async_result.id)

        file_result_id = async_result._get_file_result_id(
            expected_type=AsyncResultType.DATA_TABLE_EXPORT
        )

        file_result = self.server.file_results.get_by_id(file_result_id)

        return self.server.file_results.export(
            file_result=file_result, output_file_path=output_file_path
        )
