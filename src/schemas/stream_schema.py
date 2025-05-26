from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class StreamSchema(BaseModel):
    id: int
    device_id: str
    frame_width: Optional[int] = 1920
    frame_height: Optional[int] = 1080

    @field_validator("device_id")
    def device_id_alphanumeric(cls, field: str):
        if not field.replace('_', '').isalnum():
            raise ValueError("Device id for new camera must contain only alpha-numeric values or '_'")
        return field

    @field_validator("frame_width", "frame_height")
    def frame_size_positive(cls, field: int):
        if field <= 0:
            raise ValueError("Frame dimensions must be positive integers")
        return field
