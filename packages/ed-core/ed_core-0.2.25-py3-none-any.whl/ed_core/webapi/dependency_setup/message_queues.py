from typing import Annotated

from ed_auth.documentation.message_queue.rabbitmq.auth_rabbitmq_subscriber import (
    ABCAuthRabbitMQSubscriber, AuthRabbitMQSubscriber)
from ed_notification.documentation.message_queue.rabbitmq.notification_rabbitmq_subscriber import (
    ABCNotificationRabbitMQSubscriber, NotificationRabbitMQSubscriber)
from ed_optimization.documentation.message_queue.rabbitmq.optimization_rabbitmq_subscriber import (
    ABCOptimizationRabbitMQSubscriber, OptimizationRabbitMQSubscriber)
from fastapi import Depends

from ed_core.application.contracts.infrastructure.abc_rabbitmq_producers import \
    ABCRabbitMQProducers
from ed_core.common.generic_helpers import get_config
from ed_core.common.typing.config import Config
from ed_core.infrastructure.api.rabbitmq_handler import RabbitMQHandler


def get_auth_producer(
    config: Annotated[Config, Depends(get_config)],
) -> ABCAuthRabbitMQSubscriber:
    return AuthRabbitMQSubscriber(config["rabbitmq"]["url"])


def get_notification_producer(
    config: Annotated[Config, Depends(get_config)],
) -> ABCNotificationRabbitMQSubscriber:
    return NotificationRabbitMQSubscriber(config["rabbitmq"]["url"])


def get_optimization_producer(
    config: Annotated[Config, Depends(get_config)],
) -> ABCOptimizationRabbitMQSubscriber:
    return OptimizationRabbitMQSubscriber(config["rabbitmq"]["url"])


def get_rabbitmq_handler(
    auth_producer: Annotated[ABCAuthRabbitMQSubscriber, Depends(get_auth_producer)],
    notification_producer: Annotated[
        ABCNotificationRabbitMQSubscriber, Depends(get_notification_producer)
    ],
    optimization_producer: Annotated[
        ABCOptimizationRabbitMQSubscriber, Depends(get_optimization_producer)
    ],
) -> ABCRabbitMQProducers:
    return RabbitMQHandler(
        auth_producer,
        notification_producer,
        optimization_producer,
    )
