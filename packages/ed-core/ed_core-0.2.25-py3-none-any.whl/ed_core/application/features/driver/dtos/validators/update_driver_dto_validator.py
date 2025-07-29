from ed_core.application.features.common.dtos.validators import \
    CreateLocationDtoValidator
from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)
from ed_core.application.features.driver.dtos.update_driver_dto import \
    UpdateDriverDto


class UpdateDriverDtoValidator(ABCDtoValidator[UpdateDriverDto]):
    def validate(self, dto: UpdateDriverDto) -> ValidationResponse:
        errors = []
        if dto.location:
            errors.extend(
                CreateLocationDtoValidator().validate(dto.location).errors,
            )

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
