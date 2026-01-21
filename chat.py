#!/usr/bin/env python3
"""
Hybrid chat interface for querying the mental health knowledge graph.

Uses LLM-based routing to decide between:
- Semantic search (for general questions about facts/relationships)
- Cypher queries (for structured questions: counts, lists, aggregates)

Run with: python chat.py

Ask questions in natural language like:
- "What symptoms has the patient experienced?" (→ semantic)
- "How many medications were prescribed?" (→ cypher)
- "List all the care team members" (→ cypher)
- "Tell me about Dr. Chen's role" (→ semantic)
"""

import requests
import json
import sys

API_URL = "http://localhost:8080"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"

# ============================================
# Router prompt - LLM decides query type
# ============================================

ROUTER_PROMPT = """Classify this question for a knowledge graph. Reply with ONE word only.

CYPHER - use for:
- Counting: "how many", "count", "total"
- Listing: "list all", "show all", "return all"  
- Finding by name: "find entities named", "show doctors", "list medications"
- Connections: "who is connected to", "show relationships"
- Database queries: "show 10 entities", "limit 5"

SEMANTIC - use for:
- Understanding: "what is", "tell me about", "explain", "describe"
- General questions: "what symptoms", "who supports", "what happened"
- Exploratory: questions without specific counts or lists

Question: "{question}"

Reply: SEMANTIC or CYPHER"""

# ============================================
# Cypher generation prompt
# ============================================

CYPHER_PROMPT = """Generate a Cypher query for a Neo4j mental health knowledge graph.

SCHEMA:
- Nodes: Entity (properties: name, summary)
- Relationships: RELATES_TO, MENTIONS

IMPORTANT RULES:
1. Keep queries SIMPLE - avoid complex nested queries
2. Use toLower() for case-insensitive matching: WHERE toLower(n.name) CONTAINS 'dr'
3. Always add LIMIT (use 10-20 for lists, omit only for counts)
4. Return name and summary for useful results
5. Do NOT use entity_type (it's always null)

WORKING EXAMPLES:

Q: "List all doctors"
MATCH (n:Entity) WHERE toLower(n.name) CONTAINS 'dr' RETURN n.name, n.summary LIMIT 10

Q: "Show entities mentioning anxiety"
MATCH (n:Entity) WHERE toLower(n.summary) CONTAINS 'anxiety' RETURN n.name, n.summary LIMIT 10

Q: "Count all entities"
MATCH (n:Entity) RETURN count(n) AS total

Q: "Show all connections to Dr. Chen"
MATCH (a:Entity)-[r]->(b:Entity) WHERE a.name = 'Dr. Chen' RETURN a.name, type(r), b.name LIMIT 20

Q: "Find entities related to sertraline"  
MATCH (n:Entity) WHERE toLower(n.summary) CONTAINS 'sertraline' RETURN n.name, n.summary LIMIT 10

Q: "Count relationships"
MATCH ()-[r]->() RETURN type(r), count(r) AS total

Q: "Show 5 entity names"
MATCH (n:Entity) RETURN n.name LIMIT 5

Q: "Find who is connected to Patient"
MATCH (a:Entity)-[r]->(b:Entity) WHERE a.name = 'Patient' RETURN a.name, type(r), b.name LIMIT 20

NOW GENERATE A QUERY FOR: "{question}"

Reply with ONLY the Cypher query. No explanation, no markdown, no code blocks."""

# ============================================
# API calls
# ============================================

def call_ollama(prompt: str) -> str:
    """Call Ollama for LLM responses."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=180  # 3 minutes for slower local models
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Ollama not running. Start it with: ollama serve")
        return ""
    except Exception as e:
        print(f"\n❌ Ollama error: {e}")
        return ""

def semantic_search(question: str) -> list:
    """Perform semantic search via the API."""
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"query": question, "num_results": 5},
            timeout=120  # 2 minutes
        )
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print(f"\n❌ Semantic search error: {e}")
        return []

def execute_cypher(cypher: str) -> dict:
    """Execute a Cypher query via the API."""
    try:
        response = requests.post(
            f"{API_URL}/cypher",
            json={"cypher": cypher},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get("detail", str(e)) if e.response else str(e)
        print(f"\n❌ Cypher error: {error_detail}")
        return {"results": [], "error": error_detail}
    except Exception as e:
        print(f"\n❌ Cypher execution error: {e}")
        return {"results": [], "error": str(e)}

def get_stats() -> dict:
    """Get graph statistics."""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        return response.json()
    except:
        return {}

# ============================================
# Hybrid query logic
# ============================================

def hybrid_query(question: str) -> tuple:
    """
    Route the question to semantic search or Cypher based on LLM classification.
    Returns: (query_type, results, cypher_used)
    """
    # Step 1: Ask LLM to classify the query
    print("   🤔 Analyzing question...")
    route = call_ollama(ROUTER_PROMPT.format(question=question))
    
    if not route:
        # Fallback to semantic if LLM fails
        route = "SEMANTIC"
    
    route = route.upper().strip()
    
    # Normalize response (LLM might say "SEMANTIC." or "The answer is CYPHER")
    if "CYPHER" in route:
        route = "CYPHER"
    else:
        route = "SEMANTIC"
    
    # Step 2: Execute the appropriate query type
    if route == "CYPHER":
        print("   📊 Generating Cypher query...")
        cypher = call_ollama(CYPHER_PROMPT.format(question=question))
        
        # Strip markdown code blocks if present (LLMs often wrap in ```cypher ... ```)
        if cypher:
            cypher = cypher.strip()
            if cypher.startswith("```"):
                # Remove opening ```cypher or ``` and closing ```
                lines = cypher.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                cypher = "\n".join(lines).strip()
        
        if not cypher or not cypher.strip().upper().startswith(("MATCH", "RETURN", "CALL")):
            # Fallback to semantic if Cypher generation fails
            print("   ⚠️  Cypher generation failed, using semantic search...")
            results = semantic_search(question)
            return ("SEMANTIC (fallback)", results, None)
        
        print(f"   🔧 Cypher: {cypher[:80]}{'...' if len(cypher) > 80 else ''}")
        result = execute_cypher(cypher)
        
        if result.get("error"):
            # Fallback to semantic if Cypher execution fails
            print("   ⚠️  Cypher failed, using semantic search...")
            results = semantic_search(question)
            return ("SEMANTIC (fallback)", results, cypher)
        
        return ("CYPHER", result.get("results", []), cypher)
    else:
        print("   🔍 Using semantic search...")
        results = semantic_search(question)
        return ("SEMANTIC", results, None)

# ============================================
# Output formatting
# ============================================

def print_results(query_type: str, results: list, cypher: str = None):
    """Pretty print the query results."""
    print(f"\n📋 Results ({query_type}):")
    
    if cypher:
        print(f"   Query: {cypher}")
        print()
    
    if not results:
        print("   (No results found)")
        return
    
    if query_type.startswith("SEMANTIC"):
        # Semantic results have 'fact' field
        for i, result in enumerate(results, 1):
            fact = result.get("fact", str(result))
            print(f"   {i}. {fact}")
    else:
        # Cypher results are dicts
        for i, record in enumerate(results, 1):
            if isinstance(record, dict):
                # Format dict nicely
                parts = []
                for k, v in record.items():
                    if v is not None:
                        parts.append(f"{v}")
                print(f"   {i}. {' | '.join(parts) if parts else record}")
            else:
                print(f"   {i}. {record}")

# ============================================
# Main chat loop
# ============================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Mental Health Knowledge Graph - Hybrid Chat Interface    ║
╠══════════════════════════════════════════════════════════════╣
║  Ask questions in natural language                           ║
║  The LLM will route to semantic search OR Cypher queries     ║
║                                                              ║
║  Type 'quit' or 'exit' to stop                               ║
║  Type 'help' for example questions                           ║
║  Type 'mode' to see how routing works                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check connections
    stats = get_stats()
    if stats:
        print(f"📊 Connected! Graph has {stats.get('entities', '?')} entities, {stats.get('relationships', '?')} relationships")
    else:
        print("⚠️  Warning: API server may not be running. Start it with: python api_server.py")
    
    # Check Ollama
    test = call_ollama("Reply with just: OK")
    if "OK" in test.upper():
        print("🤖 Ollama connected for query routing\n")
    else:
        print("⚠️  Ollama may not be running. Start it with: ollama serve\n")
    
    while True:
        try:
            question = input("🔍 Ask a question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            if question.lower() == 'help':
                print("""
Example questions:

  Semantic search (general questions):
  • What symptoms has the patient experienced?
  • Tell me about Dr. Chen
  • Who provides support to the patient?
  • What treatments are being used?
  
  Cypher queries (structured questions):
  • How many symptoms are recorded?
  • List all medications
  • Count the care team members
  • Show all entities of type 'person'
                """)
                continue
            
            if question.lower() == 'mode':
                print("""
How hybrid routing works:

  1. Your question goes to the LLM (Ollama)
  2. LLM classifies it as SEMANTIC or CYPHER
  3. If SEMANTIC: vector similarity search on facts
  4. If CYPHER: LLM generates query → executes on Neo4j
  5. If Cypher fails: falls back to semantic search
  
This gives you the best of both worlds!
                """)
                continue
            
            print()
            query_type, results, cypher = hybrid_query(question)
            print_results(query_type, results, cypher)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
