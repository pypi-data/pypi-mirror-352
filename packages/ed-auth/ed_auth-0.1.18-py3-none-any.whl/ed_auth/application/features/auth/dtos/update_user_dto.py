from typing import Optional

from pydantic import BaseModel


class UpdateUserDto(BaseModel):
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
