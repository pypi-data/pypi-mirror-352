from datetime import UTC, datetime

from ed_domain.common.exceptions import EXCEPTION_NAMES, ApplicationException
from ed_domain.common.logging import get_logger
from ed_domain.core.entities import Bill, Consumer
from ed_domain.core.entities.bill import BillStatus
from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from ed_domain.core.value_objects.money import Currency, Money
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.abc_rabbitmq_producers import \
    ABCRabbitMQProducers
from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.business.dtos.create_consumer_dto import \
    CreateConsumerDto
from ed_core.application.features.business.dtos.validators import \
    CreateOrderDtoValidator
from ed_core.application.features.business.requests.commands import \
    CreateOrdersCommand
from ed_core.application.features.common.dtos import OrderDto
from ed_core.common.generic_helpers import get_new_id

LOG = get_logger()


@request_handler(CreateOrdersCommand, BaseResponse[list[OrderDto]])
class CreateOrdersCommandHandler(RequestHandler):
    def __init__(
        self, uow: ABCUnitOfWork, api: ABCApi, rabbitmq_producer: ABCRabbitMQProducers
    ):
        self._uow = uow
        self._api = api
        self._rabbitmq_producer = rabbitmq_producer

    async def handle(
        self, request: CreateOrdersCommand
    ) -> BaseResponse[list[OrderDto]]:
        business_id = request.business_id
        dto = request.dto
        for order in dto.orders:
            dto_validator = CreateOrderDtoValidator().validate(order)

            if not dto_validator.is_valid:
                return BaseResponse[list[OrderDto]].error(
                    "Orders cannot be created.",
                    dto_validator.errors,
                )

        created_orders = self._uow.order_repository.create_many(
            [
                order.create_order(
                    business_id,
                    self._create_or_get_consumer(order.consumer)["id"],
                    self._create_bill()["id"],
                    self._uow,
                )
                for order in dto.orders
            ]
        )

        return BaseResponse[list[OrderDto]].success(
            "Order created successfully.",
            [OrderDto.from_order(order, self._uow)
             for order in created_orders],
        )

    def _create_or_get_consumer(self, consumer: CreateConsumerDto) -> Consumer:
        if existing_consumer := self._uow.consumer_repository.get(
            phone_number=consumer.phone_number
        ):
            return existing_consumer

        LOG.info(
            f"Consumer with phone number {consumer.phone_number} does not exist. Creating a new consumer. Calling create_get_otp API with data: {consumer}"
        )
        create_user_response = self._api.auth_api.create_get_otp(
            {
                "first_name": consumer.first_name,
                "last_name": consumer.last_name,
                "phone_number": consumer.phone_number,
                "email": consumer.email,
            }
        )

        LOG.info(f"Response from create_get_otp API: {create_user_response}")
        if not create_user_response["is_success"]:
            raise ApplicationException(
                EXCEPTION_NAMES[create_user_response["http_status_code"]],
                "Failed to create orders",
                ["Could not create consumers."],
            )

        user_id = create_user_response["data"]["id"]
        return consumer.create_consumer(user_id, self._uow)

    def _create_bill(self) -> Bill:
        return self._uow.bill_repository.create(
            Bill(
                id=get_new_id(),
                amount=Money(
                    amount=10,
                    currency=Currency.ETB,
                ),
                bill_status=BillStatus.PENDING,
                due_date=datetime.now(UTC),
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
            )
        )
