from agents.base_agent import BaseAgent
from agents.part_agent import PartAgent


class SourceAgent(BaseAgent):
    global_part_counter = 0

    def create_part(self, part_type):
        SourceAgent.global_part_counter += 1
        part_id = SourceAgent.global_part_counter

        part = PartAgent(
            name=f"Part{part_id}",
            model=self.model,
            part_id=part_id,
            part_type=part_type,
            source_name=self.name
        )

        self.model.add_agent(part)

        print(
            f"[{self.name}] Created Part {part_id}, type {part_type}"
        )

    def step(self):
        pass