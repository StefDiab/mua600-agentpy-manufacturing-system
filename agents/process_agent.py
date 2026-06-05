import time

from agents.base_agent import BaseAgent
from config_loader import load_modbus_map
from modbus_client import modbus


class ProcessAgent(BaseAgent):
    def __init__(
        self,
        name,
        model,
        capability,
        base_cost,
        use_modbus=True
    ):
        super().__init__(name, model)

        self.capability = capability
        self.base_cost = base_cost

        self.busy = False
        self.failed = False
        self.current_part = None

        self.use_modbus = use_modbus
        self.modbus_map = load_modbus_map()

        if self.name == "Process1":
            self.start_register = self.modbus_map["startp1"]
            self.running_register = self.modbus_map["p1_running"]

        elif self.name == "Process2":
            self.start_register = self.modbus_map["startp2"]
            self.running_register = self.modbus_map["p2_running"]

        else:
            # ProcessBackup is represented by Process2 in the simulator
            self.start_register = self.modbus_map["startp2"]
            self.running_register = self.modbus_map["p2_running"]

    def calculate_cost(self):
        if self.busy:
            return self.base_cost + 10

        return self.base_cost

    def start_real_process(self):
        if not self.use_modbus:
            time.sleep(2)
            return

        # Send start pulse
        modbus.write_register(self.start_register, 1)
        time.sleep(0.5)
        modbus.write_register(self.start_register, 0)

        # Wait a little for simulator to react
        time.sleep(0.5)

        # Wait until process starts running
        started = False

        for _ in range(30):
            running = modbus.read_registers(
                self.running_register,
                1
            )[0]

            if running == 1:
                started = True
                break

            time.sleep(0.2)

        # Wait until process finishes
        if started:
            while True:
                running = modbus.read_registers(
                    self.running_register,
                    1
                )[0]

                if running == 0:
                    break

                time.sleep(0.2)

        # Extra safety delay before crane picks from process
        time.sleep(1.0)

    def step(self):
        while self.inbox:
            msg = self.inbox.pop(0)

            if msg.performative == "SET_FAILURE":
                self.failed = True
                self.model.failed_processes.add(self.name)
                print(f"[{self.name}] FAILED")

            elif msg.performative == "RECOVER":
                self.failed = False

                if self.name in self.model.failed_processes:
                    self.model.failed_processes.remove(self.name)

                print(f"[{self.name}] RECOVERED")

            elif msg.performative == "CFP":
                required_process = msg.content["process"]
                part_id = msg.content["part_id"]

                # Failed process cannot propose
                if self.failed:
                    print(
                        f"[{self.name}] Cannot propose for Part {part_id}, failed"
                    )
                    continue

                # Backup should only be used when Process1 is failed
                if self.name == "ProcessBackup":
                    if "Process1" not in self.model.failed_processes:
                        continue

                # Busy process should not propose in the real simulator
                if self.busy:
                    print(
                        f"[{self.name}] Cannot propose for Part {part_id}, busy"
                    )
                    continue

                if self.capability == required_process:
                    cost = self.calculate_cost()

                    print(
                        f"[{self.name}] PROPOSE to Part {part_id} "
                        f"for {required_process}, cost={cost}"
                    )

                    self.send(
                        receiver=msg.sender,
                        performative="PROPOSE",
                        content={
                            "part_id": part_id,
                            "process": required_process,
                            "process_agent": self.name,
                            "cost": cost
                        }
                    )
            elif msg.performative == "ACCEPT_PROPOSAL":
                part_id = msg.content["part_id"]

                if self.failed:
                    self.send(
                        receiver=msg.sender,
                        performative="PROCESS_REJECTED",
                        content={
                            "part_id": part_id,
                            "reason": "failed"
                        }
                    )
                    continue

                if self.busy:
                    self.send(
                        receiver=msg.sender,
                        performative="PROCESS_REJECTED",
                        content={
                            "part_id": part_id,
                            "reason": "busy"
                        }
                    )
                    continue

                self.busy = True
                self.current_part = part_id

                print(f"[{self.name}] ACCEPTED Part {part_id}")

                self.send(
                    receiver=msg.sender,
                    performative="PROCESS_ACCEPTED",
                    content={
                        "part_id": part_id,
                        "process_agent": self.name
                    }
                )

            elif msg.performative == "START_PROCESS":
                part_id = msg.content["part_id"]

                if self.failed:
                    print(f"[{self.name}] Failed during Part {part_id}")

                    self.busy = False
                    self.current_part = None

                    self.send(
                        receiver=msg.sender,
                        performative="PROCESS_FAILED",
                        content={
                            "part_id": part_id,
                            "process_agent": self.name
                        }
                    )
                    continue

                print(f"[{self.name}] Processing Part {part_id}")

                self.start_real_process()

                if self.failed:
                    print(f"[{self.name}] Failed during operation")

                    self.busy = False
                    self.current_part = None

                    self.send(
                        receiver=msg.sender,
                        performative="PROCESS_FAILED",
                        content={
                            "part_id": part_id,
                            "process_agent": self.name
                        }
                    )
                    continue

                print(f"[{self.name}] Finished Part {part_id}")

                self.busy = False
                self.current_part = None

                self.send(
                    receiver=msg.sender,
                    performative="PROCESS_FINISHED",
                    content={
                        "part_id": part_id,
                        "process_agent": self.name
                    }
                )