from datetime import UTC, datetime

from ed_domain.core.entities import DeliveryJob
from ed_domain.core.entities.delivery_job import DeliveryJobStatus, WayPoint
from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from ed_domain.core.value_objects.money import Currency, Money
from pydantic import BaseModel

from ed_core.common.generic_helpers import get_new_id


class CreateDeliveryJobDto(BaseModel):
    waypoints: list[WayPoint]
    estimated_distance_in_kms: float
    estimated_time_in_minutes: int
    estimated_payment: float
    estimated_completion_time: datetime

    def create_delivery_job(self, uow: ABCUnitOfWork) -> DeliveryJob:
        created_delivery_job = uow.delivery_job_repository.create(
            DeliveryJob(
                id=get_new_id(),
                waypoints=self.waypoints,
                estimated_distance_in_kms=self.estimated_distance_in_kms,
                estimated_time_in_minutes=self.estimated_time_in_minutes,
                status=DeliveryJobStatus.IN_PROGRESS,
                estimated_payment=Money(
                    amount=self.estimated_payment, currency=Currency.ETB
                ),
                estimated_completion_time=self.estimated_completion_time,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
            )
        )

        return created_delivery_job
