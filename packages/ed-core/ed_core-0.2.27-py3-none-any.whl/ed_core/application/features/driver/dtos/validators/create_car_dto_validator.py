from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)
from ed_core.application.features.driver.dtos.create_car_dto import \
    CreateCarDto


class CreateCarDtoValidator(ABCDtoValidator[CreateCarDto]):
    def validate(self, dto: CreateCarDto) -> ValidationResponse:
        errors = []

        if not dto.model:
            errors.append("Model is required")

        if not dto.make:
            errors.append("Make is required")

        if not dto.year:
            errors.append("Year is required")

        if not dto.color:
            errors.append("Color is required")

        if not dto.license_plate:
            errors.append("License plate is required")

        if not dto.seats:
            errors.append("Seats is required")

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
