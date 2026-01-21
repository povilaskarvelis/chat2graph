"""
Simple API server for Chat2Graph.

This server provides endpoints that n8n can call to:
1. Add new conversations to the knowledge graph
2. Query the knowledge graph
3. Get graph statistics

Run with: python api_server.py
Then n8n can call: http://localhost:8000/add_conversation
"""

import asyncio
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# FastAPI for the REST API
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "fastapi", "uvicorn"])
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn

load_dotenv()

# ============================================
# Pydantic models for API requests/responses
# ============================================

class ConversationInput(BaseModel):
    """Input for adding a conversation."""
    name: str
    content: str
    source_description: Optional[str] = "API submission"

class QueryInput(BaseModel):
    """Input for querying the graph."""
    query: str
    num_results: Optional[int] = 5

class CypherInput(BaseModel):
    """Input for executing a Cypher query."""
    cypher: str

class ConversationResponse(BaseModel):
    """Response after adding a conversation."""
    success: bool
    message: str
    name: str

class QueryResponse(BaseModel):
    """Response from a query."""
    query: str
    results: list

# ============================================
# Global Graphiti instance (initialized on startup)
# ============================================

graphiti = None

def get_graphiti():
    """Get or create the Graphiti instance."""
    global graphiti
    if graphiti is None:
        from graphiti_core import Graphiti
        from graphiti_core.llm_client import OpenAIClient
        from graphiti_core.llm_client.config import LLMConfig
        from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig
        
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
        llm_config = LLMConfig(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            model=model,
            small_model=model
        )
        
        embed_config = OpenAIEmbedderConfig(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            embedding_model="nomic-embed-text",
            embedding_dim=768
        )
        
        graphiti = Graphiti(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password123"),
            llm_client=OpenAIClient(config=llm_config),
            embedder=OpenAIEmbedder(config=embed_config)
        )
    return graphiti

# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="Chat2Graph API",
    description="Convert conversations into knowledge graphs",
    version="1.0.0"
)

# Allow CORS for n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    print("🚀 Starting Chat2Graph API...")
    g = get_graphiti()
    await g.build_indices_and_constraints()
    print("✅ Ready!")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Chat2Graph API",
        "endpoints": [
            "POST /add_conversation - Add a conversation to the graph",
            "POST /query - Query the knowledge graph",
            "GET /stats - Get graph statistics"
        ]
    }

@app.post("/add_conversation", response_model=ConversationResponse)
async def add_conversation(input: ConversationInput):
    """
    Add a conversation to the knowledge graph.
    
    n8n can call this endpoint to process new conversations.
    
    Example:
    ```json
    {
        "name": "slack_message_123",
        "content": "Alice: Hey, I met Bob at the conference...",
        "source_description": "Slack #general channel"
    }
    ```
    """
    from graphiti_core.nodes import EpisodeType
    
    try:
        g = get_graphiti()
        
        await g.add_episode(
            name=input.name,
            episode_body=input.content,
            source_description=input.source_description,
            reference_time=datetime.now(),
            source=EpisodeType.message
        )
        
        return ConversationResponse(
            success=True,
            message="Conversation processed and added to knowledge graph",
            name=input.name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_graph(input: QueryInput):
    """
    Query the knowledge graph with natural language.
    
    Example:
    ```json
    {
        "query": "Who works at Acme Corp?",
        "num_results": 5
    }
    ```
    """
    try:
        g = get_graphiti()
        results = await g.search(input.query, num_results=input.num_results)
        
        formatted_results = []
        for r in results:
            formatted_results.append({
                "fact": r.fact if hasattr(r, 'fact') else str(r),
                "uuid": r.uuid if hasattr(r, 'uuid') else None
            })
        
        return QueryResponse(
            query=input.query,
            results=formatted_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cypher")
async def execute_cypher(input: CypherInput):
    """
    Execute a raw Cypher query against the knowledge graph.
    
    Example:
    ```json
    {
        "cypher": "MATCH (n:Entity) RETURN n.name LIMIT 10"
    }
    ```
    """
    from neo4j import GraphDatabase
    
    try:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password123"))
        )
        
        with driver.session() as session:
            result = session.run(input.cypher)
            records = []
            for record in result:
                # Convert record to dict, handling Neo4j node/relationship types
                record_dict = {}
                for key in record.keys():
                    value = record[key]
                    # Convert Neo4j nodes to dicts
                    if hasattr(value, 'items'):  # Node-like
                        record_dict[key] = dict(value.items()) if hasattr(value, 'items') else str(value)
                    elif hasattr(value, '_properties'):  # Node or Relationship
                        record_dict[key] = dict(value._properties)
                    else:
                        record_dict[key] = value
                records.append(record_dict)
        
        driver.close()
        
        return {
            "cypher": input.cypher,
            "results": records,
            "count": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cypher error: {str(e)}")

@app.get("/schema")
async def get_schema():
    """
    Get the knowledge graph schema (node labels, relationship types, properties).
    Useful for generating Cypher queries.
    """
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password123"))
    )
    
    schema = {"node_labels": [], "relationship_types": [], "sample_properties": {}}
    
    with driver.session() as session:
        # Get node labels
        labels = session.run("CALL db.labels()").values()
        schema["node_labels"] = [label[0] for label in labels]
        
        # Get relationship types
        rel_types = session.run("CALL db.relationshipTypes()").values()
        schema["relationship_types"] = [rel[0] for rel in rel_types]
        
        # Get sample properties for Entity nodes
        try:
            sample = session.run("MATCH (n:Entity) RETURN keys(n) as props LIMIT 1").single()
            if sample:
                schema["sample_properties"]["Entity"] = sample["props"]
        except:
            pass
    
    driver.close()
    return schema

@app.get("/stats")
async def get_stats():
    """Get statistics about the knowledge graph."""
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password123"))
    )
    
    with driver.session() as session:
        # Count entities
        entity_count = session.run("MATCH (n:Entity) RETURN count(n) as count").single()["count"]
        
        # Count relationships
        rel_count = session.run("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count").single()["count"]
        
        # Count episodes
        episode_count = session.run("MATCH (n:Episodic) RETURN count(n) as count").single()["count"]
        
        # Count relationship types (including reclassified ones)
        rel_types = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count").values()
    
    driver.close()
    
    return {
        "entities": entity_count,
        "relationships": rel_count,
        "episodes": episode_count,
        "relationship_types": {r[0]: r[1] for r in rel_types}
    }


@app.post("/reclassify")
async def reclassify_relationships():
    """
    Reclassify RELATES_TO edges into specific relationship types using Ollama.
    
    This creates new typed edges (TREATS, PRESCRIBED, SUPPORTS, etc.) while
    preserving the original RELATES_TO edges.
    
    Note: This operation can take several minutes depending on the number of
    relationships and Ollama's response time.
    """
    import requests
    from neo4j import GraphDatabase
    from collections import Counter
    
    OLLAMA_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    RELATIONSHIP_TYPES = [
        "TREATS", "PRESCRIBED", "TAKES", "REFERRED", "SUPPORTS",
        "FAMILY_OF", "WORKS_AT", "DIAGNOSED_WITH", "TRIGGERS", "UNCERTAIN"
    ]
    
    CLASSIFICATION_PROMPT = """You are classifying relationships in a mental health knowledge graph.

Given a relationship between two entities, classify it into ONE of these types:
- TREATS: Healthcare provider treats a patient
- PRESCRIBED: Healthcare provider prescribed a medication
- TAKES: Patient takes a medication
- REFERRED: Provider referred patient to another provider
- SUPPORTS: Person emotionally supports another person
- FAMILY_OF: Family relationship (parent, sibling, child, spouse)
- WORKS_AT: Person works at an organization
- DIAGNOSED_WITH: Patient has been diagnosed with a condition
- TRIGGERS: An event or situation triggers a mental health symptom
- UNCERTAIN: The relationship doesn't clearly fit any category

Respond with ONLY the relationship type, nothing else.

FROM: {from_name}
FROM DESCRIPTION: {from_summary}

TO: {to_name}  
TO DESCRIPTION: {to_summary}

CONTEXT: {fact}

RELATIONSHIP TYPE:"""

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password123"))
    )
    
    # Get all RELATES_TO edges
    query = """
    MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity)
    RETURN 
        elementId(r) as rel_id,
        elementId(a) as from_id,
        a.name as from_name, 
        a.summary as from_summary,
        elementId(b) as to_id,
        b.name as to_name, 
        b.summary as to_summary,
        r.fact as fact
    """
    
    with driver.session() as session:
        result = session.run(query)
        edges = [dict(record) for record in result]
    
    if len(edges) == 0:
        driver.close()
        return {"message": "No RELATES_TO edges found", "processed": 0}
    
    stats = Counter()
    created = 0
    
    for edge in edges:
        # Classify using Ollama
        prompt = CLASSIFICATION_PROMPT.format(
            from_name=edge["from_name"] or "Unknown",
            from_summary=edge["from_summary"] or "",
            to_name=edge["to_name"] or "Unknown",
            to_summary=edge["to_summary"] or "",
            fact=edge["fact"] or ""
        )
        
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 20}
                },
                timeout=60
            )
            
            rel_type = "UNCERTAIN"
            if response.status_code == 200:
                classification = response.json().get("response", "").strip().upper()
                for rt in RELATIONSHIP_TYPES:
                    if rt in classification:
                        rel_type = rt
                        break
        except:
            rel_type = "UNCERTAIN"
        
        stats[rel_type] += 1
        
        # Create typed edge (skip UNCERTAIN)
        if rel_type != "UNCERTAIN":
            create_query = f"""
            MATCH (a:Entity), (b:Entity)
            WHERE elementId(a) = $from_id AND elementId(b) = $to_id
            CREATE (a)-[r:{rel_type} {{fact: $fact, source: 'reclassified'}}]->(b)
            """
            with driver.session() as session:
                session.run(create_query, 
                           from_id=edge["from_id"], 
                           to_id=edge["to_id"], 
                           fact=edge["fact"] or "")
            created += 1
    
    driver.close()
    
    return {
        "message": "Reclassification complete",
        "processed": len(edges),
        "new_edges_created": created,
        "kept_as_relates_to": stats["UNCERTAIN"],
        "classification_breakdown": dict(stats)
    }

# ============================================
# Run the server
# ============================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                   Chat2Graph API                         ║
╠══════════════════════════════════════════════════════════╣
║  Endpoints:                                              ║
║    POST /add_conversation  - Add conversation to graph   ║
║    POST /query            - Semantic search (NL)         ║
║    POST /cypher           - Execute Cypher query         ║
║    POST /reclassify       - Reclassify relationships     ║
║    GET  /schema           - Get graph schema             ║
║    GET  /stats            - Get graph statistics         ║
║                                                          ║
║  n8n Webhook URL: http://localhost:8080/add_conversation ║
╚══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8080)
