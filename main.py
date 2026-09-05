import datetime
import os

import uvicorn
from fastapi import FastAPI, status

from DB import DBWorker
from Models import NewDrug
from config import EVENING_TIME, MAX_OPEN_ENDED_TAKINGS, MORNING_TIME, NEXT_TAKINGS_PERIOD

app = FastAPI(
    title="Medication Schedule API",
    description="API for creating medication schedules and calculating upcoming doses.",
    version="1.0.0",
)
database = DBWorker(os.getenv("DATABASE_PATH", "db.db"))

UNIT_TO_MINUTES = {
    "minute": 1,
    "minutes": 1,
    "hour": 60,
    "hours": 60,
    "day": 60 * 24,
    "days": 60 * 24,
    "week": 60 * 24 * 7,
    "weeks": 60 * 24 * 7,
}


def get_schedule(start_time: int, repeat_time: int, repeats: int) -> list[datetime.datetime]:
    """Build a schedule, moving night-time doses to the next morning."""
    if repeats == -1:
        repeats = MAX_OPEN_ENDED_TAKINGS

    taking_times: list[datetime.datetime] = []
    current_time = start_time

    for _ in range(repeats):
        minute_of_day = current_time % (24 * 60)
        if minute_of_day >= EVENING_TIME or minute_of_day < MORNING_TIME:
            current_time = (current_time // (24 * 60) + 1) * (24 * 60) + MORNING_TIME

        value = datetime.datetime.fromtimestamp(current_time * 60)
        rounded_minutes = ((value.minute + 7) // 15) * 15
        if rounded_minutes == 60:
            value += datetime.timedelta(hours=1)
            rounded_minutes = 0

        taking_times.append(value.replace(minute=rounded_minutes, second=0, microsecond=0))
        current_time += repeat_time

    return taking_times


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/all_takings")
async def all_takings(user_id: int) -> dict[str, list[datetime.datetime]]:
    return {
        name: get_schedule(start_time, repeat_time, repeats)
        for name, start_time, repeat_time, repeats in database.get_drugs_by_uuid(user_id)
    }


@app.get("/next_takings")
async def next_takings(user_id: int) -> dict[str, list[datetime.datetime]]:
    now = datetime.datetime.now()
    period_end = now + datetime.timedelta(minutes=NEXT_TAKINGS_PERIOD)
    result: dict[str, list[datetime.datetime]] = {}

    for name, start_time, repeat_time, repeats in database.get_drugs_by_uuid(user_id):
        result[name] = [
            taking_time
            for taking_time in get_schedule(start_time, repeat_time, repeats)
            if now < taking_time < period_end
        ]
    return result


@app.get("/schedules")
async def schedules(user_id: int) -> dict[str, dict[str, object]]:
    return {
        name: {
            "start_time": datetime.datetime.fromtimestamp(start_time * 60),
            "repeat_time_minutes": repeat_time,
            "repeats": repeats,
        }
        for name, start_time, repeat_time, repeats in database.get_drugs_by_uuid(user_id)
    }


@app.post("/schedule", status_code=status.HTTP_201_CREATED)
async def new_record(drug: NewDrug) -> dict[str, int | str]:
    repeat_time = drug.repeats_value * UNIT_TO_MINUTES[drug.time_format]
    start_time = int(datetime.datetime.now().timestamp()) // 60
    schedule_id = database.add_drug(
        user_id=drug.uuid,
        name=drug.name,
        start_time=start_time,
        repeat_time=repeat_time,
        repeats=drug.duration,
    )
    return {"status": "created", "schedule_id": schedule_id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

