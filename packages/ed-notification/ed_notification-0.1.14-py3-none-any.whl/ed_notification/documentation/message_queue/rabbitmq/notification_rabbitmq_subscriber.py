from ed_domain.common.logging import get_logger
from ed_infrastructure.documentation.message_queue.rabbitmq.rabbitmq_producer import \
    RabbitMQProducer

from ed_notification.application.features.notification.dtos.send_notification_dto import \
    SendNotificationDto
from ed_notification.documentation.message_queue.rabbitmq.abc_notification_rabbitmq_subscriber import (
    ABCNotificationRabbitMQSubscriber, NotificationQueues)
from ed_notification.documentation.message_queue.rabbitmq.notification_queue_descriptions import \
    NotificationQueueDescriptions

LOG = get_logger()


class NotificationRabbitMQSubscriber(ABCNotificationRabbitMQSubscriber):
    def __init__(self, connection_url: str) -> None:
        self._connection_url = connection_url
        descriptions = NotificationQueueDescriptions(
            connection_url).descriptions

        self._producers = {
            description["name"]: RabbitMQProducer[description["request_model"]](
                url=description["connection_parameters"]["url"],
                queue=description["connection_parameters"]["queue"],
            )
            for description in descriptions
            if "request_model" in description
        }

    async def start(self) -> None:
        LOG.info("Starting producers...")
        for producer in self._producers.values():
            try:
                LOG.info(f"Starting producer for queue: {producer._queue}")
                await producer.start()
            except Exception as e:
                LOG.error(
                    f"Failed to start producer for queue {producer._queue}: {e}")
                raise

    async def send_notification(
        self, send_notification_dto: SendNotificationDto
    ) -> None:
        if producer := self._producers.get(NotificationQueues.SEND_NOTIFICATION.value):
            LOG.info(
                f"Publishing to queue: {producer._queue} the message: {send_notification_dto}"
            )
            await producer.publish(send_notification_dto)


if __name__ == "__main__":
    # Example usage
    queue_names = NotificationQueues.__members__.keys()
    print(queue_names)
