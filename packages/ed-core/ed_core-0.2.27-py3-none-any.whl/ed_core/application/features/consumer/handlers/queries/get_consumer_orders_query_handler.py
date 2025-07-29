from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import OrderDto
from ed_core.application.features.consumer.requests.queries import \
    GetConsumerOrdersQuery


@request_handler(GetConsumerOrdersQuery, BaseResponse[list[OrderDto]])
class GetConsumerOrdersQueryHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: GetConsumerOrdersQuery
    ) -> BaseResponse[list[OrderDto]]:
        orders = self._uow.order_repository.get_all(
            consumer_id=request.consumer_id)

        return BaseResponse[list[OrderDto]].success(
            "Consumer orders fetched successfully.",
            [OrderDto.from_order(order, self._uow) for order in orders],
        )
