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
[Sarah] --attended--> [Seattle Conference]
```

---

## Prerequisites

Before starting, you'll need:

- **Python 3.10+** - Check with `python3 --version`
- **Docker** - For running Neo4j locally ([Install Docker](https://docs.docker.com/get-docker/))
- **An LLM provider** (choose one):
  - **Ollama** (free, runs locally) - [Install Ollama](https://ollama.ai)
  - **Groq** (free tier, cloud) - [Get API key](https://console.groq.com)
  - **OpenAI** (paid, cloud) - [Get API key](https://platform.openai.com/api-keys)

---

## Quick Start

### Step 1: Clone and Setup Python Environment

```bash
# Clone the repository
git clone https://github.com/povilaskarvelis/chat2graph.git
cd chat2graph

# Create Python virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install graphiti-core python-dotenv fastapi uvicorn
```

### Step 2: Start Neo4j Database

**Option A: Docker (Recommended)**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

**Option B: Neo4j Aura (Free Cloud)**
1. Go to https://neo4j.com/cloud/aura-free/
2. Create a free account and instance
3. Save your connection URI, username, and password

### Step 3: Setup Your LLM Provider

Choose **one** of these options:

#### Option A: Ollama (Free, Local, Private)

```bash
# Install Ollama (Mac)
brew install ollama

# Start Ollama
ollama serve

# Download required models (in a new terminal)
ollama pull llama3.2
ollama pull nomic-embed-text
```

#### Option B: Groq (Free Tier, Fast)

1. Go to https://console.groq.com
2. Create account and get API key
3. You'll add this to `.env` in the next step

#### Option C: OpenAI (Paid)

1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. You'll add this to `.env` in the next step

### Step 4: Configure Environment

Create a `.env` file in the project root:

```bash
# For Ollama (local, free):
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OPENAI_API_KEY=dummy

# For Groq (cloud, free tier):
# LLM_PROVIDER=groq
# GROQ_API_KEY=your-groq-api-key-here
# GROQ_MODEL=llama-3.1-8b-instant
# OPENAI_API_KEY=dummy

# For OpenAI (cloud, paid):
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your-openai-api-key-here
# OPENAI_MODEL=gpt-4o-mini

# Neo4j Database (Docker defaults)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

### Step 5: Run the Demo

```bash
# Make sure venv is activated
source venv/bin/activate

# Run the demo script
python main.py
```

You should see output like:
```
🚀 Chat2Graph Starting...
🧠 Setting up AI models...
📡 Connecting to Neo4j...
📝 Processing conversation...
✅ Conversation processed and added to graph!
```

### Step 6: View Your Knowledge Graph

1. Open **http://localhost:7474** in your browser
2. Login with `neo4j` / `password123`
3. Run this query to see your graph:

```cypher
MATCH (n)-[r]->(m) RETURN n, r, m
```

4. Click and drag nodes to explore the relationships!

---

## Using the API Server

For automated processing, start the API server:

```bash
python api_server.py
```

This provides REST endpoints at **http://localhost:8080**:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/add_conversation` | POST | Add a conversation to the graph |
| `/query` | POST | Query the knowledge graph |
| `/stats` | GET | Get graph statistics |

### Example: Add a Conversation

```bash
curl -X POST http://localhost:8080/add_conversation \
  -H "Content-Type: application/json" \
  -d '{
    "name": "meeting_notes",
    "content": "John mentioned that Lisa just joined Google as a PM.",
    "source_description": "Team meeting"
  }'
```

### Example: Query the Graph

```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who works at Google?"}'
```

---

## Project Structure

```
chat2graph/
├── main.py                 # Demo script - processes a sample conversation
├── api_server.py           # REST API for automated processing
├── quick_test.py           # Fast single-conversation test
├── load_conversations.py   # Bulk conversation loader
├── sample_conversations.py # Sample conversation data
├── n8n_workflow.json       # Import this into n8n for automation
├── .env                    # Your configuration (don't commit!)
├── .env.example            # Template for .env
├── venv/                   # Python virtual environment
└── README.md               # This file
```

---

## How It Works

```
┌─────────────────────┐
│   Conversation      │  "Alice met Sarah from Acme Corp..."
│      Text           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   LLM (AI Model)    │  Extracts entities & relationships
│  Ollama/Groq/OpenAI │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Graphiti        │  Structures data, manages graph
│   (Python Library)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Neo4j          │  Stores nodes, edges, properties
│  (Graph Database)   │  Enables visual exploration
└─────────────────────┘
```

**Key Components:**
- **Graphiti** - Python library that orchestrates LLM calls and graph operations
- **Neo4j** - Graph database for storing and querying the knowledge graph
- **LLM** - AI model that understands text and extracts structured information

---

## Useful Neo4j Queries

```cypher
-- See everything
MATCH (n)-[r]->(m) RETURN n, r, m

-- Count all entities
MATCH (n:Entity) RETURN count(n)

-- Find all people
MATCH (n:Entity) WHERE n.entity_type = 'person' RETURN n

-- Find all companies
MATCH (n:Entity) WHERE n.entity_type = 'organization' RETURN n

-- Find who works where
MATCH (p)-[r:RELATES_TO]->(c) 
WHERE r.fact CONTAINS 'works' 
RETURN p, r, c

-- Search for a specific person
MATCH (n) WHERE n.name CONTAINS 'Sarah' RETURN n

-- Find connections between two entities
MATCH path = (a)-[*1..3]-(b) 
WHERE a.name CONTAINS 'Sarah' AND b.name CONTAINS 'Acme'
RETURN path

-- Delete everything (reset the graph)
MATCH (n) DETACH DELETE n
```

---

## Troubleshooting

### "Connection refused" to Neo4j
- Make sure Docker is running: `docker ps`
- Check if Neo4j container exists: `docker ps -a`
- Restart it: `docker start neo4j`

### "Model not found" with Ollama
- Pull the model: `ollama pull llama3.2`
- Make sure Ollama is running: `ollama serve`

### Slow processing with Ollama
- This is normal! Local models are slower than cloud APIs
- Use `quick_test.py` for faster testing
- Consider using Groq (free, fast cloud API)

### API key errors
- Double-check your `.env` file
- Make sure there are no spaces around the `=` sign
- For Ollama, you still need `OPENAI_API_KEY=dummy` in `.env`

---

## n8n Integration (Optional)

To automate conversation ingestion:

1. Install n8n: `npx n8n`
2. Open http://localhost:5678
3. Import `n8n_workflow.json`
4. Configure webhooks to receive conversations from Slack, Discord, etc.

---

## Resources

- [Graphiti Documentation](https://github.com/getzep/graphiti)
- [Neo4j Cypher Query Language](https://neo4j.com/docs/cypher-manual/)
- [Ollama Models](https://ollama.ai/library)
- [Groq Console](https://console.groq.com)
- [n8n Workflow Automation](https://n8n.io/)

---

## License

MIT
