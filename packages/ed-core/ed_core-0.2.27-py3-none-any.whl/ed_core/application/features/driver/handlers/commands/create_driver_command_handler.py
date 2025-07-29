from ed_domain.common.logging import get_logger
from ed_domain.core.repositories import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos.driver_dto import DriverDto
from ed_core.application.features.driver.dtos.validators import \
    CreateDriverDtoValidator
from ed_core.application.features.driver.requests.commands import \
    CreateDriverCommand

LOG = get_logger()


@request_handler(CreateDriverCommand, BaseResponse[DriverDto])
class CreateDriverCommandHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(self, request: CreateDriverCommand) -> BaseResponse[DriverDto]:
        dto_validator = CreateDriverDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            return BaseResponse[DriverDto].error(
                "Create driver failed.", dto_validator.errors
            )

        driver = request.dto.create_driver(self._uow)

        return BaseResponse[DriverDto].success(
            "Driver created successfully.",
            DriverDto.from_driver(driver, self._uow),
        )
