from pydantic import BaseModel


class PickUpOrderVerifyDto(BaseModel):
    otp: str
