from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.core.repositories import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos.consumer_dto import ConsumerDto
from ed_core.application.features.common.dtos.validators import \
    CreateConsumerDtoValidator
from ed_core.application.features.consumer.requests.commands import \
    CreateConsumerCommand

LOG = get_logger()


@request_handler(CreateConsumerCommand, BaseResponse[ConsumerDto])
class CreateConsumerCommandHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(self, request: CreateConsumerCommand) -> BaseResponse[ConsumerDto]:
        dto_validator = CreateConsumerDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            raise ApplicationException(
                Exceptions.ValidationException,
                "Create consumer failed.",
                dto_validator.errors,
            )

        consumer = request.dto.create_consumer(self._uow)

        return BaseResponse[ConsumerDto].success(
            "Consumer created successfully.",
            ConsumerDto.from_consumer(consumer, self._uow),
        )
