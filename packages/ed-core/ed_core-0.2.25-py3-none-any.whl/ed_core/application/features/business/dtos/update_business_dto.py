from datetime import UTC, datetime
from typing import Optional

from ed_domain.core.entities import Business
from ed_domain.core.repositories import ABCUnitOfWork
from pydantic import BaseModel, Field

from ed_core.application.features.common.dtos import CreateLocationDto


class UpdateBusinessDto(BaseModel):
    phone_number: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    location: Optional[CreateLocationDto] = Field(None)

    def update_business(self, business: Business, uow: ABCUnitOfWork) -> Business:
        if self.location:
            created_location = self.location.create_location(uow)
            business["location_id"] = created_location["id"]

        if self.phone_number:
            business["phone_number"] = self.phone_number

        if self.email:
            business["email"] = self.email

        if any([self.email, self.phone_number, self.location]):
            business["update_datetime"] = datetime.now(UTC)

        uow.business_repository.update(business["id"], business)

        return business
