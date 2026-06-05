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
