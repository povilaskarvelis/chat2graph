# Chat2Graph 🧠➡️🕸️

Convert conversations into a knowledge graph using AI. Extract people, companies, relationships, and facts from text and visualize them as an interactive graph.

## What This Does

Takes raw conversation text like:
> "I met Sarah from Acme Corp at the Seattle conference. She's their VP of Engineering and mentioned their CEO John is leading their expansion to Europe."

And creates a queryable knowledge graph:
```
[Sarah] --works_at--> [Acme Corp]
[Sarah] --has_role--> [VP of Engineering]
[John] --is_ceo_of--> [Acme Corp]
[Acme Corp] --expanding_to--> [Europe]
```

You can then query the graph with natural language: *"Who works at Acme Corp?"* → Returns Sarah and John.

---

## Setup Guide

This guide uses **Ollama** (free, local AI) and **Docker** (for the Neo4j database). These run entirely on your machine — no API keys or cloud services needed.

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **Python 3.10+** | Runtime | Check: `python3 --version` |
| **Docker** | Runs the Neo4j database | [Install Docker](https://docs.docker.com/get-docker/) |
| **Ollama** | Runs AI models locally | [Install Ollama](https://ollama.ai) |

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/povilaskarvelis/chat2graph.git
cd chat2graph
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start Neo4j (Graph Database)

Neo4j stores the knowledge graph. Run it with Docker:

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

Wait ~30 seconds for it to start. You can check it's running:
```bash
docker ps  # Should show "neo4j" container
```

### Step 4: Start Ollama (Local AI)

Ollama runs the AI models that extract entities from text.

```bash
# Start Ollama (runs in background)
ollama serve
```

In a **new terminal**, download the required models:
```bash
ollama pull llama3.2           # Language model (~2GB)
ollama pull nomic-embed-text   # Embedding model (~300MB)
```

### Step 5: Create Configuration File

Create a file called `.env` in the project folder:

```bash
# .env file contents:

# AI Model (Ollama - local, free)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Required placeholder (don't change)
OPENAI_API_KEY=dummy
```

### Step 6: Run the Demo

```bash
# Make sure venv is activated
source venv/bin/activate

# Run it!
python main.py
```

You should see:
```
🚀 Chat2Graph Starting...
🧠 Setting up AI models...
   🤖 Using Ollama (local, free)
📡 Connecting to Neo4j...
   ✅ Connected
📝 Processing conversation...
   (This takes 1-2 minutes with local AI)
✅ Conversation processed and added to graph!
```

### Step 7: View Your Knowledge Graph

1. Open **http://localhost:7474** in your browser
2. Connect with:
   - Username: `neo4j`
   - Password: `password123`
3. Run this query to see your graph:
   ```
   MATCH (n)-[r]->(m) RETURN n, r, m
   ```
4. You'll see an interactive visualization — drag nodes around to explore!

---

## Understanding the Graph

When you run the query `MATCH (n)-[r]->(m) RETURN n, r, m`:

| Part | Meaning |
|------|---------|
| `MATCH` | "Find..." |
| `(n)` | Any node (entity) |
| `-[r]->` | Connected by a relationship |
| `(m)` | To another node |
| `RETURN` | Show me the results |

**In plain English:** *"Find everything connected to something else."*

### More Useful Queries

```cypher
-- See all entities
MATCH (n:Entity) RETURN n

-- Find a specific person
MATCH (n) WHERE n.name CONTAINS 'Sarah' RETURN n

-- See all relationships
MATCH (n)-[r]->(m) RETURN n.name, type(r), m.name

-- Reset the graph (delete everything)
MATCH (n) DETACH DELETE n
```

---

## Project Files

| File | What It Does |
|------|--------------|
| `main.py` | Demo script — processes a sample conversation |
| `quick_test.py` | Faster test with a shorter conversation |
| `api_server.py` | REST API for adding conversations programmatically |
| `sample_conversations.py` | Example conversation data |
| `.env` | Your configuration (not committed to git) |

---

## Using the API

For programmatic access, start the API server:

```bash
python api_server.py
```

Then add conversations via HTTP:

```bash
# Add a conversation
curl -X POST http://localhost:8080/add_conversation \
  -H "Content-Type: application/json" \
  -d '{
    "name": "meeting_001",
    "content": "Tom said he just joined Microsoft as a designer.",
    "source_description": "Team standup"
  }'

# Query the graph
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who works at Microsoft?"}'

# Get statistics
curl http://localhost:8080/stats
```

---

## How It Works

```
┌─────────────────────┐
│   Conversation      │  "Alice met Bob at Google..."
│      Text           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Ollama         │  AI extracts: Alice, Bob, Google
│   (Local LLM)       │  and their relationships
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Graphiti        │  Python library that structures
│                     │  the data and manages the graph
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Neo4j          │  Stores everything as nodes
│  (Graph Database)   │  and edges for querying
└─────────────────────┘
```

---

## Troubleshooting

### Neo4j won't connect
```bash
# Check if container is running
docker ps

# If not running, start it
docker start neo4j

# If it doesn't exist, create it (Step 3)
```

### Ollama model not found
```bash
# Make sure Ollama is running
ollama serve

# Pull the models again
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Processing is slow
This is normal with local AI! Ollama on a laptop takes 1-2 minutes per conversation. For faster processing, see [Alternative: Use Groq](#alternative-use-groq-free-fast-cloud-ai) below.

### "OPENAI_API_KEY" error
Make sure your `.env` file has `OPENAI_API_KEY=dummy` — this is required even when using Ollama.

---

## Alternative Options

### Alternative: Use Groq (Free, Fast Cloud AI)

Groq offers a free tier that's much faster than local Ollama:

1. Get a free API key at https://console.groq.com
2. Update your `.env`:
   ```bash
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_your_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   OPENAI_API_KEY=dummy
   
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password123
   ```

### Alternative: Use OpenAI (Paid, Highest Quality)

For best accuracy, use OpenAI's models:

1. Get an API key at https://platform.openai.com/api-keys
2. Update your `.env`:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your_key_here
   OPENAI_MODEL=gpt-4o-mini
   
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password123
   ```

### Alternative: Use Neo4j Aura (Free Cloud Database)

Instead of Docker, use Neo4j's free cloud offering:

1. Create account at https://neo4j.com/cloud/aura-free/
2. Create a free instance
3. Update your `.env` with the connection details:
   ```bash
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_aura_password
   ```

---

## Resources

- [Graphiti Documentation](https://github.com/getzep/graphiti)
- [Neo4j Cypher Query Language](https://neo4j.com/docs/cypher-manual/)
- [Ollama Models](https://ollama.ai/library)

---

## License

MIT
