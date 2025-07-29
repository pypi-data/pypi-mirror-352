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
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.generated_pydantic_model.model import ApiUserRead as UserItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class Users(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/users"

    def get_current(self) -> UserItem:
        url = f"{self.base_url}/current"
        resp_dict = super()._get_by_id(url=url)

        return UserItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> UserItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return UserItem.model_validate(resp_dict)

    def get(
        self, json: Optional[dict[str, Any]] = None
    ) -> "Generator[UserItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            yield UserItem.model_validate(resp_dict)
