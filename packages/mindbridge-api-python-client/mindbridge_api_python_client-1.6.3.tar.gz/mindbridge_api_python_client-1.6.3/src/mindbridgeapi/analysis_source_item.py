#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Annotated, Any, Literal, Optional, Union
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.analysis_source_type_item import AnalysisSourceTypeItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAnalysisSourceCreateOnly,
    ApiAnalysisSourceRead,
    ApiAnalysisSourceUpdate,
    ApiDuplicateVirtualColumnUpdate,
    ApiJoinVirtualColumnUpdate,
    ApiSplitByDelimiterVirtualColumnUpdate,
    ApiSplitByPositionVirtualColumnUpdate,
)
from mindbridgeapi.virtual_column import VirtualColumn, VirtualColumnType


class DuplicateVirtualColumn(ApiDuplicateVirtualColumnUpdate):
    type: Literal[VirtualColumnType.DUPLICATE] = Field().merge_field_infos(
        ApiDuplicateVirtualColumnUpdate.model_fields["type"]
    )
    name: Optional[str] = Field().merge_field_infos(
        ApiDuplicateVirtualColumnUpdate.model_fields["name"], default=None
    )  # type: ignore[assignment]
    version: Optional[int] = Field().merge_field_infos(
        ApiDuplicateVirtualColumnUpdate.model_fields["version"], default=None
    )  # type: ignore[assignment]


class SplitByPositionVirtualColumn(ApiSplitByPositionVirtualColumnUpdate):
    type: Literal[VirtualColumnType.SPLIT_BY_POSITION] = Field().merge_field_infos(
        ApiSplitByPositionVirtualColumnUpdate.model_fields["type"]
    )
    name: Optional[str] = Field().merge_field_infos(
        ApiSplitByPositionVirtualColumnUpdate.model_fields["name"], default=None
    )  # type: ignore[assignment]
    version: Optional[int] = Field().merge_field_infos(
        ApiSplitByPositionVirtualColumnUpdate.model_fields["version"], default=None
    )  # type: ignore[assignment]


class SplitByDelimiterVirtualColumn(ApiSplitByDelimiterVirtualColumnUpdate):
    type: Literal[VirtualColumnType.SPLIT_BY_DELIMITER] = Field().merge_field_infos(
        ApiSplitByDelimiterVirtualColumnUpdate.model_fields["type"]
    )
    name: Optional[str] = Field().merge_field_infos(
        ApiSplitByDelimiterVirtualColumnUpdate.model_fields["name"], default=None
    )  # type: ignore[assignment]
    version: Optional[int] = Field().merge_field_infos(
        ApiSplitByDelimiterVirtualColumnUpdate.model_fields["version"], default=None
    )  # type: ignore[assignment]


class JoinVirtualColumn(ApiJoinVirtualColumnUpdate):
    type: Literal[VirtualColumnType.JOIN] = Field().merge_field_infos(
        ApiJoinVirtualColumnUpdate.model_fields["type"]
    )
    name: Optional[str] = Field().merge_field_infos(
        ApiJoinVirtualColumnUpdate.model_fields["name"], default=None
    )  # type: ignore[assignment]
    version: Optional[int] = Field().merge_field_infos(
        ApiJoinVirtualColumnUpdate.model_fields["version"], default=None
    )  # type: ignore[assignment]


_VirtualColumn = Annotated[
    Union[
        DuplicateVirtualColumn,
        SplitByPositionVirtualColumn,
        SplitByDelimiterVirtualColumn,
        JoinVirtualColumn,
    ],
    Field(discriminator="type"),
]


class _ApiAnalysisSourceCreateOnly(ApiAnalysisSourceCreateOnly):
    """An Analysis Source in MindBridge for creation.

    proposed_virtual_columns is "overridden" so that it's able to determine the
        appropriate virtual column type.
    """

    proposed_virtual_columns: Optional[list[_VirtualColumn]] = (
        Field().merge_field_infos(  # type: ignore[assignment]
            ApiAnalysisSourceCreateOnly.model_fields["proposed_virtual_columns"]
        )
    )


class _ApiAnalysisSourceUpdate(ApiAnalysisSourceUpdate):
    """An Analysis Source in MindBridge for updating.

    proposed_virtual_columns and virtual_columns are "overridden" so that it's able to
        determine the appropriate virtual column type.
    """

    proposed_virtual_columns: Optional[list[_VirtualColumn]] = (
        Field().merge_field_infos(  # type: ignore[assignment]
            ApiAnalysisSourceUpdate.model_fields["proposed_virtual_columns"]
        )
    )
    virtual_columns: Optional[list[_VirtualColumn]] = Field().merge_field_infos(
        ApiAnalysisSourceUpdate.model_fields["virtual_columns"]
    )  # type: ignore[assignment]


class AnalysisSourceItem(ApiAnalysisSourceRead):
    """An Analysis Source in MindBridge.

    proposed_virtual_columns and virtual_columns are "overridden" so that it's able to
        determine the appropriate virtual column type.
    """

    analysis_source_type_id: str = Field().merge_field_infos(
        ApiAnalysisSourceRead.model_fields["analysis_source_type_id"],
        default=AnalysisSourceTypeItem.GENERAL_LEDGER_JOURNAL,
    )
    proposed_virtual_columns: Optional[list[_VirtualColumn]] = (
        Field().merge_field_infos(  # type: ignore[assignment]
            ApiAnalysisSourceRead.model_fields["proposed_virtual_columns"]
        )
    )
    virtual_columns: Optional[list[_VirtualColumn]] = Field().merge_field_infos(
        ApiAnalysisSourceRead.model_fields["virtual_columns"]
    )  # type: ignore[assignment]
    warnings_ignored: bool = Field().merge_field_infos(
        ApiAnalysisSourceRead.model_fields["warnings_ignored"], default=True
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    @field_validator("proposed_virtual_columns", mode="before")
    @classmethod
    def _convert_virtualcolumn_to_dict(cls, v: Any) -> Any:
        """Ensures virtualcolumns are parsed as the appropriate type.

        Returns:
            List of VirtualColumns as dicts.
        """
        if not isinstance(v, list):
            return v

        new_list = []
        for x in v:
            if isinstance(x, VirtualColumn):
                new_list.append(x.model_dump(by_alias=True, exclude_none=True))
            else:
                new_list.append(x)

        return new_list

    def _get_post_json(
        self,
        out_class: type[Union[_ApiAnalysisSourceCreateOnly, _ApiAnalysisSourceUpdate]],
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=_ApiAnalysisSourceCreateOnly)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=_ApiAnalysisSourceUpdate)
