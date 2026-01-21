# Chat2Graph

Extract clinical knowledge graphs from mental health conversations using LLMs.

## Core Concept

**Problem:** Clinical interviews contain valuable diagnostic information buried in unstructured text.

**Solution:** Extract two types of entities and measure their ratio:

| Entity Type | Examples |
|-------------|----------|
| **Clinical** | symptoms, DSM criteria, treatments, triggers |
| **Semantic** | people, places, objects, topics |

The **clinical ratio** (clinical entities / total entities) reveals whether speech contains clinical content — useful for distinguishing coherent symptom descriptions from incoherent speech patterns.

---

## Setup

### Prerequisites

- Python 3.10+
- Docker (for Neo4j)
- Ollama (for local LLM)

### Installation

```bash
git clone https://github.com/povilaskarvelis/chat2graph.git
cd chat2graph

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start Services

```bash
# Neo4j (graph database)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest

# Ollama (local LLM)
ollama serve
ollama pull llama3.1:8b
```

### Configure

Create `.env`:

```bash
OLLAMA_MODEL=llama3.1:8b
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

---

## Usage

### Extract Entities

```bash
# List available conversations
python extract_clinical.py

# Extract from one conversation
python extract_clinical.py gad_sarah_001

# Extract from all conversations
python extract_clinical.py all
```

### Analyze Patterns

```bash
python analyze_graphs.py
```

### Visualize in Neo4j

Open http://localhost:7474 and run:

```cypher
MATCH (n)-[r]->(m) RETURN n, r, m
```

---

## How It Works

```
1. INPUT: Clinical interview transcript
   ┌─────────────────────────────────────────────┐
   │ "I've been feeling anxious for 6 months..." │
   └──────────────────────┬──────────────────────┘
                          │
2. LLM EXTRACTION         ▼
   ┌─────────────────────────────────────────────┐
   │ Clinical: anxiety, worry, fatigue, 6 months │
   │ Semantic: Sarah, Dr. Grande, school         │
   │ Relationships: Sarah --HAS_SYMPTOM--> anxiety│
   └──────────────────────┬──────────────────────┘
                          │
3. ENTITY RESOLUTION      ▼
   ┌─────────────────────────────────────────────┐
   │ Merge similar entities using embeddings     │
   │ "anxiety" + "Anxiety" → "anxiety"           │
   └──────────────────────┬──────────────────────┘
                          │
4. STORE IN NEO4J         ▼
   ┌─────────────────────────────────────────────┐
   │ (:Episode)-[:MENTIONS]->(:Clinical)         │
   │ (:Episode)-[:MENTIONS]->(:Semantic)         │
   └──────────────────────┬──────────────────────┘
                          │
5. ANALYZE                ▼
   ┌─────────────────────────────────────────────┐
   │ Clinical Ratio = clinical / total entities  │
   │ Density metrics by entity type              │
   └─────────────────────────────────────────────┘
```

---

## Example Results

Using clinical interview transcripts from Dr. Todd Grande's educational videos (actors portraying scripted scenarios):

| Disorder | Clinical Entities | Semantic Entities | Clinical Ratio |
|----------|------------------|-------------------|----------------|
| GAD | 11.3 | 4.7 | **70.8%** |
| ADHD | 10.7 | 5.3 | **66.7%** |
| Wernicke's Aphasia | 2.0 | 5.0 | **28.6%** |

**Key Finding:** Wernicke's Aphasia shows low clinical ratio because the incoherent speech lacks symptom descriptions. GAD and ADHD show high ratios because patients actively describe symptoms.

### Example Entities by Disorder

**GAD (coherent, symptom-focused):**
- Clinical: anxiety, worry, fatigue, sleep problems, muscle tension
- Semantic: school, family, education

**Wernicke's Aphasia (incoherent, random topics):**
- Clinical: anxiety, worry (only 2)
- Semantic: golf, iPad, world (random, disconnected)

---

## Project Files

| File | Purpose |
|------|---------|
| `extract_clinical.py` | LLM extraction with entity resolution |
| `analyze_graphs.py` | Compute metrics by disorder |
| `empirical_conversations.py` | Example clinical transcripts |

---

## Architecture

| Component | Role |
|-----------|------|
| **Ollama** | Local LLM for entity extraction |
| **Neo4j** | Graph storage |
| **sentence-transformers** | Embeddings for entity resolution |

### Entity Resolution

Similar entities are merged using embedding similarity (threshold: 0.85):

```
Before: "anxiety", "Anxiety", "anxious"
After:  "anxiety" (merged)
```

---

## Cypher Queries

```cypher
-- View full graph
MATCH (n)-[r]->(m) RETURN n, r, m

-- View one conversation
MATCH (e:Episode {name: 'gad_sarah_001'})-[:MENTIONS]->(n)
RETURN e, n

-- Count by entity type
MATCH (e:Episode)-[:MENTIONS]->(n)
RETURN e.name, 
       sum(CASE WHEN n:Clinical THEN 1 ELSE 0 END) as clinical,
       sum(CASE WHEN n:Semantic THEN 1 ELSE 0 END) as semantic

-- Compare disorders
MATCH (e:Episode)-[:MENTIONS]->(n)
WHERE e.name IN ['gad_sarah_001', 'wernickes_aphasia_byron_001']
RETURN e, n
```

---

## Troubleshooting

```bash
# Neo4j not running
docker start neo4j

# Clear database and re-extract
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
with driver.session() as s: s.run('MATCH (n) DETACH DELETE n')
driver.close()
"
python extract_clinical.py all
```

---

## Limitations

- Entity extraction depends on LLM quality (currently llama3.1:8b)
- No validation against DSM criteria
- Entity resolution is within-conversation only
- Example dataset is small (n=7)

---

## License

Research and development tool. Example data from educational demonstrations with actors.
