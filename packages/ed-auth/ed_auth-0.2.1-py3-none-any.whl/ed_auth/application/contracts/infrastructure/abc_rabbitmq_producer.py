from abc import ABCMeta, abstractmethod

from ed_core.documentation.message_queue.rabbitmq.abc_core_rabbitmq_subscriber import \
    ABCCoreRabbitMQSubscriber
from ed_notification.documentation.message_queue.rabbitmq.abc_notification_rabbitmq_subscriber import \
    ABCNotificationRabbitMQSubscriber


class ABCRabbitMQProducers(metaclass=ABCMeta):
    @property
    @abstractmethod
    def notification(self) -> ABCNotificationRabbitMQSubscriber: ...

    @property
    @abstractmethod
    def core(self) -> ABCCoreRabbitMQSubscriber: ...
