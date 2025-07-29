from dataclasses import dataclass
from uuid import UUID

from rmediator.decorators import request
from rmediator.mediator import Request

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.business.dtos import CreateOrderDto
from ed_core.application.features.business.dtos.create_order_dto import \
    CreateOrdersDto
from ed_core.application.features.common.dtos import OrderDto


@request(BaseResponse[list[OrderDto]])
@dataclass
class CreateOrdersCommand(Request):
    business_id: UUID
    dto: CreateOrdersDto
