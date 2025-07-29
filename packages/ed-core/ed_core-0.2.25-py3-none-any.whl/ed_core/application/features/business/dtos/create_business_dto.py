from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.entities import Business
from ed_domain.core.repositories import ABCUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.common.dtos import CreateLocationDto
from ed_core.common.generic_helpers import get_new_id


class CreateBusinessDto(BaseModel):
    user_id: UUID
    business_name: str
    owner_first_name: str
    owner_last_name: str
    phone_number: str
    email: str
    location: CreateLocationDto

    def create_business(self, uow: ABCUnitOfWork) -> Business:
        created_location = self.location.create_location(uow)

        created_business = uow.business_repository.create(
            Business(
                id=get_new_id(),
                user_id=self.user_id,
                business_name=self.business_name,
                owner_first_name=self.owner_first_name,
                owner_last_name=self.owner_last_name,
                phone_number=self.phone_number,
                email=self.email,
                location_id=created_location["id"],
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                active_status=True,
            )
        )

        return created_business
