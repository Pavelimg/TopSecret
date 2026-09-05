from typing import Literal

from pydantic import BaseModel, Field, field_validator


class NewDrug(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    time_format: Literal[
        "minute", "minutes", "hour", "hours", "day", "days", "week", "weeks"
    ]
    repeats_value: int = Field(gt=0)
    duration: int = -1
    uuid: int = Field(gt=0)

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if value == -1 or value > 0:
            return value
        raise ValueError("duration must be -1 or a positive integer")

