#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from typing import ClassVar
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.analysis_type_item import AnalysisTypeItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import ApiLibraryRead


def _empty_analysis_types() -> Generator[AnalysisTypeItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure analysis_types is
    not None for the LibraryItem class

    Yields:
        AnalysisTypeItem: Will never yield anything
    """
    yield from ()


class LibraryItem(ApiLibraryRead):
    MINDBRIDGE_FOR_PROFIT: ClassVar[str] = "5cc9076887f13cb8a7a1926b"
    MINDBRIDGE_NOT_FOR_PROFIT: ClassVar[str] = "5cc90bbd87f13cb8a7a1926d"
    MINDBRIDGE_NOT_FOR_PROFIT_WITH_FUNDS: ClassVar[str] = "5cc90b8f87f13cb8a7a1926c"
    MINDBRIDGE_REVIEW: ClassVar[str] = "5f2c22489db6c9ff301b16cb"
    analysis_types: Generator[AnalysisTypeItem, None, None] = Field(
        default_factory=_empty_analysis_types, exclude=True
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)
