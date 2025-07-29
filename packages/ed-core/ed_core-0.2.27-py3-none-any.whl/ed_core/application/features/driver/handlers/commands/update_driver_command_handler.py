from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.core.repositories import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos.driver_dto import DriverDto
from ed_core.application.features.driver.dtos.validators import \
    UpdateDriverDtoValidator
from ed_core.application.features.driver.requests.commands import \
    UpdateDriverCommand

LOG = get_logger()


@request_handler(UpdateDriverCommand, BaseResponse[DriverDto])
class UpdateDriverCommandHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(self, request: UpdateDriverCommand) -> BaseResponse[DriverDto]:
        dto_validator = UpdateDriverDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            return BaseResponse[DriverDto].error(
                "Update driver failed.", dto_validator.errors
            )

        driver = self._uow.driver_repository.get(id=request.driver_id)
        if driver is None:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Driver update failed.",
                ["Driver not found."],
            )

        updated_driver = request.dto.update_driver(driver, self._uow)

        return BaseResponse[DriverDto].success(
            "Driver updated successfully.",
            DriverDto.from_driver(updated_driver, self._uow),
        )
