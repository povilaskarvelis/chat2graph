#!/usr/bin/env python3
"""
Simple chat interface for querying the mental health knowledge graph.

Run with: python chat.py

Ask questions in natural language like:
- "What symptoms has the patient experienced?"
- "Who provides support to the patient?"
- "What medications have been prescribed?"
- "What is the care team?"
"""

import requests
import sys

API_URL = "http://localhost:8080"

def query_graph(question: str) -> list:
    """Send a natural language query to the knowledge graph."""
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"query": question, "num_results": 5},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: API server not running. Start it with: python api_server.py")
        return []
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []

def print_results(results: list):
    """Pretty print the query results."""
    if not results:
        print("   (No results found)")
        return
    
    for i, result in enumerate(results, 1):
        fact = result.get("fact", str(result))
        print(f"   {i}. {fact}")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        Mental Health Knowledge Graph - Chat Interface        ║
╠══════════════════════════════════════════════════════════════╣
║  Ask questions in natural language about the knowledge graph ║
║  Type 'quit' or 'exit' to stop                               ║
║  Type 'help' for example questions                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        stats = response.json()
        print(f"📊 Connected! Graph has {stats['entities']} entities, {stats['relationships']} relationships\n")
    except:
        print("⚠️  Warning: API server may not be running. Start it with: python api_server.py\n")
    
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
Example questions you can ask:
  • What symptoms has the patient experienced?
  • Who provides support to the patient?
  • What medications have been prescribed?
  • Who is Dr. Chen?
  • What treatments are being used?
  • Who are the care team members?
  • What triggered the anxiety?
  • What is the patient's support network?
                """)
                continue
            
            print(f"\n💭 Searching for: \"{question}\"")
            results = query_graph(question)
            print("\n📋 Results:")
            print_results(results)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
