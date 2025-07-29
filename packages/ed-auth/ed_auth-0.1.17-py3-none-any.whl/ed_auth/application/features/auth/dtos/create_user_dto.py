from datetime import UTC, datetime
from typing import Optional

from ed_domain.core.entities import AuthUser
from ed_domain.core.repositories import ABCUnitOfWork
from ed_domain.utils.security.password import ABCPasswordHandler
from pydantic import BaseModel

from ed_auth.common.generic_helpers import get_new_id


class CreateUserDto(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

    def create_user(
        self, uow: ABCUnitOfWork, password_handler: ABCPasswordHandler
    ) -> AuthUser:
        hashed_password = password_handler.hash(self.password or "")

        return uow.auth_user_repository.create(
            AuthUser(
                id=get_new_id(),
                first_name=self.first_name or "",
                last_name=self.last_name or "",
                email=self.email or "",
                phone_number=self.phone_number or "",
                password_hash=hashed_password,
                verified=False,
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                logged_in=False,
            )
        )
