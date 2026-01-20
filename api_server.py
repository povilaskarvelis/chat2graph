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
    
    driver.close()
    
    return {
        "entities": entity_count,
        "relationships": rel_count,
        "episodes": episode_count
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
║    POST /query            - Query the knowledge graph    ║
║    GET  /stats            - Get graph statistics         ║
║                                                          ║
║  n8n Webhook URL: http://localhost:8080/add_conversation ║
╚══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8080)
