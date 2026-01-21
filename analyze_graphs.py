"""
Analyze knowledge graph patterns across different disorders.

This script queries the Neo4j graph to extract structural features
that may differentiate between GAD, ADHD, and Wernicke's Aphasia.

Usage:
    python analyze_graphs.py

The analysis looks at:
- Node counts and types per conversation
- Edge density and connectivity
- Common entity patterns by disorder
- Symptom clustering
"""

import os
from collections import defaultdict
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

# Map conversation names to disorder categories
# Format: (disorder_demonstrated, meets_criteria)
# Note: These are ACTED scenarios for educational purposes, not real patients.
# meets_criteria = True means the actor's portrayed symptoms meet DSM-5 criteria
# meets_criteria = False means subthreshold/does not meet full criteria
CONVERSATION_DISORDERS = {
    "gad_sarah_001": ("GAD", True),
    "gad_sarah_002": ("GAD", True),   # with comorbidities
    "gad_sarah_003": ("GAD", False),  # subthreshold
    "adhd_elise_001": ("ADHD", False),
    "adhd_elise_002": ("ADHD", True),
    "adhd_elise_003": ("ADHD", True),
    "wernickes_aphasia_byron_001": ("Wernicke's Aphasia", True),
}


def get_driver():
    """Create Neo4j driver."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_graph_stats(driver):
    """Get overall graph statistics."""
    with driver.session() as session:
        # Total counts
        result = session.run("""
            MATCH (n:Entity) 
            RETURN count(n) as node_count
        """)
        node_count = result.single()["node_count"]
        
        result = session.run("""
            MATCH ()-[r]->() 
            RETURN count(r) as edge_count
        """)
        edge_count = result.single()["edge_count"]
        
        # Episode counts
        result = session.run("""
            MATCH (e:Episodic) 
            RETURN count(e) as episode_count
        """)
        episode_count = result.single()["episode_count"]
        
        return {
            "total_nodes": node_count,
            "total_edges": edge_count,
            "total_episodes": episode_count
        }


def get_nodes_per_episode(driver):
    """Get node counts grouped by episode (conversation)."""
    query = """
    MATCH (e:Episodic)-[:MENTIONS]->(n:Entity)
    RETURN e.name as episode, count(DISTINCT n) as node_count
    ORDER BY episode
    """
    
    with driver.session() as session:
        result = session.run(query)
        return {r["episode"]: r["node_count"] for r in result}


def get_edges_per_episode(driver):
    """Get edge counts for entities mentioned in each episode."""
    query = """
    MATCH (e:Episodic)-[:MENTIONS]->(n:Entity)
    WITH e, collect(DISTINCT n) as nodes
    UNWIND nodes as n1
    UNWIND nodes as n2
    MATCH (n1)-[r]->(n2)
    WHERE n1 <> n2
    RETURN e.name as episode, count(DISTINCT r) as edge_count
    ORDER BY episode
    """
    
    with driver.session() as session:
        result = session.run(query)
        return {r["episode"]: r["edge_count"] for r in result}


def get_entity_names_per_episode(driver):
    """Get entity names grouped by episode."""
    query = """
    MATCH (e:Episodic)-[:MENTIONS]->(n:Entity)
    RETURN e.name as episode, collect(DISTINCT n.name) as entities
    ORDER BY episode
    """
    
    with driver.session() as session:
        result = session.run(query)
        return {r["episode"]: r["entities"] for r in result}


def get_relationship_facts_per_episode(driver):
    """Get relationship facts for each episode."""
    query = """
    MATCH (e:Episodic)-[:MENTIONS]->(n:Entity)
    WITH e, collect(DISTINCT n) as nodes
    UNWIND nodes as n1
    UNWIND nodes as n2  
    MATCH (n1)-[r]->(n2)
    WHERE n1 <> n2
    RETURN e.name as episode, 
           n1.name as from_node,
           n2.name as to_node,
           r.fact as fact
    ORDER BY episode
    """
    
    with driver.session() as session:
        result = session.run(query)
        edges_by_episode = defaultdict(list)
        for r in result:
            edges_by_episode[r["episode"]].append({
                "from": r["from_node"],
                "to": r["to_node"],
                "fact": r["fact"]
            })
        return dict(edges_by_episode)


def analyze_by_disorder(nodes_per_ep, edges_per_ep, entities_per_ep):
    """Aggregate metrics by disorder type."""
    by_disorder = defaultdict(lambda: {
        "episodes": [],
        "node_counts": [],
        "edge_counts": [],
        "all_entities": set(),
        "meets_criteria": []
    })
    
    for episode, disorder_info in CONVERSATION_DISORDERS.items():
        disorder, meets = disorder_info
        
        node_count = nodes_per_ep.get(episode, 0)
        edge_count = edges_per_ep.get(episode, 0)
        entities = entities_per_ep.get(episode, [])
        
        by_disorder[disorder]["episodes"].append(episode)
        by_disorder[disorder]["node_counts"].append(node_count)
        by_disorder[disorder]["edge_counts"].append(edge_count)
        by_disorder[disorder]["all_entities"].update(entities)
        by_disorder[disorder]["meets_criteria"].append(meets)
    
    return dict(by_disorder)


def print_analysis(stats, nodes_per_ep, edges_per_ep, entities_per_ep, edges_per_ep_detail):
    """Print the analysis results."""
    
    print("=" * 70)
    print("  KNOWLEDGE GRAPH ANALYSIS: Disorder Pattern Comparison")
    print("=" * 70)
    
    # Overall stats
    print(f"""
OVERALL GRAPH STATISTICS:
  Total Entities: {stats['total_nodes']}
  Total Relationships: {stats['total_edges']}
  Total Episodes (Conversations): {stats['total_episodes']}
""")
    
    # Per-episode stats
    print("-" * 70)
    print("PER-CONVERSATION METRICS:")
    print("-" * 70)
    print(f"{'Conversation':<35} {'Disorder':<12} {'Meets':<8} {'Nodes':<8} {'Edges':<8}")
    print("-" * 70)
    
    for episode in sorted(CONVERSATION_DISORDERS.keys()):
        disorder, meets = CONVERSATION_DISORDERS[episode]
        nodes = nodes_per_ep.get(episode, 0)
        edges = edges_per_ep.get(episode, 0)
        meets_str = "Yes" if meets else "No"
        print(f"{episode:<35} {disorder:<12} {meets_str:<8} {nodes:<8} {edges:<8}")
    
    # Aggregate by disorder
    print("\n" + "-" * 70)
    print("AGGREGATED BY DISORDER:")
    print("-" * 70)
    
    by_disorder = analyze_by_disorder(nodes_per_ep, edges_per_ep, entities_per_ep)
    
    for disorder, data in by_disorder.items():
        avg_nodes = sum(data["node_counts"]) / len(data["node_counts"]) if data["node_counts"] else 0
        avg_edges = sum(data["edge_counts"]) / len(data["edge_counts"]) if data["edge_counts"] else 0
        
        # Calculate density (edges / possible edges)
        # For a directed graph: possible edges = n * (n-1)
        densities = []
        for i, nc in enumerate(data["node_counts"]):
            ec = data["edge_counts"][i]
            if nc > 1:
                possible = nc * (nc - 1)
                density = ec / possible if possible > 0 else 0
                densities.append(density)
        avg_density = sum(densities) / len(densities) if densities else 0
        
        meets_count = sum(1 for m in data["meets_criteria"] if m)
        total_count = len(data["meets_criteria"])
        
        print(f"""
{disorder}:
  Conversations: {total_count} ({meets_count} meet criteria, {total_count - meets_count} subthreshold)
  Average Nodes: {avg_nodes:.1f}
  Average Edges: {avg_edges:.1f}
  Average Density: {avg_density:.3f}
  Unique Entities: {len(data['all_entities'])}
""")
    
    # Sample entities by disorder
    print("-" * 70)
    print("SAMPLE ENTITIES BY DISORDER:")
    print("-" * 70)
    
    for disorder, data in by_disorder.items():
        entities = list(data["all_entities"])[:10]  # First 10
        print(f"\n{disorder}:")
        for e in entities:
            print(f"  - {e}")
    
    # Sample relationships
    print("\n" + "-" * 70)
    print("SAMPLE RELATIONSHIPS BY DISORDER:")
    print("-" * 70)
    
    for disorder in by_disorder.keys():
        print(f"\n{disorder}:")
        # Get first episode for this disorder
        for episode, (ep_disorder, _) in CONVERSATION_DISORDERS.items():
            if ep_disorder == disorder and episode in edges_per_ep_detail:
                edges = edges_per_ep_detail[episode][:5]  # First 5 relationships
                for edge in edges:
                    fact = edge['fact'][:80] + "..." if len(edge['fact'] or '') > 80 else edge['fact']
                    print(f"  {edge['from']} -> {edge['to']}")
                    print(f"    \"{fact}\"")
                break
    
    # Key observations
    print("\n" + "=" * 70)
    print("KEY OBSERVATIONS:")
    print("=" * 70)
    print("""
Compare these metrics across disorders to identify distinguishing patterns:

1. NODE COUNT: Do some disorders produce more entities?
   - GAD may have many worry-related nodes (topics of concern)
   - ADHD may have symptom nodes across inattention + hyperactivity
   - Wernicke's may have fewer coherent entities

2. EDGE DENSITY: How interconnected are the entities?
   - Higher density = more relationships extracted
   - Wernicke's may have lower density (less coherent speech)

3. ENTITY TYPES: What kinds of things are extracted?
   - GAD: worry topics, physical symptoms, time references
   - ADHD: attention symptoms, hyperactivity symptoms, settings
   - Wernicke's: potentially nonsensical or fragmented entities

4. MEETS CRITERIA: Do threshold vs subthreshold cases differ?
   - Compare metrics for meets_criteria=True vs False
   
NEXT STEPS:
- Visualize in Neo4j: MATCH (n)-[r]->(m) RETURN n, r, m
- Filter by episode: MATCH (e:Episodic {name: 'gad_sarah_001'})-[:MENTIONS]->(n) RETURN n
- Compare specific conversations in the browser
""")


def main():
    """Run the analysis."""
    print("\nConnecting to Neo4j...")
    driver = get_driver()
    
    try:
        # Test connection
        with driver.session() as session:
            session.run("RETURN 1")
        print("Connected!\n")
        
        # Gather data
        stats = get_graph_stats(driver)
        nodes_per_ep = get_nodes_per_episode(driver)
        edges_per_ep = get_edges_per_episode(driver)
        entities_per_ep = get_entity_names_per_episode(driver)
        edges_detail = get_relationship_facts_per_episode(driver)
        
        # Check if we have data
        if stats["total_nodes"] == 0:
            print("No data found in the graph!")
            print("Run 'python load_empirical.py' first to load conversations.")
            return
        
        # Print analysis
        print_analysis(stats, nodes_per_ep, edges_per_ep, entities_per_ep, edges_detail)
        
    finally:
        driver.close()


if __name__ == "__main__":
    main()
