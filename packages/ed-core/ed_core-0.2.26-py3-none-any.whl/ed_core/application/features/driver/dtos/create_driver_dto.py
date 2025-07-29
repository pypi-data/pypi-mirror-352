from datetime import UTC, datetime
from uuid import UUID

from ed_domain.core.entities import Driver
from ed_domain.core.repositories import ABCUnitOfWork
from pydantic import BaseModel

from ed_core.application.features.common.dtos import CreateLocationDto
from ed_core.application.features.driver.dtos.create_car_dto import \
    CreateCarDto
from ed_core.common.generic_helpers import get_new_id


class CreateDriverDto(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    profile_image: str
    phone_number: str
    email: str
    location: CreateLocationDto
    car: CreateCarDto

    def create_driver(self, uow: ABCUnitOfWork) -> Driver:
        created_location = self.location.create_location(uow)
        created_car = self.car.create_car(uow)
        created_driver = uow.driver_repository.create(
            Driver(
                id=get_new_id(),
                user_id=self.user_id,
                first_name=self.first_name,
                last_name=self.last_name,
                profile_image=self.profile_image,
                phone_number=self.phone_number,
                email=self.email,
                current_location_id=created_location["id"],
                location_id=created_location["id"],
                car_id=created_car["id"],
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                active_status=True,
            )
        )

        return created_driver
