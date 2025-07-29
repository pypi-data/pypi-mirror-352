from abc import ABCMeta, abstractmethod
from enum import StrEnum

from ed_auth.application.features.auth.dtos import DeleteUserDto, UpdateUserDto
from ed_auth.application.features.auth.dtos.create_user_dto import \
    CreateUserDto


class AuthQueues(StrEnum):
    CREATE_USER = "auth.create_user"
    DELETE_USER = "auth.delete_user"
    UPDATE_USER = "auth.update_user"


class ABCAuthRabbitMQSubscriber(metaclass=ABCMeta):
    @abstractmethod
    async def create_user(self, create_user_dto: CreateUserDto) -> None: ...

    @abstractmethod
    async def delete_user(self, delete_user_dto: DeleteUserDto) -> None: ...

    @abstractmethod
    async def update_user(self, update_user_dto: UpdateUserDto) -> None: ...
