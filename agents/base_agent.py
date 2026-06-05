class BaseAgent:
    def __init__(self, name, model):
        self.name = name
        self.model = model
        self.inbox = []

    def receive(self, message):
        self.inbox.append(message)

    def send(self, receiver, performative, content=None):
        self.model.send_message(
            sender=self.name,
            receiver=receiver,
            performative=performative,
            content=content or {}
        )

    def step(self):
        pass