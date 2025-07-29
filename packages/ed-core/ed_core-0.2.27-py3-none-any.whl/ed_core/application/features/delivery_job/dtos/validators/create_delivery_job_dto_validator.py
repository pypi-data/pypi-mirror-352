from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)
from ed_core.application.features.delivery_job.dtos import CreateDeliveryJobDto


class CreateDeliveryJobDtoValidator(ABCDtoValidator[CreateDeliveryJobDto]):
    def validate(self, dto: CreateDeliveryJobDto) -> ValidationResponse:
        errors = []

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
