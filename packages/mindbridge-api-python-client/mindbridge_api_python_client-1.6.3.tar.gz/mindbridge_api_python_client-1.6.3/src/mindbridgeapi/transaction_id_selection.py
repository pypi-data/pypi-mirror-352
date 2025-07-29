#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from pydantic import ConfigDict, Field, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.generated_pydantic_model.model import (
    ApiTransactionIdSelectionRead,
    Type39 as _TransactionIdType,
)

TransactionIdType = _TransactionIdType  # Match the type of TransactionIdSelection.type


class TransactionIdSelection(ApiTransactionIdSelectionRead):
    apply_smart_splitter: bool = Field().merge_field_infos(
        ApiTransactionIdSelectionRead.model_fields["apply_smart_splitter"],
        default=False,
    )
    type: TransactionIdType = Field().merge_field_infos(
        ApiTransactionIdSelectionRead.model_fields["type"],
        default=TransactionIdType.COMBINATION,
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)
