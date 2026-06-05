from collections import deque


class Message:
    def __init__(self, sender, receiver, performative, content=None):
        self.sender = sender
        self.receiver = receiver
        self.performative = performative
        self.content = content or {}


class MASModel:
    def __init__(self):
        self.agents = {}
        self.message_queue = deque()
        self.step_count = 0
        self.completed_parts = 0

        # Used for failure recovery negotiation
        self.failed_processes = set()

    def add_agent(self, agent):
        self.agents[agent.name] = agent

    def send_message(self, sender, receiver, performative, content=None):
        msg = Message(
            sender=sender,
            receiver=receiver,
            performative=performative,
            content=content or {}
        )

        self.message_queue.append(msg)

    def deliver_messages(self):
        while self.message_queue:
            msg = self.message_queue.popleft()

            if msg.receiver in self.agents:
                self.agents[msg.receiver].receive(msg)
            else:
                print(f"[MODEL] Unknown receiver: {msg.receiver}")

    def step(self):
        self.step_count += 1

        self.deliver_messages()

        for agent in list(self.agents.values()):
            agent.step()

    def run(self, max_steps=500):
        for _ in range(max_steps):
            self.step()

            all_parts_done = True
            has_parts = False

            for agent in self.agents.values():
                if agent.__class__.__name__ == "PartAgent":
                    has_parts = True

                    if agent.state != "DONE":
                        all_parts_done = False

            if has_parts and all_parts_done:
                print("\n[MODEL] All parts completed")
                break