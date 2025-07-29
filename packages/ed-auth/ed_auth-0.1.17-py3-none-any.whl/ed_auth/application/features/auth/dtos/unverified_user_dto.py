from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UnverifiedUserDto(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
