import json


def load_positions():
    with open("config/positions.json", "r") as file:
        return json.load(file)


def load_modbus_map():
    with open("config/modbus_map.json", "r") as file:
        return json.load(file)