import time

from agents.base_agent import BaseAgent
from config_loader import load_modbus_map
from modbus_client import modbus


class CraneAgent(BaseAgent):

    SAFE_HEIGHT = 220

    def __init__(self, name, model, positions, use_modbus=True):
        super().__init__(name, model)

        self.positions = positions
        self.modbus_map = load_modbus_map()
        self.use_modbus = use_modbus
        self.busy = False

    def get_current_position(self):
        values = modbus.read_registers(
            self.modbus_map["atX"],
            2
        )

        return values[0], values[1]

    def get_current_x(self):
        x, _ = self.get_current_position()
        return x

    def wait_until_arrived(self, target_x, target_y):
        if not self.use_modbus:
            time.sleep(0.5)
            return

        while True:
            at_x, at_y = self.get_current_position()

            if at_x == target_x and at_y == target_y:
                break

            time.sleep(0.1)

    def move_to(self, x, y):
        if self.use_modbus:
            modbus.write_register(
                self.modbus_map["setX"],
                x
            )

            modbus.write_register(
                self.modbus_map["setY"],
                y
            )

        self.wait_until_arrived(x, y)

    def set_vacuum(self, state):
        value = 1 if state else 0

        if self.use_modbus:
            modbus.write_register(
                self.modbus_map["vacuum"],
                value
            )

        time.sleep(0.3)

    def pick_or_place(self, x, y, vacuum_state):
        current_x, current_y = self.get_current_position()

        # 1. Always move vertically up first
        if current_y < self.SAFE_HEIGHT:
            self.move_to(current_x, self.SAFE_HEIGHT)

        time.sleep(0.3)

        # 2. Move horizontally only at safe height
        self.move_to(x, self.SAFE_HEIGHT)

        time.sleep(0.3)

        # 3. Move down to station
        self.move_to(x, y)

        time.sleep(0.3)

        # 4. Pick or place
        self.set_vacuum(vacuum_state)

        time.sleep(0.5)

        # 5. Move back up before any other movement
        self.move_to(x, self.SAFE_HEIGHT)

        time.sleep(0.3)

    def transport(self, part_id, from_station, to_station):
        from_pos = self.positions[from_station]
        to_pos = self.positions[to_station]

        print(
            f"[Crane] Transporting Part {part_id} "
            f"from {from_station} ({from_pos['x']},{from_pos['y']}) "
            f"to {to_station} ({to_pos['x']},{to_pos['y']})"
        )

        self.pick_or_place(
            from_pos["x"],
            from_pos["y"],
            True
        )

        self.pick_or_place(
            to_pos["x"],
            to_pos["y"],
            False
        )

    def step(self):
        while self.inbox:
            msg = self.inbox.pop(0)

            if msg.performative == "REQUEST_MOVE":
                part_id = msg.content["part_id"]
                from_station = msg.content["from"]
                to_station = msg.content["to"]

                self.busy = True

                self.transport(
                    part_id,
                    from_station,
                    to_station
                )

                self.busy = False

                self.send(
                    receiver=msg.sender,
                    performative="MOVE_FINISHED",
                    content={
                        "part_id": part_id,
                        "to": to_station
                    }
                )