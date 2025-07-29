#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from datetime import date, datetime, timezone
from typing import Any, Optional, Union
from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic_core import PydanticUndefined
from mindbridgeapi.accounting_period import AccountingPeriod
from mindbridgeapi.analysis_item import AnalysisItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.engagement_account_grouping_item import EngagementAccountGroupingItem
from mindbridgeapi.file_manager_item import FileManagerItem
from mindbridgeapi.generated_pydantic_model.model import (
    ApiEngagementCreateOnly,
    ApiEngagementRead,
    ApiEngagementUpdate,
)
from mindbridgeapi.library_item import LibraryItem


def _empty_analyses() -> Generator[AnalysisItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure analyses is not None
    for the EngagementItem class

    Yields:
        AnalysisItem: Will never yield anything
    """
    yield from ()


def _empty_file_manager_items() -> Generator[FileManagerItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure file_manager_items
    is not None for the EngagementItem class

    Yields:
        FileManagerItem: Will never yield anything
    """
    yield from ()


def _empty_engagement_account_groupings() -> Generator[
    EngagementAccountGroupingItem, None, None
]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure
    engagement_account_groupings is not None for the EngagementAccountGroupingItem class

    Yields:
        EngagementAccountGroupingItem: Will never yield anything
    """
    yield from ()


class EngagementItem(ApiEngagementRead):
    file_manager_items: Generator[FileManagerItem, None, None] = Field(
        default_factory=_empty_file_manager_items, exclude=True
    )
    analyses: Generator[AnalysisItem, None, None] = Field(
        default_factory=_empty_analyses, exclude=True
    )
    engagement_account_groupings: Generator[
        EngagementAccountGroupingItem, None, None
    ] = Field(default_factory=_empty_engagement_account_groupings, exclude=True)
    settings_based_on_engagement_id: Optional[str] = Field().merge_field_infos(
        ApiEngagementCreateOnly.model_fields["settings_based_on_engagement_id"]
    )
    accounting_package: str = Field().merge_field_infos(
        ApiEngagementRead.model_fields["accounting_package"], default="Other"
    )
    accounting_period: AccountingPeriod = Field().merge_field_infos(
        ApiEngagementRead.model_fields["accounting_period"],
        default=PydanticUndefined,
        default_factory=AccountingPeriod,
    )
    audit_period_end_date: date = Field().merge_field_infos(
        ApiEngagementRead.model_fields["audit_period_end_date"],
        default=datetime.now(tz=timezone.utc)
        .astimezone()
        .date()
        .replace(month=12, day=31),
    )
    industry: str = Field().merge_field_infos(
        ApiEngagementRead.model_fields["industry"], default="Other"
    )
    library_id: str = Field().merge_field_infos(
        ApiEngagementRead.model_fields["library_id"],
        default=LibraryItem.MINDBRIDGE_FOR_PROFIT,
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(
        self, out_class: type[Union[ApiEngagementCreateOnly, ApiEngagementUpdate]]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiEngagementCreateOnly)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiEngagementUpdate)
