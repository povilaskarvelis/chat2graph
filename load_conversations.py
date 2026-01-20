"""
Load sample conversations into the knowledge graph.

This script processes multiple conversations and builds a rich knowledge graph
with entities and relationships across all of them.

Usage:
    python load_conversations.py
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import sample data
from sample_conversations import CONVERSATIONS


def get_llm_client():
    """Create LLM client configured for Ollama."""
    from graphiti_core.llm_client import OpenAIClient
    from graphiti_core.llm_client.config import LLMConfig
    
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    config = LLMConfig(
        api_key="ollama",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        model=model,
        small_model=model
    )
    return OpenAIClient(config=config)


def get_embedder():
    """Create embedder configured for Ollama."""
    from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig
    
    config = OpenAIEmbedderConfig(
        api_key="ollama",
        base_url="http://localhost:11434/v1",
        embedding_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        embedding_dim=768
    )
    return OpenAIEmbedder(config=config)


async def main():
    """Load all sample conversations into the knowledge graph."""
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    
    print("=" * 60)
    print("🚀 Loading Sample Conversations into Knowledge Graph")
    print("=" * 60)
    
    # Setup
    print("\n🧠 Setting up AI models...")
    llm_client = get_llm_client()
    embedder = get_embedder()
    print("   ✅ Ollama ready")
    
    # Connect to Neo4j
    print("\n📡 Connecting to Neo4j...")
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password123"),
        llm_client=llm_client,
        embedder=embedder
    )
    print("   ✅ Connected")
    
    # Initialize schema
    print("\n🔧 Initializing schema...")
    await graphiti.build_indices_and_constraints()
    print("   ✅ Ready")
    
    # Process each conversation
    print("\n" + "=" * 60)
    print("📝 Processing Conversations")
    print("=" * 60)
    
    base_time = datetime.now()
    
    for i, conv in enumerate(CONVERSATIONS):
        print(f"\n[{i+1}/{len(CONVERSATIONS)}] Processing: {conv['name']}")
        print(f"    Source: {conv['source_description']}")
        
        # Use different timestamps for each conversation
        # (Graphiti uses timestamps for temporal reasoning)
        reference_time = base_time - timedelta(days=len(CONVERSATIONS) - i)
        
        try:
            await graphiti.add_episode(
                name=conv['name'],
                episode_body=conv['content'],
                source_description=conv['source_description'],
                reference_time=reference_time,
                source=EpisodeType.message
            )
            print(f"    ✅ Done!")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Run some queries to show what was extracted
    print("\n" + "=" * 60)
    print("🔍 Testing Knowledge Graph Queries")
    print("=" * 60)
    
    queries = [
        "Who works at DataFlow Inc?",
        "Which investors are mentioned?",
        "Who knows people at Google?",
        "What companies are mentioned?",
        "Who is connected to Andreessen Horowitz?",
        "What research collaborations exist?",
    ]
    
    for query in queries:
        print(f"\n❓ {query}")
        try:
            results = await graphiti.search(query, num_results=3)
            if results:
                for j, result in enumerate(results, 1):
                    fact = result.fact if hasattr(result, 'fact') else str(result)
                    print(f"   {j}. {fact}")
            else:
                print("   (No results)")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Cleanup
    await graphiti.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎉 COMPLETE!")
    print("=" * 60)
    print(f"""
Your knowledge graph now contains information about:

📊 ENTITIES EXTRACTED:
   • People: Emma, Marcus, Sophie, Dr. Rebecca Torres, James Park, 
            Nina Chen, Michael Zhang, Lisa Wang, Tom, Alex Rivera, 
            and many more...
   • Companies: DataFlow Inc, Nexus Systems, Sequoia Capital, 
               Google, DeepMind, Stanford, MIT, Salesforce, etc.
   • Investors: Andreessen Horowitz, Accel, Index Ventures, etc.

🔗 RELATIONSHIPS FOUND:
   • Employment: Who works where
   • Investments: Who invested in what
   • Collaborations: Research partnerships
   • Introductions: Who knows who

📊 View your graph:
   1. Open http://localhost:7474
   2. Login: neo4j / password123
   3. Run: MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100
""")


if __name__ == "__main__":
    asyncio.run(main())
