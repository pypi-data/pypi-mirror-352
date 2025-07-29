from pydantic import BaseModel


class VerifyTokenDto(BaseModel):
    token: str
