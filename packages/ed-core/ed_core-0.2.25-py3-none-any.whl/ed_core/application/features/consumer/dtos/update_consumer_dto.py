from typing import Optional

from pydantic import BaseModel, Field

from ed_core.application.features.common.dtos.update_location_dto import \
    UpdateLocationDto


class UpdateConsumerDto(BaseModel):
    location: Optional[UpdateLocationDto] = Field(None)
