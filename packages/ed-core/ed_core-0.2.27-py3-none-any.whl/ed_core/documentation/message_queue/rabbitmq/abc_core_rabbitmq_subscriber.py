from abc import ABCMeta, abstractmethod
from enum import StrEnum

from ed_core.application.features.delivery_job.dtos.create_delivery_job_dto import \
    CreateDeliveryJobDto


class CoreQueues(StrEnum):
    CREATE_DELIVERY_JOB = "core.create_delivery_job"
    UPDATE_DRIVER_LOCATION = "core.update_driver_location"


class ABCCoreRabbitMQSubscriber(metaclass=ABCMeta):
    @abstractmethod
    def create_delivery_job(
        self, create_delivery_job_dto: CreateDeliveryJobDto
    ) -> None: ...
