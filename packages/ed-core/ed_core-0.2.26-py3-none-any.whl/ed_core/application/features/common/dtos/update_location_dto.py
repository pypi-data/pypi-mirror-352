from datetime import UTC, datetime

from ed_domain.core.entities import Location
from ed_domain.core.repositories import ABCUnitOfWork
from pydantic import BaseModel

from ed_core.common.generic_helpers import get_new_id

CITY = "Addis Ababa"
COUNTRY = "Ethiopia"


class UpdateLocationDto(BaseModel):
    address: str
    latitude: float
    longitude: float
    postal_code: str

    def update_location(self, uow: ABCUnitOfWork) -> Location:
        created_location = uow.location_repository.create(
            Location(
                id=get_new_id(),
                address=self.address,
                latitude=self.latitude,
                longitude=self.longitude,
                postal_code=self.postal_code,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                last_used=datetime.now(UTC),
                city=CITY,
                country=COUNTRY,
                deleted=False,
            )
        )

        return created_location
