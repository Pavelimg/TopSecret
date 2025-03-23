from pydantic import BaseModel


class NewDrugs(BaseModel):
    name: str
    time_format: str  # minute/hour/day/week/
    repeats_value: int
    duration: int | None = None
    uuid: int
