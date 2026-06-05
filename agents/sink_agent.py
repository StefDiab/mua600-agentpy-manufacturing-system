from agents.base_agent import BaseAgent


class SinkAgent(BaseAgent):
    def step(self):
        while self.inbox:
            msg = self.inbox.pop(0)

            if msg.performative == "RECEIVE_PART":
                print(f"[Sink] Received Part {msg.content['part_id']}")