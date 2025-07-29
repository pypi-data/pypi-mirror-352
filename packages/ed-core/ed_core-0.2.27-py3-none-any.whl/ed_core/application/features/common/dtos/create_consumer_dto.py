from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.entities import Consumer
from ed_domain.core.repositories import ABCUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.common.dtos.create_location_dto import \
    CreateLocationDto
from ed_core.common.generic_helpers import get_new_id


class CreateConsumerDto(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    phone_number: str
    email: str
    location: CreateLocationDto

    def create_consumer(self, uow: ABCUnitOfWork) -> Consumer:
        created_location = self.location.create_location(uow)

        created_consumer = uow.consumer_repository.create(
            Consumer(
                id=get_new_id(),
                user_id=self.user_id,
                first_name=self.first_name,
                last_name=self.last_name,
                phone_number=self.phone_number,
                email=self.email,
                location_id=created_location["id"],
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                active_status=True,
            )
        )

        return created_consumer
