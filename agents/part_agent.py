from agents.base_agent import BaseAgent


class PartAgent(BaseAgent):
    def __init__(
        self,
        name,
        model,
        part_id,
        part_type,
        source_name
    ):
        super().__init__(name, model)

        self.part_id = part_id
        self.part_type = part_type
        self.current_location = source_name

        if self.part_type == 1:
            self.route = ["Process1"]

        elif self.part_type == 2:
            self.route = ["Process2", "Process1"]

        else:
            raise ValueError(f"Unknown part type: {self.part_type}")

        self.current_step = 0
        self.state = "REQUEST_PROCESS"
        self.proposals = []
        self.selected_process = None
        self.wait_counter = 0

    def current_required_process(self):
        return self.route[self.current_step]

    def send_cfp(self):
        required_process = self.current_required_process()

        print(
            f"[Part {self.part_id}] CFP for {required_process}"
        )

        self.proposals = []

        for agent_name in self.model.agents:
            if agent_name.startswith("Process"):
                self.send(
                    receiver=agent_name,
                    performative="CFP",
                    content={
                        "part_id": self.part_id,
                        "process": required_process
                    }
                )

        self.state = "WAITING_PROPOSALS"
        self.wait_counter = 0

    def choose_best_proposal(self):
        if not self.proposals:
            return None

        best = min(
            self.proposals,
            key=lambda p: p["cost"]
        )

        return best["process_agent"]

    def move_to_process(self):
        self.send(
            receiver="Crane",
            performative="REQUEST_MOVE",
            content={
                "part_id": self.part_id,
                "from": self.current_location,
                "to": self.selected_process
            }
        )

        self.state = "MOVING_TO_PROCESS"

    def start_process(self):
        self.send(
            receiver=self.selected_process,
            performative="START_PROCESS",
            content={
                "part_id": self.part_id
            }
        )

        self.state = "PROCESSING"

    def move_to_sink(self):
        self.send(
            receiver="Crane",
            performative="REQUEST_MOVE",
            content={
                "part_id": self.part_id,
                "from": self.current_location,
                "to": "Sink"
            }
        )

        self.state = "MOVING_TO_SINK"

    def handle_process_failure(self):
        print(
            f"[Part {self.part_id}] Process failed. "
            f"Starting new negotiation."
        )

        self.state = "REQUEST_PROCESS"

    def step(self):
        while self.inbox:
            msg = self.inbox.pop(0)

            if msg.performative == "PROPOSE":
                self.proposals.append(msg.content)

            elif msg.performative == "PROCESS_ACCEPTED":
                self.selected_process = msg.content["process_agent"]

                print(
                    f"[Part {self.part_id}] Accepted by {self.selected_process}"
                )

                self.move_to_process()

            elif msg.performative == "PROCESS_REJECTED":
                print(
                    f"[Part {self.part_id}] Proposal rejected, negotiating again"
                )

                self.state = "REQUEST_PROCESS"

            elif msg.performative == "MOVE_FINISHED":
                if self.state == "MOVING_TO_PROCESS":
                    self.current_location = self.selected_process
                    self.start_process()

                elif self.state == "MOVING_TO_SINK":
                    self.current_location = "Sink"
                    self.state = "DONE"
                    self.model.completed_parts += 1

                    print(f"[Part {self.part_id}] Completed at Sink")

            elif msg.performative == "PROCESS_FINISHED":
                self.current_step += 1

                if self.current_step >= len(self.route):
                    self.move_to_sink()
                else:
                    self.state = "REQUEST_PROCESS"

            elif msg.performative == "PROCESS_FAILED":
                self.handle_process_failure()

        if self.state == "REQUEST_PROCESS":
            self.send_cfp()

        elif self.state == "WAITING_PROPOSALS":
            self.wait_counter += 1

            if self.proposals:
                selected = self.choose_best_proposal()

                print(
                    f"[Part {self.part_id}] Choosing {selected}"
                )

                self.send(
                    receiver=selected,
                    performative="ACCEPT_PROPOSAL",
                    content={
                        "part_id": self.part_id
                    }
                )

                self.state = "WAITING_ACCEPT"

            elif self.wait_counter > 5:
                print(
                    f"[Part {self.part_id}] No proposal received, retrying CFP"
                )

                self.state = "REQUEST_PROCESS"