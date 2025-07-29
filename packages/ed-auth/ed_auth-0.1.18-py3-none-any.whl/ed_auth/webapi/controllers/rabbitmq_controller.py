from typing import Annotated
from uuid import UUID

from ed_domain.common.logging import get_logger
from fastapi import Depends
from faststream.rabbit.fastapi import RabbitRouter
from faststream.rabbit.schemas import RabbitQueue
from rmediator.mediator import Mediator

from ed_auth.application.features.auth.dtos import (CreateUserDto,
                                                    DeleteUserDto,
                                                    UpdateUserDto)
from ed_auth.application.features.auth.requests.commands import (
    CreateUserCommand, DeleteUserCommand, UpdateUserCommand)
from ed_auth.common.generic_helpers import get_config
from ed_auth.documentation.message_queue.rabbitmq.abc_auth_rabbitmq_subscriber import \
    AuthQueues
from ed_auth.webapi.dependency_setup import mediator

LOG = get_logger()
config = get_config()
router = RabbitRouter(config["rabbitmq"]["url"])


@router.subscriber(RabbitQueue(AuthQueues.CREATE_USER, durable=True))
async def create_user(
    create_user_dto: CreateUserDto, mediator: Annotated[Mediator, Depends(mediator)]
):
    return await mediator.send(CreateUserCommand(create_user_dto))


@router.subscriber(RabbitQueue(AuthQueues.DELETE_USER, durable=True))
async def delete_user(
    delete_user_dto: DeleteUserDto, mediator: Annotated[Mediator, Depends(mediator)]
):
    return await mediator.send(DeleteUserCommand(delete_user_dto["id"]))


@router.subscriber(RabbitQueue(AuthQueues.UPDATE_USER, durable=True))
async def update_user(
    update_user_dto: UpdateUserDto, mediator: Annotated[Mediator, Depends(mediator)]
):
    return await mediator.send(
        UpdateUserCommand(UUID(update_user_dto["id"]), update_user_dto)
    )
