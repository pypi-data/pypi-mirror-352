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
from mindbridgeapi.analysis_types import AnalysisTypes
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemNotFoundError
from mindbridgeapi.library_item import LibraryItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class Libraries(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/libraries"

    def get_by_id(self, id: str) -> LibraryItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        library_item = LibraryItem.model_validate(resp_dict)
        self.restart_analysis_types(library_item)
        return library_item

    def get(
        self, json: Optional[dict[str, Any]] = None
    ) -> "Generator[LibraryItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            library_item = LibraryItem.model_validate(resp_dict)
            self.restart_analysis_types(library_item)
            yield library_item

    def restart_analysis_types(self, library_item: LibraryItem) -> None:
        if getattr(library_item, "id", None) is None:
            raise ItemNotFoundError

        if (
            library_item.analysis_type_ids is not None
            and len(library_item.analysis_type_ids) != 0
        ):
            library_item.analysis_types = AnalysisTypes(server=self.server).get(
                json={"id": {"$in": library_item.analysis_type_ids}}
            )
