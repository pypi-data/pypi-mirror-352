from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.entities import Order
from ed_domain.core.entities.order import OrderStatus, Parcel
from ed_domain.core.repositories import ABCUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.business.dtos.create_consumer_dto import \
    CreateConsumerDto
from ed_core.common.generic_helpers import get_new_id


class CreateOrderDto(BaseModel):
    consumer: CreateConsumerDto
    latest_time_of_delivery: datetime
    parcel: Parcel

    def create_order(
        self,
        business_id: UUID,
        consumer_id: UUID,
        bill_id: UUID,
        uow: ABCUnitOfWork,
    ) -> Order:
        created_order = uow.order_repository.create(
            Order(
                id=get_new_id(),
                business_id=business_id,
                consumer_id=consumer_id,
                bill_id=bill_id,
                latest_time_of_delivery=self.latest_time_of_delivery,
                parcel=self.parcel,
                order_status=OrderStatus.PENDING,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
            )
        )

        return created_order


class CreateOrdersDto(BaseModel):
    orders: list[CreateOrderDto]
