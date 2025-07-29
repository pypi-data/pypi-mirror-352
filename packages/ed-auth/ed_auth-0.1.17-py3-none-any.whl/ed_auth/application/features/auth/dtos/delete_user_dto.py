from uuid import UUID

from pydantic import BaseModel


class DeleteUserDto(BaseModel):
    id: UUID
