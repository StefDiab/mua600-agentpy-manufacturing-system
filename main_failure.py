from mas_model import MASModel

from config_loader import load_positions
from planner import extract_orders

from agents.crane_agent import CraneAgent
from agents.source_agent import SourceAgent
from agents.process_agent import ProcessAgent
from agents.sink_agent import SinkAgent


def main():
    print("\n========== AGENT NEGOTIATION FAILURE DEMO ==========")

    positions = load_positions()

    model = MASModel()

    crane = CraneAgent(
        name="Crane",
        model=model,
        positions=positions,
        use_modbus=True
    )

    source1 = SourceAgent("Source1", model)

    process1 = ProcessAgent(
        name="Process1",
        model=model,
        capability="Process1",
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
    model.add_agent(process1)
    model.add_agent(process_backup)
    model.add_agent(sink)

    # Set Process1 as failed before negotiation
    model.send_message(
        sender="System",
        receiver="Process1",
        performative="SET_FAILURE",
        content={}
    )

    user_order = input("\nWrite production order for failure demo: ")

    print("\nUSER ORDER:")
    print(user_order)

    orders = extract_orders(user_order)

    print("\nPARSED ORDERS:")
    print(orders)

    type1_qty = orders.get("type1", 0)

    if orders.get("type2", 0) > 0:
        print(
            "\n[WARNING] Failure demo only supports type1 parts. "
            "Type2 parts are ignored in this demo."
        )

    for _ in range(type1_qty):
        source1.create_part(part_type=1)

    model.run(max_steps=300)

    print("\n========== FAILURE DEMO FINISHED ==========")


if __name__ == "__main__":
    main()