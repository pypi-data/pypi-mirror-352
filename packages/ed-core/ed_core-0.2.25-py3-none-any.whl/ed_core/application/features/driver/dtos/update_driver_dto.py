from datetime import UTC, datetime
from typing import Optional

from ed_domain.core.entities import Driver
from ed_domain.core.repositories import ABCUnitOfWork
from pydantic import BaseModel, Field

from ed_core.application.features.common.dtos import CreateLocationDto


class UpdateDriverDto(BaseModel):
    profile_image: Optional[str] = Field(None)
    phone_number: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    location: Optional[CreateLocationDto] = Field(None)

    def update_driver(self, driver: Driver, uow: ABCUnitOfWork) -> Driver:
        if self.location:
            created_location = self.location.create_location(uow)
            driver["location_id"] = created_location["id"]

        if self.phone_number:
            driver["phone_number"] = self.phone_number

        if self.email:
            driver["email"] = self.email

        if any([self.email, self.phone_number, self.location]):
            driver["update_datetime"] = datetime.now(UTC)

        uow.driver_repository.update(driver["id"], driver)

        return driver
