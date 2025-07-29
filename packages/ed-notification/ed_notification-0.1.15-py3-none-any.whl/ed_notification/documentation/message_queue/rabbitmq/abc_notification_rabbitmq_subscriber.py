from abc import ABCMeta, abstractmethod
from enum import StrEnum

from ed_notification.application.features.notification.dtos.send_notification_dto import \
    SendNotificationDto


class NotificationQueues(StrEnum):
    SEND_NOTIFICATION = "notification.send_notification"


class ABCNotificationRabbitMQSubscriber(metaclass=ABCMeta):
    @abstractmethod
    async def send_notification(
        self, send_notification_dto: SendNotificationDto
    ) -> None: ...
