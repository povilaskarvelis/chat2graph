# Chat2Graph 🧠➡️🕸️

A tool for analyzing clinical conversations using knowledge graphs. Extracts clinical and semantic entities from mental health interviews to identify patterns that differentiate disorders.

## Purpose

This project extracts structured knowledge graphs from clinical conversations to answer:

**Can graph structure help identify mental health disorders?**

By extracting two types of entities:
- **Clinical entities:** symptoms, DSM criteria, treatments, triggers
- **Semantic entities:** people, places, objects, topics

We can compute metrics that differentiate disorders:

| Disorder | Clinical Nodes | Semantic Nodes | Clinical Ratio |
|----------|---------------|----------------|----------------|
| GAD | 11.3 | 5.0 | **69.4%** |
| ADHD | 8.7 | 4.0 | **68.4%** |
| Wernicke's Aphasia | 2.0 | 5.0 | **28.6%** |

**Key finding:** Wernicke's Aphasia shows low clinical ratio and zero internal density because the speech is incoherent and lacks symptom descriptions.

---

## Quick Start

```bash
# 1. Make sure Neo4j and Ollama are running
docker start neo4j
ollama serve

# 2. Activate environment
source venv/bin/activate

# 3. Extract entities from clinical interviews
python extract_clinical.py all

# 4. Analyze graph patterns by disorder
python analyze_graphs.py

# 5. Visualize in Neo4j Browser
open http://localhost:7474
# Run: MATCH (n)-[r]->(m) RETURN n, r, m
```

---

## How It Works

```
STEP 1: Clinical interview transcript
┌─────────────────────────────────────────────────────────────┐
│  "I've been feeling anxious for about 6 months now.         │
│   It started after I lost my job. I worry constantly..."    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
STEP 2: LLM extracts clinical + semantic entities
┌─────────────────────────────────────────────────────────────┐
│  CLINICAL ENTITIES:                                         │
│   • anxiety (symptom)                                       │
│   • worry (symptom)                                         │
│   • 6 months (criterion - duration)                         │
│   • job loss (trigger)                                      │
│                                                             │
│  SEMANTIC ENTITIES:                                         │
│   • Sarah (person)                                          │
│   • Dr. Grande (person)                                     │
│   • work (place)                                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
STEP 3: Store in Neo4j with entity type labels
┌─────────────────────────────────────────────────────────────┐
│  (:Episode {name: 'gad_sarah_001'})                         │
│       │                                                     │
│       ├──MENTIONS──>(:Clinical {name: 'anxiety'})           │
│       ├──MENTIONS──>(:Clinical {name: 'worry'})             │
│       ├──MENTIONS──>(:Semantic {name: 'Sarah'})             │
│       └──MENTIONS──>(:Semantic {name: 'Dr. Grande'})        │
│                                                             │
│  (Sarah)──HAS_SYMPTOM──>(anxiety)                           │
│  (job loss)──TRIGGERS──>(anxiety)                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
STEP 4: Analyze patterns by disorder
┌─────────────────────────────────────────────────────────────┐
│  Clinical Ratio = clinical / (clinical + semantic)          │
│                                                             │
│  GAD:        69.4%  (many symptoms described)               │
│  ADHD:       68.4%  (many symptoms described)               │
│  Wernicke's: 28.6%  (incoherent, few symptoms)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

| Component | Purpose | How to Run |
|-----------|---------|------------|
| **Ollama** | Local LLM for entity extraction | `ollama serve` |
| **Neo4j** | Graph database for storage | `docker start neo4j` |
| **extract_clinical.py** | Extract entities from transcripts | `python extract_clinical.py` |
| **analyze_graphs.py** | Compare patterns by disorder | `python analyze_graphs.py` |

### Entity Types

**Clinical Entities** (mental health specific):
- Symptoms: anxiety, worry, fatigue, sleep problems, attention issues
- DSM Criteria: duration ("6 months"), frequency ("more days than not")
- Treatments: medications, therapy types, coping strategies
- Triggers: life events, stressors

**Semantic Entities** (general concepts):
- People: patient, clinician, family members
- Places: school, work, home, clinic
- Objects: physical items mentioned
- Topics: abstract concepts discussed

---

## Setup Guide

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **Python 3.10+** | Runtime | `python3 --version` |
| **Docker** | Runs Neo4j | [Install Docker](https://docs.docker.com/get-docker/) |
| **Ollama** | Local LLM | [Install Ollama](https://ollama.ai) |

### Step 1: Clone and Setup

```bash
git clone https://github.com/povilaskarvelis/chat2graph.git
cd chat2graph

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Neo4j

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

### Step 3: Start Ollama

```bash
ollama serve
ollama pull llama3.1:8b  # Or llama3.2
```

### Step 4: Configure

Create `.env` file:

```bash
# Ollama
OLLAMA_MODEL=llama3.1:8b

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

### Step 5: Run Extraction

```bash
# Extract from all conversations
python extract_clinical.py all

# Or extract one at a time
python extract_clinical.py gad_sarah_001
```

### Step 6: Analyze

```bash
python analyze_graphs.py
```

### Step 7: Visualize

Open http://localhost:7474 and run:

```cypher
MATCH (n)-[r]->(m) RETURN n, r, m
```

---

## Analysis Output

Running `python analyze_graphs.py` produces:

```
===========================================================================
  CLINICAL KNOWLEDGE GRAPH ANALYSIS
  Comparing Clinical vs Semantic Entities by Disorder
===========================================================================

NODE COUNTS:
                        Clinical   Semantic   Clinical Ratio
                        Nodes      Nodes      (higher = more clinical)
  -------------------------------------------------------------
  GAD                    11.3        5.0        69.4%
  ADHD                    8.7        4.0        68.4%
  Wernicke's Aphasia      2.0        5.0        28.6%

DENSITY BY CONNECTION TYPE:
                        Clinical   Semantic   Cross-type
                        Density    Density    Density
  -------------------------------------------------------------
  GAD                   0.000      0.083        0.042
  ADHD                  0.003      0.044        0.028
  Wernicke's Aphasia    0.000      0.050        0.100
```

**Interpretation:**
- **High clinical ratio** = patient describing clear symptoms (GAD, ADHD)
- **Low clinical ratio** = speech without clinical content (Wernicke's)
- **Zero density** = disconnected entities (incoherent speech)

---

## Clinical Interview Data

The `empirical_conversations.py` file contains transcripts from Dr. Todd Grande's educational videos.

**Note:** The "patients" are actors portraying scripted scenarios — NOT real patients.

| Conversation | Condition | Meets Criteria? |
|--------------|-----------|-----------------|
| `gad_sarah_001` | GAD | Yes |
| `gad_sarah_002` | GAD (comorbidities) | Yes |
| `gad_sarah_003` | GAD (subthreshold) | No |
| `adhd_elise_001` | ADHD | No |
| `adhd_elise_002` | ADHD Combined | Yes |
| `adhd_elise_003` | ADHD | Yes |
| `wernickes_aphasia_byron_001` | Wernicke's Aphasia | Yes |

---

## Project Files

| File | Purpose | How to Run |
|------|---------|------------|
| `extract_clinical.py` | **Extract entities from transcripts** | `python extract_clinical.py all` |
| `analyze_graphs.py` | **Compare graph patterns by disorder** | `python analyze_graphs.py` |
| `chat.py` | Query the graph with natural language | `python chat.py` |
| `empirical_conversations.py` | Clinical interview data | — |
| `sample_conversations.py` | Synthetic sample data | — |

---

## Cypher Queries

View full graph:
```cypher
MATCH (n)-[r]->(m) RETURN n, r, m
```

View one conversation:
```cypher
MATCH (e:Episode {name: 'gad_sarah_001'})-[:MENTIONS]->(n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN e, n, r, m
```

View only clinical entities:
```cypher
MATCH (e:Episode)-[:MENTIONS]->(n:Clinical)
RETURN e, n
```

Compare Wernicke's vs GAD:
```cypher
MATCH (e:Episode)-[:MENTIONS]->(n)
WHERE e.name IN ['gad_sarah_001', 'wernickes_aphasia_byron_001']
OPTIONAL MATCH (n)-[r]->(m)
RETURN e, n, r, m
```

Count by entity type:
```cypher
MATCH (e:Episode)-[:MENTIONS]->(n)
RETURN e.name, 
       sum(CASE WHEN n:Clinical THEN 1 ELSE 0 END) as clinical,
       sum(CASE WHEN n:Semantic THEN 1 ELSE 0 END) as semantic
```

---

## Troubleshooting

### Neo4j won't connect
```bash
docker ps          # Check if running
docker start neo4j # Start if stopped
```

### Ollama errors
```bash
ollama serve       # Make sure it's running
ollama list        # Check available models
```

### Clear and re-extract
```bash
# Clear database
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
with driver.session() as s: s.run('MATCH (n) DETACH DELETE n')
driver.close()
print('Cleared!')
"

# Re-extract
python extract_clinical.py all
```

---

## Disclaimer

This is a research and development tool. Clinical interview data is from educational demonstrations with actors, not real patients. Any clinical application would require appropriate validation, privacy safeguards, and regulatory compliance.
