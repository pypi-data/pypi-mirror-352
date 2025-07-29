from pydantic import BaseModel


class DropOffOrderVerifyDto(BaseModel):
    otp: str
