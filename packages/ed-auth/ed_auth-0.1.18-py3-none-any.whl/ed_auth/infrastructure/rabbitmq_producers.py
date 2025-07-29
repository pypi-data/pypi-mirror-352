from ed_core.documentation.message_queue.rabbitmq.abc_core_rabbitmq_subscriber import \
    ABCCoreRabbitMQSubscriber
from ed_core.documentation.message_queue.rabbitmq.core_rabbitmq_subscriber import \
    CoreRabbitMQSubscriber
from ed_notification.documentation.message_queue.rabbitmq.abc_notification_rabbitmq_subscriber import \
    ABCNotificationRabbitMQSubscriber
from ed_notification.documentation.message_queue.rabbitmq.notification_rabbitmq_subscriber import \
    NotificationRabbitMQSubscriber

from ed_auth.application.contracts.infrastructure.abc_rabbitmq_producer import \
    ABCRabbitMQProducers
from ed_auth.common.typing.config import Config


class RabbitMQProducers(ABCRabbitMQProducers):
    def __init__(self, config: Config) -> None:
        self._notification = NotificationRabbitMQSubscriber(
            config["rabbitmq"]["url"])
        self._core = CoreRabbitMQSubscriber(config["rabbitmq"]["url"])

    @property
    def notification(self) -> ABCNotificationRabbitMQSubscriber:
        return self._notification

    @property
    def core(self) -> ABCCoreRabbitMQSubscriber:
        return self._core
