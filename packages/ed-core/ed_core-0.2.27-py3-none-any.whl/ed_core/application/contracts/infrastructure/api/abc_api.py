from abc import ABCMeta, abstractmethod

from ed_auth.documentation.api.abc_auth_api_client import ABCAuthApiClient
from ed_notification.documentation.api.abc_notification_api_client import \
    ABCNotificationApiClient


class ABCApi(metaclass=ABCMeta):
    @property
    @abstractmethod
    def auth_api(self) -> ABCAuthApiClient: ...

    @property
    @abstractmethod
    def notification_api(self) -> ABCNotificationApiClient: ...
