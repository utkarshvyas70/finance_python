from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Success"

    model_config = {"from_attributes": True}