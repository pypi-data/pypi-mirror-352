#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.engagement_account_group_item import EngagementAccountGroupItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class EngagementAccountGroups(BaseSet):
    base_url: str = field(init=False)

    def __post_init__(self) -> None:
        self.base_url = f"{self.server.base_url}/engagement-account-groups"

    def get_by_id(self, id: str) -> EngagementAccountGroupItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return EngagementAccountGroupItem.model_validate(resp_dict)

    def get(
        self, json: Optional[dict[str, Any]] = None
    ) -> "Generator[EngagementAccountGroupItem, None, None]":
        mb_query_dict = _convert_json_query(
            json, required_key="engagementAccountGroupingId"
        )

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=mb_query_dict):
            yield EngagementAccountGroupItem.model_validate(resp_dict)
