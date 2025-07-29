from typing import Optional

from pydantic import BaseModel


class LoginUserDto(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
