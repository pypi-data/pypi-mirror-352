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
    ApiAccountingPeriodRead,
    Frequency,
)


class AccountingPeriod(ApiAccountingPeriodRead):
    fiscal_start_month: int = Field().merge_field_infos(
        ApiAccountingPeriodRead.model_fields["fiscal_start_month"], default=1
    )
    fiscal_start_day: int = Field().merge_field_infos(
        ApiAccountingPeriodRead.model_fields["fiscal_start_day"], default=1
    )
    frequency: Frequency = Field().merge_field_infos(
        ApiAccountingPeriodRead.model_fields["frequency"], default=Frequency.ANNUAL
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)
