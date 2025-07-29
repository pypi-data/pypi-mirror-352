from ed_core.application.features.common.dtos.create_consumer_dto import \
    CreateConsumerDto
from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)
from ed_core.application.features.common.dtos.validators.create_location_dto_validator import \
    CreateLocationDtoValidator


class CreateConsumerDtoValidator(ABCDtoValidator[CreateConsumerDto]):
    def validate(self, dto: CreateConsumerDto) -> ValidationResponse:
        errors = []

        if not dto.first_name:
            errors.append("First name of consumer is required.")

        if not dto.last_name:
            errors.append("Last name of consumer is required.")

        if not dto.phone_number:
            errors.append("Phone number of consumer is required")

        errors.extend(
            CreateLocationDtoValidator().validate(dto.location).errors,
        )

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
