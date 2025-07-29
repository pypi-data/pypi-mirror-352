from datetime import UTC, datetime

from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.core.entities import Otp
from ed_domain.core.entities.notification import NotificationType
from ed_domain.core.entities.otp import OtpVerificationAction
from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from ed_domain.utils.otp import ABCOtpGenerator
from ed_domain.utils.security.password import ABCPasswordHandler
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_auth.application.common.responses.base_response import BaseResponse
from ed_auth.application.contracts.infrastructure.abc_rabbitmq_producer import \
    ABCRabbitMQProducers
from ed_auth.application.features.auth.dtos import UnverifiedUserDto
from ed_auth.application.features.auth.dtos.validators import \
    CreateUserDtoValidator
from ed_auth.application.features.auth.requests.commands import \
    CreateUserCommand
from ed_auth.common.generic_helpers import get_new_id

LOG = get_logger()


@request_handler(CreateUserCommand, BaseResponse[UnverifiedUserDto])
class CreateUserCommandHandler(RequestHandler):
    def __init__(
        self,
        rabbitmq_prodcuers: ABCRabbitMQProducers,
        uow: ABCUnitOfWork,
        otp: ABCOtpGenerator,
        password: ABCPasswordHandler,
    ):
        self._rabbitmq_prodcuers = rabbitmq_prodcuers
        self._uow = uow
        self._otp = otp
        self._password = password
        self._dto_validator = CreateUserDtoValidator()

    async def handle(
        self, request: CreateUserCommand
    ) -> BaseResponse[UnverifiedUserDto]:
        dto = request.dto
        email, phone_number = dto.email, dto.phone_number
        dto_validation_response = self._dto_validator.validate(dto)

        if not dto_validation_response.is_valid:
            raise ApplicationException(
                Exceptions.ValidationException,
                "Creating account failed.",
                dto_validation_response.errors,
            )

        if email and self._uow.auth_user_repository.get(email=email):
            raise ApplicationException(
                Exceptions.ConflictException,
                "Creating account failed.",
                ["User with that email already exists."],
            )

        if phone_number and self._uow.auth_user_repository.get(
            phone_number=phone_number
        ):
            raise ApplicationException(
                Exceptions.ConflictException,
                "Creating account failed.",
                ["User with that phone number already exists."],
            )

        user = request.dto.create_user(self._uow, self._password)
        created_otp = self._uow.otp_repository.create(
            Otp(
                id=get_new_id(),
                user_id=user["id"],
                action=OtpVerificationAction.VERIFY_EMAIL,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                expiry_datetime=datetime.now(UTC),
                value=self._otp.generate(),
                deleted=False,
            )
        )

        await self._rabbitmq_prodcuers.notification.send_notification(
            {
                "user_id": user["id"],
                "message": f"Your OTP for logging in is {created_otp['value']}",
                "notification_type": NotificationType.EMAIL,
            }
        )

        return BaseResponse[UnverifiedUserDto].success(
            "User created successfully. Verify email.",
            UnverifiedUserDto(**user),  # type: ignore
        )
