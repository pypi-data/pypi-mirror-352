from ed_core.application.features.common.dtos.validators import \
    CreateLocationDtoValidator
from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)
from ed_core.application.features.driver.dtos import CreateDriverDto
from ed_core.application.features.driver.dtos.validators import \
    CreateCarDtoValidator


class CreateDriverDtoValidator(ABCDtoValidator[CreateDriverDto]):
    def validate(self, dto: CreateDriverDto) -> ValidationResponse:
        errors = []
        # TODO: Properly validate the create user dto

        if not dto.first_name:
            errors.append("First name is required")

        if not dto.last_name:
            errors.append("Last name is required")

        if not dto.phone_number:
            errors.append("Phone number is required")

        if not dto.profile_image:
            errors.append("Profile image is required")

        errors.extend(
            CreateCarDtoValidator().validate(dto.car).errors,
        )
        errors.extend(
            CreateLocationDtoValidator().validate(dto.location).errors,
        )

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
