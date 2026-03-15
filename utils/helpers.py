import random


def generate_id():

    return random.randint(10000, 99999)


def calculate_risk_score(value):

    if value > 80:
        return "CRITICAL"

    if value > 50:
        return "HIGH"

    if value > 20:
        return "MEDIUM"

    return "LOW"