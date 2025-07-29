from ed_domain.documentation.message_queue.rabbitmq.abc_queue_descriptions import \
    ABCQueueDescriptions
from ed_domain.documentation.message_queue.rabbitmq.definitions.queue_description import \
    QueueDescription

from ed_auth.application.features.auth.dtos import (CreateUserDto,
                                                    DeleteUserDto,
                                                    UpdateUserDto)
from ed_auth.documentation.message_queue.rabbitmq.abc_auth_rabbitmq_subscriber import \
    AuthQueues


class AuthQueueDescriptions(ABCQueueDescriptions):
    def __init__(self, connection_url: str) -> None:
        self._descriptions: list[QueueDescription] = [
            {
                "name": AuthQueues.CREATE_USER,
                "connection_parameters": {
                    "url": connection_url,
                    "queue": AuthQueues.CREATE_USER,
                },
                "durable": True,
                "request_model": CreateUserDto,
            },
            {
                "name": AuthQueues.DELETE_USER,
                "connection_parameters": {
                    "url": connection_url,
                    "queue": AuthQueues.DELETE_USER,
                },
                "durable": True,
                "request_model": DeleteUserDto,
            },
            {
                "name": AuthQueues.UPDATE_USER,
                "connection_parameters": {
                    "url": connection_url,
                    "queue": AuthQueues.UPDATE_USER,
                },
                "durable": True,
                "request_model": UpdateUserDto,
            },
        ]

    @property
    def descriptions(self) -> list[QueueDescription]:
        return self._descriptions
