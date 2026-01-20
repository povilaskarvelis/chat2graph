# Chat2Graph 🧠➡️🕸️

A foundation for building mental health applications using knowledge graphs. Extract clinical entities, relationships, and patterns from conversations to enable diagnostics, monitoring, and care coordination tools.

## Purpose

This project provides the infrastructure for converting unstructured mental health conversations (clinical notes, therapy sessions, care coordination) into structured knowledge graphs that can power:

- **Diagnostic support tools** — Track symptoms, their patterns, and relationships over time
- **Care coordination systems** — Map patient support networks and provider relationships  
- **Treatment monitoring** — Link treatments to outcomes and identify what works
- **Research applications** — Aggregate patterns across anonymized clinical data

## What It Does

Takes clinical conversation text like:
> "Patient reports increased anxiety since job loss in March. Currently on sertraline prescribed by Dr. Wilson. Sister Emma and partner Michael provide primary support."

And creates a queryable knowledge graph:
```
[Patient] --has_symptom--> [Anxiety]
[Anxiety] --triggered_by--> [Job Loss]
[Job Loss] --occurred--> [March]
[Patient] --takes_medication--> [Sertraline]
[Dr. Wilson] --prescribed--> [Sertraline]
[Emma] --supports--> [Patient]
[Michael] --supports--> [Patient]
```

You can then query: *"What support systems does this patient have?"* or *"What triggered the anxiety symptoms?"*

---

## Extracted Entity Types

| Category | Examples |
|----------|----------|
| **People** | Patients, clinicians, therapists, family members, support network |
| **Symptoms** | Anxiety, depression, sleep disturbance, social withdrawal |
| **Treatments** | Medications (sertraline, bupropion), therapy approaches (CBT) |
| **Organizations** | Healthcare facilities, support services, employers |
| **Temporal** | Symptom onset, treatment duration, episode history |
| **Relationships** | Who treats whom, who supports whom, what treats what |

---

## Key Technologies

This project combines several tools. Here's what each does:

### Graphiti
**What:** A Python library that orchestrates the conversion of text into knowledge graphs.

**Role:** Graphiti takes your conversation text, sends it to an LLM (like Ollama) to extract entities and relationships, then stores the structured data in Neo4j. It handles the complexity of:
- Prompting the LLM to identify entities (people, symptoms, treatments)
- Extracting relationships between entities
- Managing temporal information (when things happened)
- Deduplicating entities across multiple conversations

**Install:** `pip install graphiti-core` (included in requirements.txt)

**Not Docker:** Graphiti is a Python library that runs in your Python environment.

---

### Neo4j
**What:** A graph database optimized for storing and querying connected data.

**Role:** Neo4j stores the knowledge graph — all the entities (nodes) and relationships (edges) extracted from conversations. Unlike traditional databases that store data in tables, Neo4j stores data as a network of connections, making it ideal for questions like "Who is connected to whom?" or "What path connects symptom X to treatment Y?"

**Key features:**
- Visual graph exploration in the browser
- Powerful query language (Cypher)
- Handles complex relationship traversals efficiently

**Install:** We run Neo4j in Docker for convenience, but you could also:
- Install it natively: https://neo4j.com/download/
- Use Neo4j Aura (free cloud): https://neo4j.com/cloud/aura-free/

**Docker is optional:** Docker just makes it easier to run Neo4j without installing it system-wide.

---

### Cypher
**What:** Neo4j's query language for graph databases.

**Role:** Cypher lets you ask questions about your knowledge graph. It's designed to look like the patterns you're searching for:

```cypher
-- "Find everyone who supports the patient"
MATCH (supporter)-[:SUPPORTS]->(patient)
RETURN supporter.name

-- "What symptoms are linked to what triggers?"
MATCH (trigger)-[:TRIGGERED]->(symptom)
RETURN trigger.name, symptom.name
```

The syntax mirrors graph patterns:
- `(node)` — a circle/entity
- `-[relationship]->` — an arrow/connection
- `MATCH` — find this pattern
- `RETURN` — show me these parts

**Not installed separately:** Cypher comes built into Neo4j.

---

### Ollama
**What:** A tool for running large language models (LLMs) locally on your computer.

**Role:** Ollama runs the AI models that understand your text and extract entities. When Graphiti needs to identify "Dr. Wilson prescribed sertraline," it sends the text to Ollama, which uses models like Llama 3.2 to understand and extract that information.

**Why local?** 
- Free (no API costs)
- Private (data stays on your machine)
- Works offline

**Install:** Native app from https://ollama.ai (or `brew install ollama` on Mac)

**Not Docker:** Ollama runs as a native application for better GPU access.

---

### How They Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                        │
│                     (Python scripts)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                       Graphiti                               │
│              (Python library - pip install)                  │
│                                                              │
│  • Receives conversation text                                │
│  • Sends to LLM for entity extraction                        │
│  • Structures the extracted data                             │
│  • Stores in Neo4j                                           │
└──────────┬─────────────────────────────────┬────────────────┘
           │                                 │
           ▼                                 ▼
┌─────────────────────┐         ┌─────────────────────────────┐
│       Ollama        │         │          Neo4j              │
│   (native app)      │         │    (Docker container)       │
│                     │         │                             │
│ • Runs LLM locally  │         │ • Stores nodes & edges      │
│ • Extracts entities │         │ • Answers Cypher queries    │
│ • Creates embeddings│         │ • Visual graph browser      │
└─────────────────────┘         └─────────────────────────────┘
```

---

## Setup Guide

### Prerequisites

| Tool | What It Is | Install |
|------|------------|---------|
| **Python 3.10+** | Programming language runtime | Check: `python3 --version` |
| **Docker** | Containerization (runs Neo4j) | [Install Docker](https://docs.docker.com/get-docker/) |
| **Ollama** | Local AI model runner | [Install Ollama](https://ollama.ai) |

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/povilaskarvelis/chat2graph.git
cd chat2graph
```

### Step 2: Set Up Python Environment

This installs Graphiti and other Python dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install Graphiti and dependencies
pip install -r requirements.txt
```

### Step 3: Start Neo4j (Graph Database)

Neo4j stores the knowledge graph. The easiest way to run it is with Docker:

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

- Port `7474` — Web browser interface
- Port `7687` — Database connection (Bolt protocol)

Wait ~30 seconds, then verify: `docker ps`

### Step 4: Start Ollama (Local AI)

Ollama runs the AI models that extract entities from text:

```bash
# Start Ollama (runs in background)
ollama serve
```

In a **new terminal**, download the required models:
```bash
ollama pull llama3.2           # Language model for understanding text (~2GB)
ollama pull nomic-embed-text   # Embedding model for similarity search (~300MB)
```

### Step 5: Create Configuration

Create a `.env` file in the project root:

```bash
# AI Model (Ollama - local, free)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Required placeholder
OPENAI_API_KEY=dummy
```

### Step 6: Run the Demo

```bash
source venv/bin/activate
python main.py
```

### Step 7: View the Knowledge Graph

1. Open **http://localhost:7474** in your browser
2. Login: `neo4j` / `password123`
3. Run this Cypher query to see your graph:
   ```cypher
   MATCH (n)-[r]->(m) RETURN n, r, m
   ```

---

## Sample Data

The `sample_conversations.py` file contains synthetic mental health conversations:

| Conversation | Type |
|--------------|------|
| `intake_assessment_001` | Clinical intake with symptom history |
| `care_coordination_002` | Multidisciplinary team meeting |
| `therapy_session_015` | CBT session notes |
| `support_group_session` | Facilitated group discussion |
| `treatment_planning_review` | Quarterly progress review |

**Note:** All sample data is entirely fictional and created for testing purposes.

---

## Project Files

| File | Purpose |
|------|---------|
| `main.py` | Demo script with sample conversation |
| `sample_conversations.py` | Synthetic mental health conversations |
| `api_server.py` | REST API for programmatic access |
| `quick_test.py` | Fast single-conversation test |
| `load_conversations.py` | Bulk conversation loader |

---

## Using the API

For integration with other systems:

```bash
python api_server.py
```

Endpoints at **http://localhost:8080**:

```bash
# Add clinical notes
curl -X POST http://localhost:8080/add_conversation \
  -H "Content-Type: application/json" \
  -d '{
    "name": "session_042",
    "content": "Patient reports improved sleep after starting melatonin...",
    "source_description": "Therapy session notes"
  }'

# Query the graph
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What treatments has this patient tried?"}'
```

---

## Example Cypher Queries

```cypher
-- Find all symptoms mentioned
MATCH (n:Entity) WHERE n.entity_type = 'symptom' RETURN n

-- Find patient support networks
MATCH (supporter)-[r]->(patient)
WHERE r.fact CONTAINS 'support'
RETURN supporter, r, patient

-- Find medication relationships
MATCH (provider)-[r]->(medication)
WHERE r.fact CONTAINS 'prescribed'
RETURN provider.name, medication.name

-- Track symptom triggers
MATCH (trigger)-[r]->(symptom)
WHERE r.fact CONTAINS 'trigger'
RETURN trigger, symptom

-- See all entities and relationships
MATCH (n)-[r]->(m) RETURN n, r, m
```

---

## Future Development

This infrastructure can support:

- [ ] Symptom trajectory visualization
- [ ] Treatment outcome analysis
- [ ] Care team network mapping
- [ ] Risk factor identification
- [ ] Natural language clinical queries
- [ ] Integration with EHR systems
- [ ] Anonymized research data aggregation

---

## Troubleshooting

### Neo4j won't connect
```bash
docker ps          # Check if running
docker start neo4j # Start if stopped
```

### Ollama model not found
```bash
ollama serve                    # Make sure it's running
ollama pull llama3.2           # Pull models
ollama pull nomic-embed-text
```

### Processing is slow
Local AI takes 1-2 minutes per conversation. For faster processing, see alternatives below.

---

## Alternative Configurations

### Groq (Free, Fast Cloud AI)
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

### OpenAI (Paid, Highest Quality)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Neo4j Aura (Free Cloud Database)
Use connection details from https://neo4j.com/cloud/aura-free/

---

## Resources

- [Graphiti Documentation](https://github.com/getzep/graphiti)
- [Neo4j Cypher Query Language](https://neo4j.com/docs/cypher-manual/)
- [Ollama Models](https://ollama.ai/library)

---

## Disclaimer

This is a research and development tool. Sample conversations are entirely synthetic. Any clinical application would require appropriate validation, privacy safeguards, and regulatory compliance.

## License

MIT
