"""
Analyze knowledge graph patterns across different disorders.

This script queries the Neo4j graph to extract structural features
that may differentiate between GAD, ADHD, and Wernicke's Aphasia.

Usage:
    python analyze_graphs.py

The analysis compares:
- Clinical vs Semantic entity counts
- Clinical ratio (clinical / total entities)
- Edge density and connectivity
- Entity patterns by disorder type
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
CONVERSATION_DISORDERS = {
    "gad_sarah_001": ("GAD", True),
    "gad_sarah_002": ("GAD", True),
    "gad_sarah_003": ("GAD", False),
    "adhd_elise_001": ("ADHD", False),
    "adhd_elise_002": ("ADHD", True),
    "adhd_elise_003": ("ADHD", True),
    "wernickes_aphasia_byron_001": ("Wernicke's Aphasia", True),
}


def get_driver():
    """Create Neo4j driver."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_overall_stats(driver):
    """Get overall graph statistics."""
    with driver.session() as session:
        # Total entities
        result = session.run("MATCH (n:Entity) RETURN count(n) as count")
        total_entities = result.single()["count"]
        
        # Clinical entities
        result = session.run("MATCH (n:Clinical) RETURN count(n) as count")
        clinical_count = result.single()["count"]
        
        # Semantic entities
        result = session.run("MATCH (n:Semantic) RETURN count(n) as count")
        semantic_count = result.single()["count"]
        
        # Total relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        total_rels = result.single()["count"]
        
        # Episodes
        result = session.run("MATCH (e:Episode) RETURN count(e) as count")
        episode_count = result.single()["count"]
        
        return {
            "total_entities": total_entities,
            "clinical_entities": clinical_count,
            "semantic_entities": semantic_count,
            "total_relationships": total_rels,
            "episodes": episode_count
        }


def get_entities_per_episode(driver):
    """Get clinical and semantic entity counts per episode with density breakdown."""
    results = {}
    
    with driver.session() as session:
        # Get all episodes
        episodes = session.run("MATCH (e:Episode) RETURN e.name as name")
        episode_names = [r["name"] for r in episodes]
        
        for ep_name in episode_names:
            # Clinical count
            result = session.run("""
                MATCH (e:Episode {name: $name})-[:MENTIONS]->(n:Clinical)
                RETURN count(n) as count
            """, name=ep_name)
            clinical = result.single()["count"]
            
            # Semantic count
            result = session.run("""
                MATCH (e:Episode {name: $name})-[:MENTIONS]->(n:Semantic)
                RETURN count(n) as count
            """, name=ep_name)
            semantic = result.single()["count"]
            
            # Clinical-to-Clinical relationships
            result = session.run("""
                MATCH (e:Episode {name: $name})-[:MENTIONS]->(n1:Clinical)
                MATCH (e)-[:MENTIONS]->(n2:Clinical)
                MATCH (n1)-[r]->(n2)
                WHERE n1 <> n2 AND NOT type(r) = 'MENTIONS'
                RETURN count(DISTINCT r) as count
            """, name=ep_name)
            clinical_rels = result.single()["count"]
            
            # Semantic-to-Semantic relationships
            result = session.run("""
                MATCH (e:Episode {name: $name})-[:MENTIONS]->(n1:Semantic)
                MATCH (e)-[:MENTIONS]->(n2:Semantic)
                MATCH (n1)-[r]->(n2)
                WHERE n1 <> n2 AND NOT type(r) = 'MENTIONS'
                RETURN count(DISTINCT r) as count
            """, name=ep_name)
            semantic_rels = result.single()["count"]
            
            # Cross-type relationships (Clinical <-> Semantic)
            result = session.run("""
                MATCH (e:Episode {name: $name})-[:MENTIONS]->(n1:Clinical)
                MATCH (e)-[:MENTIONS]->(n2:Semantic)
                MATCH (n1)-[r]-(n2)
                WHERE NOT type(r) = 'MENTIONS'
                RETURN count(DISTINCT r) as count
            """, name=ep_name)
            cross_rels = result.single()["count"]
            
            # Total relationship count
            total_rels = clinical_rels + semantic_rels + cross_rels
            
            # Calculate densities
            # Clinical density: edges / possible edges within clinical nodes
            clinical_density = 0
            if clinical > 1:
                possible_clinical = clinical * (clinical - 1)
                clinical_density = clinical_rels / possible_clinical if possible_clinical > 0 else 0
            
            # Semantic density: edges / possible edges within semantic nodes
            semantic_density = 0
            if semantic > 1:
                possible_semantic = semantic * (semantic - 1)
                semantic_density = semantic_rels / possible_semantic if possible_semantic > 0 else 0
            
            # Cross-type density: cross edges / possible cross edges
            cross_density = 0
            if clinical > 0 and semantic > 0:
                possible_cross = clinical * semantic * 2  # bidirectional
                cross_density = cross_rels / possible_cross if possible_cross > 0 else 0
            
            # Overall density
            total_nodes = clinical + semantic
            overall_density = 0
            if total_nodes > 1:
                possible_total = total_nodes * (total_nodes - 1)
                overall_density = total_rels / possible_total if possible_total > 0 else 0
            
            results[ep_name] = {
                "clinical": clinical,
                "semantic": semantic,
                "total": clinical + semantic,
                "relationships": total_rels,
                "clinical_rels": clinical_rels,
                "semantic_rels": semantic_rels,
                "cross_rels": cross_rels,
                "clinical_density": clinical_density,
                "semantic_density": semantic_density,
                "cross_density": cross_density,
                "overall_density": overall_density
            }
    
    return results


def get_clinical_entities_by_episode(driver):
    """Get list of clinical entity names per episode."""
    results = {}
    
    with driver.session() as session:
        query = """
        MATCH (e:Episode)-[:MENTIONS]->(n:Clinical)
        RETURN e.name as episode, collect(n.name) as entities, collect(n.type) as types
        """
        result = session.run(query)
        for r in result:
            results[r["episode"]] = list(zip(r["entities"], r["types"]))
    
    return results


def get_semantic_entities_by_episode(driver):
    """Get list of semantic entity names per episode."""
    results = {}
    
    with driver.session() as session:
        query = """
        MATCH (e:Episode)-[:MENTIONS]->(n:Semantic)
        RETURN e.name as episode, collect(n.name) as entities, collect(n.type) as types
        """
        result = session.run(query)
        for r in result:
            results[r["episode"]] = list(zip(r["entities"], r["types"]))
    
    return results


def get_relationships_by_episode(driver):
    """Get relationships for each episode."""
    results = {}
    
    with driver.session() as session:
        query = """
        MATCH (e:Episode)-[:MENTIONS]->(n1:Entity)
        MATCH (e)-[:MENTIONS]->(n2:Entity)
        MATCH (n1)-[r]->(n2)
        WHERE n1 <> n2 AND NOT type(r) = 'MENTIONS'
        RETURN e.name as episode, n1.name as from_node, n2.name as to_node, 
               type(r) as rel_type, r.description as description
        """
        result = session.run(query)
        for r in result:
            ep = r["episode"]
            if ep not in results:
                results[ep] = []
            results[ep].append({
                "from": r["from_node"],
                "to": r["to_node"],
                "type": r["rel_type"],
                "description": r["description"]
            })
    
    return results


def analyze_by_disorder(entities_per_ep):
    """Aggregate metrics by disorder type."""
    by_disorder = defaultdict(lambda: {
        "episodes": [],
        "clinical_counts": [],
        "semantic_counts": [],
        "total_counts": [],
        "relationship_counts": [],
        "clinical_densities": [],
        "semantic_densities": [],
        "cross_densities": [],
        "overall_densities": [],
        "meets_criteria": []
    })
    
    default_ep = {
        "clinical": 0, "semantic": 0, "total": 0, "relationships": 0,
        "clinical_density": 0, "semantic_density": 0, "cross_density": 0, "overall_density": 0
    }
    
    for episode, disorder_info in CONVERSATION_DISORDERS.items():
        disorder, meets = disorder_info
        
        ep_data = entities_per_ep.get(episode, default_ep)
        
        by_disorder[disorder]["episodes"].append(episode)
        by_disorder[disorder]["clinical_counts"].append(ep_data["clinical"])
        by_disorder[disorder]["semantic_counts"].append(ep_data["semantic"])
        by_disorder[disorder]["total_counts"].append(ep_data["total"])
        by_disorder[disorder]["relationship_counts"].append(ep_data["relationships"])
        by_disorder[disorder]["clinical_densities"].append(ep_data.get("clinical_density", 0))
        by_disorder[disorder]["semantic_densities"].append(ep_data.get("semantic_density", 0))
        by_disorder[disorder]["cross_densities"].append(ep_data.get("cross_density", 0))
        by_disorder[disorder]["overall_densities"].append(ep_data.get("overall_density", 0))
        by_disorder[disorder]["meets_criteria"].append(meets)
    
    return dict(by_disorder)


def print_analysis(overall, entities_per_ep, clinical_by_ep, semantic_by_ep, rels_by_ep):
    """Print the analysis results."""
    
    print("=" * 75)
    print("  CLINICAL KNOWLEDGE GRAPH ANALYSIS")
    print("  Comparing Clinical vs Semantic Entities by Disorder")
    print("=" * 75)
    
    # Overall stats
    clinical_ratio = overall['clinical_entities'] / overall['total_entities'] if overall['total_entities'] > 0 else 0
    print(f"""
OVERALL STATISTICS:
  Total Entities: {overall['total_entities']}
    - Clinical: {overall['clinical_entities']} ({clinical_ratio:.1%})
    - Semantic: {overall['semantic_entities']} ({1-clinical_ratio:.1%})
  Total Relationships: {overall['total_relationships']}
  Episodes: {overall['episodes']}
""")
    
    # Per-episode table
    print("-" * 75)
    print("PER-CONVERSATION METRICS:")
    print("-" * 75)
    print(f"{'Conversation':<32} {'Disorder':<10} {'Clinical':<10} {'Semantic':<10} {'Ratio':<10} {'Rels':<8}")
    print("-" * 75)
    
    for episode in sorted(CONVERSATION_DISORDERS.keys()):
        disorder, meets = CONVERSATION_DISORDERS[episode]
        ep_data = entities_per_ep.get(episode, {"clinical": 0, "semantic": 0, "total": 0, "relationships": 0})
        
        total = ep_data["clinical"] + ep_data["semantic"]
        ratio = ep_data["clinical"] / total if total > 0 else 0
        ratio_str = f"{ratio:.0%}"
        
        meets_marker = "*" if meets else ""
        print(f"{episode:<32} {disorder:<10} {ep_data['clinical']:<10} {ep_data['semantic']:<10} {ratio_str:<10} {ep_data['relationships']:<8}{meets_marker}")
    
    print("\n  * = meets diagnostic criteria")
    
    # Aggregate by disorder
    print("\n" + "-" * 75)
    print("AGGREGATED BY DISORDER:")
    print("-" * 75)
    
    by_disorder = analyze_by_disorder(entities_per_ep)
    
    for disorder, data in by_disorder.items():
        avg_clinical = sum(data["clinical_counts"]) / len(data["clinical_counts"]) if data["clinical_counts"] else 0
        avg_semantic = sum(data["semantic_counts"]) / len(data["semantic_counts"]) if data["semantic_counts"] else 0
        avg_total = avg_clinical + avg_semantic
        avg_ratio = avg_clinical / avg_total if avg_total > 0 else 0
        avg_rels = sum(data["relationship_counts"]) / len(data["relationship_counts"]) if data["relationship_counts"] else 0
        
        # Density by type (use stored values)
        avg_clinical_density = sum(data["clinical_densities"]) / len(data["clinical_densities"]) if data["clinical_densities"] else 0
        avg_semantic_density = sum(data["semantic_densities"]) / len(data["semantic_densities"]) if data["semantic_densities"] else 0
        avg_cross_density = sum(data["cross_densities"]) / len(data["cross_densities"]) if data["cross_densities"] else 0
        avg_overall_density = sum(data["overall_densities"]) / len(data["overall_densities"]) if data["overall_densities"] else 0
        
        meets_count = sum(1 for m in data["meets_criteria"] if m)
        total_count = len(data["meets_criteria"])
        
        print(f"""
{disorder}:
  Conversations: {total_count} ({meets_count} meet criteria)
  Avg Clinical Entities: {avg_clinical:.1f}
  Avg Semantic Entities: {avg_semantic:.1f}
  Avg Clinical Ratio: {avg_ratio:.1%}
  Avg Relationships: {avg_rels:.1f}
  
  Density by Entity Type:
    Clinical-to-Clinical: {avg_clinical_density:.3f}
    Semantic-to-Semantic: {avg_semantic_density:.3f}
    Cross-type (Clin<->Sem): {avg_cross_density:.3f}
    Overall: {avg_overall_density:.3f}
""")
    
    # Clinical entities by disorder
    print("-" * 75)
    print("CLINICAL ENTITIES BY DISORDER:")
    print("-" * 75)
    
    for disorder in by_disorder.keys():
        print(f"\n{disorder}:")
        all_clinical = set()
        for episode, (ep_disorder, _) in CONVERSATION_DISORDERS.items():
            if ep_disorder == disorder and episode in clinical_by_ep:
                for name, etype in clinical_by_ep[episode]:
                    all_clinical.add((name, etype))
        
        for name, etype in sorted(all_clinical)[:15]:
            print(f"  - {name} ({etype})")
        if len(all_clinical) > 15:
            print(f"  ... and {len(all_clinical) - 15} more")
    
    # Semantic entities by disorder
    print("\n" + "-" * 75)
    print("SEMANTIC ENTITIES BY DISORDER:")
    print("-" * 75)
    
    for disorder in by_disorder.keys():
        print(f"\n{disorder}:")
        all_semantic = set()
        for episode, (ep_disorder, _) in CONVERSATION_DISORDERS.items():
            if ep_disorder == disorder and episode in semantic_by_ep:
                for name, etype in semantic_by_ep[episode]:
                    all_semantic.add((name, etype))
        
        for name, etype in sorted(all_semantic)[:10]:
            print(f"  - {name} ({etype})")
        if len(all_semantic) > 10:
            print(f"  ... and {len(all_semantic) - 10} more")
    
    # Sample relationships
    print("\n" + "-" * 75)
    print("SAMPLE RELATIONSHIPS BY DISORDER:")
    print("-" * 75)
    
    for disorder in by_disorder.keys():
        print(f"\n{disorder}:")
        for episode, (ep_disorder, _) in CONVERSATION_DISORDERS.items():
            if ep_disorder == disorder and episode in rels_by_ep:
                for rel in rels_by_ep[episode][:5]:
                    desc = rel['description'][:50] + "..." if rel['description'] and len(rel['description']) > 50 else rel['description']
                    print(f"  {rel['from']} --[{rel['type']}]--> {rel['to']}")
                    if desc:
                        print(f"      \"{desc}\"")
                break
    
    # Key findings
    print("\n" + "=" * 75)
    print("KEY METRICS FOR DISORDER DIFFERENTIATION:")
    print("=" * 75)
    
    # Calculate summary stats
    summary = {}
    for disorder, data in by_disorder.items():
        avg_clinical = sum(data["clinical_counts"]) / len(data["clinical_counts"]) if data["clinical_counts"] else 0
        avg_semantic = sum(data["semantic_counts"]) / len(data["semantic_counts"]) if data["semantic_counts"] else 0
        avg_total = avg_clinical + avg_semantic
        avg_ratio = avg_clinical / avg_total if avg_total > 0 else 0
        avg_clin_dens = sum(data["clinical_densities"]) / len(data["clinical_densities"]) if data["clinical_densities"] else 0
        avg_sem_dens = sum(data["semantic_densities"]) / len(data["semantic_densities"]) if data["semantic_densities"] else 0
        avg_cross_dens = sum(data["cross_densities"]) / len(data["cross_densities"]) if data["cross_densities"] else 0
        summary[disorder] = {
            "clinical": avg_clinical, "semantic": avg_semantic, "ratio": avg_ratio,
            "clin_dens": avg_clin_dens, "sem_dens": avg_sem_dens, "cross_dens": avg_cross_dens
        }
    
    print("""
NODE COUNTS:
                        Clinical   Semantic   Clinical Ratio
                        Nodes      Nodes      (higher = more clinical)
  -------------------------------------------------------------""")
    for disorder, s in summary.items():
        print(f"  {disorder:<20} {s['clinical']:>6.1f}     {s['semantic']:>6.1f}       {s['ratio']:>6.1%}")
    
    print("""

DENSITY BY CONNECTION TYPE:
                        Clinical   Semantic   Cross-type
                        Density    Density    Density
  -------------------------------------------------------------""")
    for disorder, s in summary.items():
        print(f"  {disorder:<20} {s['clin_dens']:>6.3f}     {s['sem_dens']:>6.3f}       {s['cross_dens']:>6.3f}")
    
    print("""
INTERPRETATION:
  Node Counts:
    - High clinical ratio = patient describing clear symptoms
    - Low clinical ratio = speech without clinical content (e.g., Wernicke's)
  
  Density:
    - Clinical density: how interconnected are the symptoms?
    - Semantic density: how connected are non-clinical topics?
    - Cross-type density: links between symptoms and contexts
    - Higher density = more relationships extracted per node
    - Wernicke's: expect low clinical density (few symptom connections)
""")


def main():
    """Run the analysis."""
    print("\nConnecting to Neo4j...")
    driver = get_driver()
    
    try:
        with driver.session() as session:
            session.run("RETURN 1")
        print("Connected!\n")
        
        # Gather data
        overall = get_overall_stats(driver)
        entities_per_ep = get_entities_per_episode(driver)
        clinical_by_ep = get_clinical_entities_by_episode(driver)
        semantic_by_ep = get_semantic_entities_by_episode(driver)
        rels_by_ep = get_relationships_by_episode(driver)
        
        if overall["total_entities"] == 0:
            print("No data found in the graph!")
            print("Run 'python extract_clinical.py all' first to extract entities.")
            return
        
        print_analysis(overall, entities_per_ep, clinical_by_ep, semantic_by_ep, rels_by_ep)
        
    finally:
        driver.close()


if __name__ == "__main__":
    main()
