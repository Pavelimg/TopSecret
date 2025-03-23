import datetime

from fastapi import FastAPI
import uvicorn  # https://fastapi.tiangolo.com/tutorial/debugging

from Models import *
from DB import *
from config import *

app = FastAPI()
database = DBWorker()


def get_schedule(start_time, repeat_time, repeats) -> list[datetime.datetime]:
    if repeats == -1:
        repeats = size_of_infinity
    drugs_time = []
    current_time = start_time
    for _ in range(repeats):
        # Проверяем, не выпадает ли время приёма на ночь (с 22:00 до 8:00)
        if (current_time % (24 * 60)) >= evening_time or (current_time % (24 * 60)) < morning_time:
            # Если выпадает на ночь, переносим на утро следующего дня
            current_time = (current_time // (24 * 60) + 1) * (24 * 60) + morning_time
        dt = datetime.datetime.fromtimestamp(current_time * 60)
        rounded_minutes = (dt.minute // 15) * 15
        if dt.minute % 15 >= 7.5:  # Если остаток от деления на 15 больше или равен 7.5, округляем вверх
            rounded_minutes += 15
        if rounded_minutes >= 60:  # Если округление минут превышает 59, увеличиваем час и обнуляем минуты
            rounded_minutes = 0
            dt += datetime.timedelta(hours=1)
        drugs_time.append(dt.replace(minute=rounded_minutes))
        current_time += repeat_time
    return drugs_time


# Нет в ТЗ
@app.get("/all_takings")
async def all_takings(user_id: int):
    res = {}
    for i in database.get_drugs_by_uuid(user_id):
        res[i[0]] = list(get_schedule(i[1], i[2], i[3]))
    return res


@app.get("/next_takings")
async def next_takings(user_id: int):
    res = {}
    time_now = datetime.datetime.now()
    print(type(time_now))
    for i in database.get_drugs_by_uuid(user_id):
        res[i[0]] = list(filter(
            lambda x: True if time_now < x < (time_now + datetime.timedelta(minutes=next_takings_period)) else False,
            get_schedule(i[1], i[2], i[3])))
    return res


@app.get("/schedules")
async def schedules(user_id: int):
    res = {}
    for i in database.get_drugs_by_uuid(user_id):
        res[i[0]] = {
            "start_time": datetime.datetime.fromtimestamp(i[1] * 60),
            "repeat_time": datetime.timedelta(minutes=i[2]),
            "repeats": i[3]
        }
    return res


@app.post("/schedule")
async def new_record(drugs: NewDrugs):
    curr_time = int(datetime.datetime.now().timestamp()) // 60

    repeats_min = drugs.repeats_value
    match drugs.time_format:
        case "hours":
            repeats_min *= 60
        case "days":
            repeats_min *= 60 * 24
        case "week":
            repeats_min *= 60 * 24 * 7

    database.add_drug(user_id=drugs.uuid,
                      name=drugs.name,
                      start_time=curr_time,
                      repeat_time=repeats_min,
                      repeats=drugs.duration)


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
