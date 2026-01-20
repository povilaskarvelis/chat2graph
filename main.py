"""
Chat2Graph: Convert conversations into a knowledge graph

This script demonstrates how to:
1. Connect to a Neo4j database
2. Process conversation text with Graphiti
3. Extract entities and relationships automatically
4. Query the resulting knowledge graph

SUPPORTED LLM PROVIDERS:
- OpenAI (default): Set OPENAI_API_KEY
- Anthropic Claude: Set ANTHROPIC_API_KEY and LLM_PROVIDER=anthropic
- Groq (free tier!): Set GROQ_API_KEY and LLM_PROVIDER=groq
- Ollama (local, free): Set LLM_PROVIDER=ollama (no API key needed)
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_llm_client():
    """
    Create the appropriate LLM client based on environment configuration.
    
    Supports: OpenAI, Groq (via OpenAI-compatible API), Ollama (local)
    
    Groq and Ollama work because they provide OpenAI-compatible APIs,
    so we just point the OpenAI client at their servers using base_url!
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    # Import the clients
    from graphiti_core.llm_client import OpenAIClient
    from graphiti_core.llm_client.config import LLMConfig
    
    if provider == "openai":
        # Default: OpenAI
        print(f"   🤖 Using OpenAI")
        config = LLMConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        )
        return OpenAIClient(config=config)
    
    elif provider == "groq":
        # Groq - fast and has FREE tier!
        # Groq provides an OpenAI-compatible API
        print(f"   🤖 Using Groq (free tier!)")
        config = LLMConfig(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        )
        return OpenAIClient(config=config)
    
    elif provider == "ollama":
        # Ollama - runs locally, 100% free and private
        # Ollama also provides an OpenAI-compatible API
        print(f"   🤖 Using Ollama (local, free)")
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        config = LLMConfig(
            api_key="ollama",  # Ollama doesn't need a real key
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            model=model,
            small_model=model  # Use same model for "small" tasks too
        )
        return OpenAIClient(config=config)
    
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. "
                        f"Supported: openai, groq, ollama")


def get_embedder():
    """
    Create the appropriate embedder based on environment configuration.
    
    The embedder converts text into vectors for similarity search.
    Ollama provides OpenAI-compatible embedding endpoints!
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig
    
    if provider == "openai":
        print(f"   📊 Using OpenAI embeddings")
        config = OpenAIEmbedderConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            embedding_model="text-embedding-3-small"
        )
        return OpenAIEmbedder(config=config)
    
    elif provider == "ollama":
        # Ollama provides embeddings via OpenAI-compatible API
        print(f"   📊 Using Ollama embeddings (local)")
        config = OpenAIEmbedderConfig(
            api_key="ollama",  # Ollama doesn't need a real key
            base_url="http://localhost:11434/v1",
            embedding_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            embedding_dim=768  # nomic-embed-text dimension
        )
        return OpenAIEmbedder(config=config)
    
    else:
        # For Groq or others without embeddings, we'd need OpenAI
        # For now, return None and let Graphiti use its default
        print(f"   📊 Using default embeddings")
        return None


async def main():
    """Main function to demonstrate the conversation-to-graph pipeline."""
    
    # ----------------------------------------
    # Step 1: Import Graphiti (after env is loaded)
    # ----------------------------------------
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    
    print("🚀 Chat2Graph Starting...\n")
    
    # ----------------------------------------
    # Step 2: Set up LLM Client and Embedder
    # ----------------------------------------
    print("🧠 Setting up AI models...")
    try:
        llm_client = get_llm_client()
        embedder = get_embedder()
    except Exception as e:
        print(f"   ❌ AI setup failed: {e}")
        print("\n💡 Check your .env file and make sure Ollama is running!")
        print("   Run: brew services start ollama")
        return
    
    # ----------------------------------------
    # Step 3: Connect to Neo4j
    # ----------------------------------------
    print("\n📡 Connecting to Neo4j...")
    
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
    
    try:
        graphiti = Graphiti(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
            llm_client=llm_client,  # Use our configured LLM
            embedder=embedder       # Use our configured embedder
        )
        print(f"   ✅ Connected to {neo4j_uri}\n")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n💡 Make sure Neo4j is running!")
        print("   Option 1: Start Docker and run:")
        print("     docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \\")
        print("       -e NEO4J_AUTH=neo4j/password123 neo4j:latest")
        print("\n   Option 2: Use Neo4j Aura (free cloud):")
        print("     https://neo4j.com/cloud/aura-free/")
        return
    
    # ----------------------------------------
    # Step 4: Initialize the graph schema
    # ----------------------------------------
    print("🔧 Initializing graph schema...")
    await graphiti.build_indices_and_constraints()
    print("   ✅ Schema ready\n")
    
    # ----------------------------------------
    # Step 5: Sample conversation to process
    # ----------------------------------------
    # This is an example conversation. In real use, you'd get this from:
    # - Slack/Discord messages
    # - Meeting transcripts
    # - Support tickets
    # - Any text conversations
    
    conversation = """
    Alice: Hey team, I just got back from the Seattle tech conference!
    
    Bob: Oh nice! How was it? Did you meet anyone interesting?
    
    Alice: Yes! I met Sarah Chen from Acme Corp. She's their VP of Engineering.
    Really impressive - they're building some cool AI stuff.
    
    Bob: Acme Corp... aren't they expanding to Europe soon?
    
    Alice: Exactly! Sarah mentioned their CEO, John Miller, is leading that 
    initiative. They're opening an office in London next quarter.
    
    Carol: That's exciting. I heard John used to work at TechGiant before 
    founding Acme. Small world!
    
    Alice: Sarah also introduced me to their lead data scientist, Dr. Wei Zhang.
    He's doing fascinating work on knowledge graphs - might be worth reaching out.
    """
    
    print("📝 Processing conversation...")
    print("   (This may take 30-60 seconds as the AI extracts entities)\n")
    
    # ----------------------------------------
    # Step 6: Add conversation to knowledge graph
    # ----------------------------------------
    # Graphiti will automatically:
    # - Extract entities (people, companies, places, etc.)
    # - Identify relationships between entities
    # - Store everything in Neo4j with timestamps
    
    from datetime import datetime
    
    try:
        await graphiti.add_episode(
            name="team_chat_001",
            episode_body=conversation,
            source_description="Team Slack conversation about Seattle conference",
            reference_time=datetime.now(),  # When this conversation happened
            source=EpisodeType.message      # Type of content
        )
        print("   ✅ Conversation processed and added to graph!\n")
    except Exception as e:
        print(f"   ❌ Processing failed: {e}")
        print("\n💡 Make sure your API key is set correctly in .env")
        await graphiti.close()
        return
    
    # ----------------------------------------
    # Step 7: Query the knowledge graph
    # ----------------------------------------
    print("🔍 Querying the knowledge graph...\n")
    
    queries = [
        "Who works at Acme Corp?",
        "What companies are expanding to Europe?",
        "Who is John Miller?",
        "What happened at the Seattle conference?",
    ]
    
    for query in queries:
        print(f"   Q: {query}")
        try:
            results = await graphiti.search(query, num_results=3)
            if results:
                for i, result in enumerate(results, 1):
                    # Each result has fact content and metadata
                    print(f"      {i}. {result.fact if hasattr(result, 'fact') else result}")
            else:
                print("      (No results found)")
        except Exception as e:
            print(f"      Error: {e}")
        print()
    
    # ----------------------------------------
    # Step 8: Clean up
    # ----------------------------------------
    await graphiti.close()
    
    print("=" * 50)
    print("🎉 Success! Your knowledge graph is ready.")
    print("\n📊 View your graph visually:")
    print("   1. Open http://localhost:7474 in your browser")
    print("   2. Log in with neo4j / password123")
    print("   3. Run this query:")
    print("      MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
