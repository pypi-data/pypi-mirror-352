from uuid import UUID

from pydantic import BaseModel


class CreateUserVerifyDto(BaseModel):
    user_id: UUID
    otp: str
