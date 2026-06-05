# MUA600 AgentPy-Inspired Manufacturing System

This project was developed for the MUA600 Multi-Agent Systems course.  
It implements an AgentPy-inspired Multi-Agent System for controlling a crane-based manufacturing cell through Modbus TCP.

The system demonstrates decentralized agent communication, negotiation between agents, LLM-based order planning, Modbus-based crane control, and failure recovery.

---

## Project Overview

The system controls a simulated manufacturing cell with:

- Source1 and Source2
- Process1 and Process2
- ProcessBackup
- Crane
- Sink

A user can write a natural language production order, for example:

```text
Produce 1 type1 part and 1 type2 part
```

The LLM planner converts the order into structured JSON:

```json
{
  "type1": 1,
  "type2": 1
}
```

The agents then negotiate and execute the production process.

---

## Agent Architecture

The system is implemented as a Python-based, AgentPy-inspired Multi-Agent System.

The main agents are:

| Agent | Responsibility |
|---|---|
| SourceAgent | Creates new parts |
| PartAgent | Owns the product route and makes decisions |
| ProcessAgent | Offers processing services and handles processing |
| ProcessBackup | Alternative process resource used during failure |
| CraneAgent | Moves parts between stations using Modbus TCP |
| SinkAgent | Receives completed parts |
| MASModel | Runs the step-based agent simulation and message delivery |

---

## Agent Communication and Negotiation

The agents communicate using message passing.

Main message types:

```text
CFP
PROPOSE
ACCEPT_PROPOSAL
PROCESS_ACCEPTED
PROCESS_REJECTED
REQUEST_MOVE
MOVE_FINISHED
START_PROCESS
PROCESS_FINISHED
SET_FAILURE
RECOVER
```

The negotiation follows this principle:

```text
PartAgent sends CFP
ProcessAgents send PROPOSE
PartAgent chooses the best proposal
PartAgent sends ACCEPT_PROPOSAL
ProcessAgent accepts
CraneAgent moves the part
ProcessAgent processes the part
```

This means the PartAgent does not use a hardcoded resource directly.  
Instead, it asks available process agents and selects the best proposal based on cost and availability.

---

## Implemented Requirements

| Requirement | Description | Status |
|---|---|---|
| R1 | Decentralized control of one product type | Implemented |
| R2 | Multiple product types | Implemented |
| R3 | Plug & Produce configuration | Implemented |
| R4 | Failure recovery | Implemented |
| R5 | LLM planner | Implemented |

---

## Product Routes

### Type 1

```text
Source1 → Process1 → Sink
```

### Type 2

```text
Source2 → Process2 → Process1 → Sink
```

If Process1 fails, the PartAgent negotiates with available process agents and can select ProcessBackup instead.

---

## LLM Planner

The project uses Ollama with the `llama3.2:1b` model.

The LLM is used only for high-level production planning.  
It does not control the crane or write to Modbus directly.

Example:

```text
User order:
Produce 2 type1 parts and 2 type2 parts
```

LLM output:

```json
{
  "type1": 2,
  "type2": 2
}
```

The structured output is then used by the agents to create parts and run the production flow.

---

## Modbus TCP Integration

The system communicates with the crane simulation through Modbus TCP.

Default connection:

```text
Host: 127.0.0.1
Port: 502
```

The crane movement is handled by the `CraneAgent`, which writes target coordinates to the simulator and waits for feedback from the position registers.

Important Modbus registers are stored in:

```text
config/modbus_map.json
```

Station coordinates are stored in:

```text
config/positions.json
```

---

## Project Structure

```text
Agentpy/
│
├── agents/
│   ├── base_agent.py
│   ├── crane_agent.py
│   ├── part_agent.py
│   ├── process_agent.py
│   ├── sink_agent.py
│   └── source_agent.py
│
├── config/
│   ├── modbus_map.json
│   └── positions.json
│
├── config_loader.py
├── main.py
├── main_failure.py
├── mas_model.py
├── modbus_client.py
├── planner.py
├── README.md
└── .gitignore
```

---

## Installation

Create and activate a Python 3.10 virtual environment:

```powershell
py -3.10 -m venv .venv310
.venv310\Scripts\activate
```

Install required packages:

```powershell
pip install pymodbus ollama
```

Install the Ollama model:

```powershell
ollama pull llama3.2:1b
```

Check that Ollama works:

```powershell
ollama list
```

---

## Running the Normal Demo

Start the crane simulation first.

Then run:

```powershell
python main.py
```

Example input:

```text
Produce 1 type1 part and 1 type2 part
```

This demo shows:

- LLM order planning
- Type 1 production
- Type 2 production
- Agent negotiation
- Modbus crane control
- Normal production flow

---

## Running the Failure Demo

Run:

```powershell
python main_failure.py
```

Recommended input:

```text
Produce 1 type1 part
```

This demo shows:

- Process1 failure
- CFP negotiation
- ProcessBackup proposal
- PartAgent selecting the backup process
- Continued production after failure

---

## Example Normal Output

```text
[Part 1] CFP for Process1
[Process1] PROPOSE to Part 1 for Process1, cost=1
[ProcessBackup] PROPOSE to Part 1 for Process1, cost=5
[Part 1] Choosing Process1
[Process1] ACCEPTED Part 1
[Crane] Transporting Part 1 from Source1 to Process1
[Process1] Processing Part 1
[Process1] Finished Part 1
[Crane] Transporting Part 1 from Process1 to Sink
[Part 1] Completed at Sink
```

---

## Example Failure Output

```text
[Process1] FAILED
[Part 1] CFP for Process1
[Process1] Cannot propose for Part 1, failed
[ProcessBackup] PROPOSE to Part 1 for Process1, cost=5
[Part 1] Choosing ProcessBackup
[ProcessBackup] ACCEPTED Part 1
[Crane] Transporting Part 1 from Source1 to ProcessBackup
[ProcessBackup] Processing Part 1
[ProcessBackup] Finished Part 1
[Crane] Transporting Part 1 from ProcessBackup to Sink
[Part 1] Completed at Sink
```

---

## Notes

This project uses an AgentPy-inspired architecture, but it does not depend on the official `agentpy` package.  
The implementation uses a custom step-based MAS model with message queues and agent decision logic.

The LLM planner is used for high-level order intake only.  
The actual execution is deterministic and handled by the Python agents.

For the failure demo, ProcessBackup is represented by the same physical station as Process2 in the simulator.

---

## Author

Mostafa Aldiab  
Master's Programme in AI and Automation  
University West
