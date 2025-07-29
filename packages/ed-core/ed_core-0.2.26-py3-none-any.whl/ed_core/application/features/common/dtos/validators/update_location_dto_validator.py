from ed_core.application.features.common.dtos import UpdateLocationDto
from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)


class UpdateLocationDtoValidator(ABCDtoValidator[UpdateLocationDto]):
    def validate(self, dto: UpdateLocationDto) -> ValidationResponse:
        errors = []

        if not dto.latitude:
            errors.append("Latitude is required")

        if not dto.longitude:
            errors.append("Longitude is required")

        if not dto.address:
            errors.append("Address is required")

        if not dto.postal_code:
            errors.append("Postal code is required")

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
