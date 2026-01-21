"""
Load empirical clinical conversations into the knowledge graph.

This script processes clinical interview transcripts and builds knowledge graphs
that can be analyzed to identify patterns characteristic of different disorders.

Usage:
    python load_empirical.py                    # List available conversations
    python load_empirical.py <name>             # Load a specific conversation
    python load_empirical.py all                # Load all conversations

The script loads conversations from empirical_conversations.py which contains:
- GAD (Generalized Anxiety Disorder) interviews
- ADHD interviews  
- Wernicke's Aphasia interview

Each conversation has metadata (diagnosis, meets_criteria) that serves as
ground truth for analyzing graph structural differences.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import empirical data
from empirical_conversations import CONVERSATIONS

# Build lookup dict
CONVERSATIONS_BY_NAME = {conv['name']: conv for conv in CONVERSATIONS}


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


def list_conversations():
    """List all available conversations."""
    print("=" * 65)
    print("  Available Conversations")
    print("=" * 65)
    print()
    for conv in CONVERSATIONS:
        diagnosis = conv.get('diagnosis', 'Unknown')
        meets = conv.get('meets_criteria', None)
        meets_str = "meets criteria" if meets else "subthreshold" if meets is False else ""
        print(f"  {conv['name']}")
        print(f"      {diagnosis} ({meets_str})")
    print()
    print("Usage:")
    print("  python load_empirical.py <name>    # Load specific conversation")
    print("  python load_empirical.py all       # Load all conversations")
    print()


async def load_single_conversation(conv):
    """Load a single conversation into the knowledge graph."""
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    
    diagnosis = conv.get('diagnosis', 'Unknown')
    meets = conv.get('meets_criteria', None)
    meets_str = "meets criteria" if meets else "subthreshold" if meets is False else ""
    
    print("=" * 65)
    print(f"  Loading: {conv['name']}")
    print(f"  {diagnosis} ({meets_str})")
    print("=" * 65)
    
    # Setup
    print("\n[1/3] Setting up AI models...")
    llm_client = get_llm_client()
    embedder = get_embedder()
    print("      Ollama ready")
    
    # Connect to Neo4j
    print("\n[2/3] Connecting to Neo4j...")
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password123"),
        llm_client=llm_client,
        embedder=embedder
    )
    print("      Connected")
    
    # Initialize schema
    await graphiti.build_indices_and_constraints()
    
    # Process the conversation
    print(f"\n[3/3] Processing conversation...")
    
    # Build source description with metadata
    source_desc = f"{conv['source_description']} | Diagnosis: {diagnosis}"
    if meets is not None:
        source_desc += f" | Meets criteria: {meets}"
    
    try:
        await graphiti.add_episode(
            name=conv['name'],
            episode_body=conv['content'],
            source_description=source_desc,
            reference_time=datetime.now(),
            source=EpisodeType.message
        )
        print(f"      Done!")
    except Exception as e:
        print(f"      Error: {e}")
    
    # Cleanup
    await graphiti.close()
    
    print("\n" + "=" * 65)
    print(f"  COMPLETE: {conv['name']}")
    print("=" * 65)
    print(f"""
View in Neo4j:
  MATCH (e:Episodic {{name: '{conv['name']}'}})-[:MENTIONS]->(n) RETURN e, n
""")


async def load_all_conversations():
    """Load all conversations into the knowledge graph."""
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    
    print("=" * 65)
    print("  Loading All Empirical Clinical Conversations")
    print("=" * 65)
    
    # Setup
    print("\n[1/3] Setting up AI models...")
    llm_client = get_llm_client()
    embedder = get_embedder()
    print("      Ollama ready")
    
    # Connect to Neo4j
    print("\n[2/3] Connecting to Neo4j...")
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password123"),
        llm_client=llm_client,
        embedder=embedder
    )
    print("      Connected")
    
    # Initialize schema
    await graphiti.build_indices_and_constraints()
    
    # Process each conversation
    print(f"\n[3/3] Processing {len(CONVERSATIONS)} conversations...")
    print("-" * 65)
    
    base_time = datetime.now()
    results = []
    
    for i, conv in enumerate(CONVERSATIONS):
        diagnosis = conv.get('diagnosis', 'Unknown')
        meets = conv.get('meets_criteria', None)
        meets_str = "meets criteria" if meets else "subthreshold" if meets is False else ""
        
        print(f"\n  [{i+1}/{len(CONVERSATIONS)}] {conv['name']}")
        print(f"      {diagnosis} ({meets_str})")
        
        reference_time = base_time - timedelta(days=len(CONVERSATIONS) - i)
        
        source_desc = f"{conv['source_description']} | Diagnosis: {diagnosis}"
        if meets is not None:
            source_desc += f" | Meets criteria: {meets}"
        
        try:
            await graphiti.add_episode(
                name=conv['name'],
                episode_body=conv['content'],
                source_description=source_desc,
                reference_time=reference_time,
                source=EpisodeType.message
            )
            print(f"      Done!")
            results.append({"name": conv['name'], "status": "success"})
        except Exception as e:
            print(f"      Error: {e}")
            results.append({"name": conv['name'], "status": "error"})
    
    await graphiti.close()
    
    success = sum(1 for r in results if r['status'] == 'success')
    print("\n" + "=" * 65)
    print(f"  COMPLETE: {success}/{len(CONVERSATIONS)} loaded")
    print("=" * 65)


async def main():
    """Main entry point - handle command line arguments."""
    if len(sys.argv) < 2:
        list_conversations()
        return
    
    arg = sys.argv[1]
    
    if arg == "all":
        await load_all_conversations()
    elif arg in CONVERSATIONS_BY_NAME:
        await load_single_conversation(CONVERSATIONS_BY_NAME[arg])
    else:
        print(f"Unknown conversation: {arg}")
        print()
        list_conversations()


if __name__ == "__main__":
    asyncio.run(main())
