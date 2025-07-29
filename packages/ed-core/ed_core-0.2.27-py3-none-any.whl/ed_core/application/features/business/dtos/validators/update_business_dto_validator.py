from ed_core.application.features.business.dtos.update_business_dto import \
    UpdateBusinessDto
from ed_core.application.features.common.dtos.validators import \
    CreateLocationDtoValidator
from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)


class UpdateBusinessDtoValidator(ABCDtoValidator[UpdateBusinessDto]):
    _location_validator = CreateLocationDtoValidator()

    def validate(self, dto: UpdateBusinessDto) -> ValidationResponse:
        errors = []

        if dto.location:
            errors.extend(
                self._location_validator.validate(dto.location).errors,
            )

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
