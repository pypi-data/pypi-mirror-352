from uuid import UUID

from pydantic import BaseModel


class LoginUserVerifyDto(BaseModel):
    user_id: UUID
    otp: str
