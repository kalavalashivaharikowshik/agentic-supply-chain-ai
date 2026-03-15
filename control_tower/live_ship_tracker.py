import time
import random


ships = [
    {"name":"Ship A","lat":22,"lon":120},
    {"name":"Ship B","lat":30,"lon":140}
]


def update_positions():

    for ship in ships:

        ship["lat"] += random.uniform(-0.5,0.5)
        ship["lon"] += random.uniform(-0.5,0.5)

    return ships