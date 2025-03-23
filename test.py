from requests import post, get

post("http://127.0.0.1:8080/schedule", json={
    "name": "a",
    "uuid": 1,
    "time_format": "hours",
    "repeats_value": 5,
    "duration": 10
})

post("http://127.0.0.1:8080/schedule", json={
    "name": "b",
    "uuid": 2,
    "time_format": "hours",
    "repeats_value": 6,
    "duration": 15
})

post("http://127.0.0.1:8080/schedule", json={
    "name": "c",
    "uuid": 2,
    "time_format": "days",
    "repeats_value": 7,
    "duration": 13
})

print(get("http://127.0.0.1:8080/next_takings?user_id=1").json())
print(get("http://127.0.0.1:8080/all_takings?user_id=1").json())
print(get("http://127.0.0.1:8080/schedules?user_id=1").json())
print()
print(get("http://127.0.0.1:8080/next_takings?user_id=2").json())
print(get("http://127.0.0.1:8080/all_takings?user_id=2").json())
print(get("http://127.0.0.1:8080/schedules?user_id=2").json())
