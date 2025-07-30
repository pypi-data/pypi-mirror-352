<p align="center">
  <img src="https://github.com/user-attachments/assets/9f95dfde-f258-4bdd-ac3a-23aad569d9c0" 
       alt="Group 14" 
       width="300" 
       style="padding: 10px; border-radius: 8px;"/>
</p>

# Muvius A2A Framework

The **Muvius A2A (Agent-to-Agent) Framework** is an open-source, modular system for building intelligent, role-driven, and memory-aware AI agents that can communicate with one another to accomplish complex marketplace tasks like negotiation, matchmaking, and fulfillment.

---

## Memory-Retaining Agents

Each Muvius agent has three layers of memory:
- **Procedural Memory**: Defines the agent’s role, goals, and policies.
- **Episodic Memory**: Logs of prior interactions and session context.
- **Semantic Memory**: A vectorized memory store for long-term understanding, reasoning, and context recall.

---

## Agent Retention Flow

1. **User Message** is received by an agent.
2. **System Prompt** is constructed using:
   - Procedural memory
   - Episodic enrichment (e.g., recent messages)
   - Semantic context from vector search
3. **Working Memory** is assembled into a structured prompt.
4. LLM inference generates a response.
5. Agent memory is **updated** with new episodic and semantic traces.
6. Agents can optionally **communicate with each other** using structured JSON messages.

---

## Architecture Overview

```text
┌──────────────────────────────┐
│         Orchestrator         │
│ Routes messages & manages    │
│ A2A communication flow       │
└────────────┬─────────────────┘
             │
     ┌───────▼────────┐       ┌───────────────┐
     │  Buyer Agent   │ <---> │ Seller Agent  │
     └──────┬─────────┘       └───────────────┘
            │
  ┌─────────▼────────────┐
  │ Working Memory Builder│
  └─────────┬────────────┘
            │
   ┌────────▼──────────┐
   │ Memory Manager     │
   │ - Procedural (YAML)│
   │ - Episodic (SQLite)│
   │ - Semantic (Qdrant)│
   └────────────────────┘
```

---

## Tech Stack (All Open Source)

| Layer              | Tool/Framework         |
|--------------------|------------------------|
| Vector Store       | Qdrant / Weaviate      |
| Embeddings         | Sentence-Transformers  |
| Local LLM          | Ollama / llama.cpp     |
| Memory DB          | SQLite / DuckDB        |
| Communication Bus  | JSON-RPC or Redis Pub/Sub |
| API Layer          | FastAPI (Python) or Echo/Fiber (Go) |
| Orchestration      | Docker Compose / Kubernetes |

---

## Agent Communication (A2A)

Agents communicate using structured JSON payloads:

```json
{
  "from_agent": "BuyerAgent",
  "to_agent": "SellerAgent",
  "intent": "propose_trade",
  "semantic_context": ["price", "location", "urgency"],
  "proposed_action": "counter_offer",
  "timestamp": "2025-06-02T14:00:00Z"
}
```

## Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/your-org/muvius-a2a-framework.git
cd muvius-a2a-framework
```

### 2. Start Agents Locally (with Docker Compose)

```bash
docker-compose up --build
```

### 3. Interact with Agents

Use the 
```bash
/interact
```
API for each agent:
```bash
POST /api/agent/buyer/interact
```
```json
{
  "user_id": "123",
  "message": "Is this scooter still available?"
}
```

## Directory Structure
```text
muvius/
├── orchestrator/        # Agent router & dispatcher
├── agents/
│   ├── buyer_agent/
│   │   ├── memory/       # procedural.yaml, episodic.db, embeddings/
│   │   └── main.py
│   └── seller_agent/
│       └── ...
├── shared/
│   └── memory_utils.py
├── embeddings/
│   └── models/
└── docker-compose.yml
```

## Testing and Extending
	- Add new roles by cloning an agent folder and modifying its procedural memory.
	- Create shared memory overlays for organizational agents.
	- Use pytest or go test for isolated unit testing.

⸻

## License
```text
MIT License. Fully open-source and extensible.
```

## Roadmap
	•	Multi-agent simulation testing suite
	•	Agent registry & directory service
	•	Multi-language agent support
	•	Shared semantic memory overlays

## Maintainers

Developed by the Muvio AI team
