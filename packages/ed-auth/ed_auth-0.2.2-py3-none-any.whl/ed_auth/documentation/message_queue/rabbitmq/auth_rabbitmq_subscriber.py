from ed_domain.common.logging import get_logger
from ed_infrastructure.documentation.message_queue.rabbitmq.rabbitmq_producer import \
    RabbitMQProducer

from ed_auth.application.features.auth.dtos import (CreateUserDto,
                                                    DeleteUserDto,
                                                    UpdateUserDto)
from ed_auth.documentation.message_queue.rabbitmq.abc_auth_rabbitmq_subscriber import (
    ABCAuthRabbitMQSubscriber, AuthQueues)
from ed_auth.documentation.message_queue.rabbitmq.auth_queue_descriptions import \
    AuthQueueDescriptions

LOG = get_logger()


class AuthRabbitMQSubscriber(ABCAuthRabbitMQSubscriber):
    def __init__(self, connection_url: str) -> None:
        descriptions = AuthQueueDescriptions(connection_url).descriptions
        self._producers = {
            queue["name"]: RabbitMQProducer[queue["request_model"]](
                queue["connection_parameters"]["url"],
                queue["connection_parameters"]["queue"],
            )
            for queue in descriptions
            if "request_model" in queue
        }

    async def create_user(self, create_user_dto: CreateUserDto) -> None:
        if producer := self._producers.get(AuthQueues.CREATE_USER):
            LOG.info(f"Publishing to {producer._queue} queue.")
            await producer.publish(create_user_dto)

        LOG.info(
            f"Could not find producer for {AuthQueues.CREATE_USER} queue.")

    async def delete_user(self, delete_user_dto: DeleteUserDto) -> None:
        if producer := self._producers.get(AuthQueues.DELETE_USER):
            LOG.info(f"Publishing to {producer._queue} queue.")
            await producer.publish(delete_user_dto)

        LOG.info(
            f"Could not find producer for {AuthQueues.DELETE_USER} queue.")

    async def update_user(self, update_user_dto: UpdateUserDto) -> None:
        if producer := self._producers.get(AuthQueues.UPDATE_USER):
            LOG.info(f"Publishing to {producer._queue} queue.")
            await producer.publish(update_user_dto)

        LOG.info(
            f"Could not find producer for {AuthQueues.UPDATE_USER} queue.")

    async def start(self) -> None:
        LOG.info("Starting all RabbitMQ producers.")
        for producer in self._producers.values():
            LOG.info(f"Starting producer for {producer._queue}")
            await producer.start()

    def stop_producers(self) -> None:
        LOG.info("Stopping all RabbitMQ producers.")
        for producer in self._producers.values():
            LOG.info(f"Stopping producer for {producer._queue}")
            producer.stop()
