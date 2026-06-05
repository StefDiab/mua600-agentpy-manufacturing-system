from mas_model import MASModel

from config_loader import load_positions
from planner import extract_orders

from agents.crane_agent import CraneAgent
from agents.source_agent import SourceAgent
from agents.process_agent import ProcessAgent
from agents.sink_agent import SinkAgent


def main():
    print("\n========== AGENTPY-LIKE MAS DEMO ==========")

    positions = load_positions()

    model = MASModel()

    crane = CraneAgent(
        name="Crane",
        model=model,
        positions=positions,
        use_modbus=True
    )

    source1 = SourceAgent("Source1", model)
    source2 = SourceAgent("Source2", model)

    process1 = ProcessAgent(
        name="Process1",
        model=model,
        capability="Process1",
        base_cost=1,
        use_modbus=True
    )

    process2 = ProcessAgent(
        name="Process2",
        model=model,
        capability="Process2",
        base_cost=1,
        use_modbus=True
    )

    process_backup = ProcessAgent(
        name="ProcessBackup",
        model=model,
        capability="Process1",
        base_cost=5,
        use_modbus=True
    )

    sink = SinkAgent("Sink", model)

    model.add_agent(crane)
    model.add_agent(source1)
    model.add_agent(source2)
    model.add_agent(process1)
    model.add_agent(process2)
    model.add_agent(process_backup)
    model.add_agent(sink)

    user_order = input("\nWrite production order: ")

    print("\nUSER ORDER:")
    print(user_order)

    orders = extract_orders(user_order)

    print("\nPARSED ORDERS:")
    print(orders)

    for _ in range(orders.get("type1", 0)):
        source1.create_part(part_type=1)

    for _ in range(orders.get("type2", 0)):
        source2.create_part(part_type=2)

    model.run(max_steps=500)

    print("\n========== DEMO FINISHED ==========")


if __name__ == "__main__":
    main()