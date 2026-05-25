import random


EVENTS = [
    "sensor",
    "timer",
    "watchdog"
]


def random_state():

    return {

        "obstacle": random.choice([True, False]),
        "highSpeed": random.choice([True, False]),
        "frontObstacle": random.choice([True, False]),
        "collisionRisk": random.choice([True, False]),
        "batteryLow": random.choice([True, False]),
        "chargingStationNear": random.choice([True, False]),
        "goalVisible": random.choice([True, False]),
        "idle": random.choice([True, False]),
        "communicationLost": random.choice([True, False]),
        "sensorFailure": random.choice([True, False]),
        "localizationLost": random.choice([True, False]),
    }


def random_event_trace(length=10):

    return [

        random.choice(EVENTS)

        for _ in range(length)
    ]
