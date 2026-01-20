"""
Quick test script - processes ONE short conversation.
Takes about 1-2 minutes with Ollama.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Short test conversation
TEST_CONVERSATION = """
John: Did you hear? Apple is acquiring TechStartup for $500 million.
Sarah: Wow! That's huge. Tim Cook must really want their AI team.
John: Exactly. The CEO Maria Garcia built an amazing computer vision platform.
Sarah: I worked with Maria at Stanford. She's brilliant.
John: Their lead researcher Dr. Lee has 50 patents in neural networks.
"""

async def main():
    from graphiti_core import Graphiti
    from graphiti_core.llm_client import OpenAIClient
    from graphiti_core.llm_client.config import LLMConfig
    from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig
    from graphiti_core.nodes import EpisodeType
    
    print("🚀 Quick Test - Processing 1 short conversation\n")
    
    # Setup Ollama
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
    
    print("📡 Connecting...")
    graphiti = Graphiti(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password123",
        llm_client=OpenAIClient(config=llm_config),
        embedder=OpenAIEmbedder(config=embed_config)
    )
    
    await graphiti.build_indices_and_constraints()
    print("✅ Connected\n")
    
    print("📝 Processing conversation (1-2 min)...")
    print("   Extracting: People, Companies, Relationships...\n")
    
    await graphiti.add_episode(
        name="quick_test",
        episode_body=TEST_CONVERSATION,
        source_description="Quick test conversation",
        reference_time=datetime.now(),
        source=EpisodeType.message
    )
    
    print("✅ Done!\n")
    
    # Test queries
    print("🔍 Testing queries:\n")
    queries = ["Who works at Apple?", "What is TechStartup?", "Who is Maria Garcia?"]
    
    for q in queries:
        print(f"Q: {q}")
        results = await graphiti.search(q, num_results=2)
        for r in results:
            print(f"   → {r.fact if hasattr(r, 'fact') else r}")
        print()
    
    await graphiti.close()
    print("🎉 Success! View graph at http://localhost:7474")

if __name__ == "__main__":
    asyncio.run(main())
