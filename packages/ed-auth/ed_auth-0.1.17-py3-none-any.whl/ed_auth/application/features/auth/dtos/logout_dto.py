from pydantic import BaseModel


class LogoutDto(BaseModel):
    token: str
