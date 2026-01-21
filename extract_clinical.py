"""
Clinical Entity Extraction for Mental Health Knowledge Graphs

This script extracts clinical and semantic entities from interview transcripts
using direct LLM calls (no Graphiti), then stores them in Neo4j.

Features:
    - Dual entity extraction (clinical vs semantic)
    - Embedding-based entity resolution (merges similar entities)
    - Relationship extraction

Usage:
    python extract_clinical.py                    # List available conversations
    python extract_clinical.py <name>             # Extract from specific conversation
    python extract_clinical.py all                # Extract from all conversations

Entity Types:
    CLINICAL: symptoms, DSM criteria, medications, treatments, triggers
    SEMANTIC: people, places, objects, topics, abstract concepts
"""

import json
import os
import sys
import requests
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()

# Entity resolution model (loaded lazily)
_embedding_model = None

def get_embedding_model():
    """Lazy load the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        print("  Loading embedding model for entity resolution...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

# Import conversation data
from empirical_conversations import CONVERSATIONS

CONVERSATIONS_BY_NAME = {conv['name']: conv for conv in CONVERSATIONS}

# Extraction prompt
EXTRACTION_PROMPT = """You are a clinical entity extractor. Analyze this mental health interview transcript and extract entities and relationships.

EXTRACT TWO TYPES OF ENTITIES:

1. CLINICAL ENTITIES (mental health specific):
   - Symptoms: anxiety, worry, depression, fatigue, sleep problems, attention issues, restlessness, irritability, muscle tension, hyperactivity, fidgeting, etc.
   - DSM Criteria: duration mentions ("6 months", "since March"), frequency ("more days than not", "every day"), impairment domains (work, school, home, social)
   - Treatments: medications (sertraline, bupropion), therapy types (CBT), coping strategies (meditation, breathing exercises)
   - Triggers: job loss, stress, life events that cause symptoms

2. SEMANTIC ENTITIES (general concepts mentioned):
   - People: patient name, clinician name, family members, friends
   - Places/Settings: school, work, home, clinic
   - Objects: anything physical mentioned
   - Topics: abstract concepts, activities discussed

EXTRACT RELATIONSHIPS between entities:
   - HAS_SYMPTOM: patient experiences a symptom
   - TRIGGERS: something causes/triggers a symptom
   - TREATS: treatment addresses a symptom
   - DURATION: how long something has lasted
   - AFFECTS: symptom affects a domain (work, home, etc.)
   - SUPPORTS: person supports patient
   - PRESCRIBES: clinician prescribes treatment

Return ONLY valid JSON in this exact format (no other text):
{{
  "clinical_entities": [
    {{"name": "entity name", "type": "symptom|criterion|treatment|trigger"}}
  ],
  "semantic_entities": [
    {{"name": "entity name", "type": "person|place|object|topic"}}
  ],
  "relationships": [
    {{"from": "entity name", "to": "entity name", "type": "relationship type", "description": "brief description"}}
  ]
}}

INTERVIEW TRANSCRIPT:
{transcript}

JSON OUTPUT:"""


def get_neo4j_driver():
    """Create Neo4j driver."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def normalize_entity_name(name):
    """Basic normalization: lowercase, strip whitespace."""
    if not name:
        return name
    return name.lower().strip()


def resolve_entities(entities, similarity_threshold=0.85):
    """
    Resolve similar entities using embedding similarity.
    
    Returns a mapping from original names to canonical names,
    and the deduplicated entity list.
    """
    if not entities or len(entities) < 2:
        return {e['name']: e['name'] for e in entities}, entities
    
    model = get_embedding_model()
    
    # Get unique names
    names = [e['name'] for e in entities]
    unique_names = list(set(names))
    
    if len(unique_names) < 2:
        return {name: name for name in names}, entities
    
    # Compute embeddings
    embeddings = model.encode(unique_names)
    
    # Compute similarity matrix
    sim_matrix = cosine_similarity(embeddings)
    
    # Find clusters of similar entities
    # Use simple greedy clustering: first entity becomes canonical
    canonical_map = {}  # original -> canonical
    processed = set()
    
    for i, name_i in enumerate(unique_names):
        if name_i in processed:
            continue
            
        # This becomes a canonical name
        canonical = name_i
        canonical_map[name_i] = canonical
        processed.add(name_i)
        
        # Find all similar names
        for j, name_j in enumerate(unique_names):
            if name_j in processed:
                continue
            if sim_matrix[i][j] >= similarity_threshold:
                # Prefer shorter name as canonical, or lowercase
                if len(name_j) < len(canonical):
                    # Update canonical
                    old_canonical = canonical
                    canonical = name_j
                    # Remap previous entries
                    for k, v in canonical_map.items():
                        if v == old_canonical:
                            canonical_map[k] = canonical
                
                canonical_map[name_j] = canonical
                processed.add(name_j)
    
    # Build deduplicated entity list
    seen_canonical = set()
    resolved_entities = []
    
    for entity in entities:
        canonical_name = canonical_map.get(entity['name'], entity['name'])
        if canonical_name not in seen_canonical:
            resolved_entity = entity.copy()
            resolved_entity['name'] = canonical_name
            resolved_entity['original_names'] = [entity['name']]
            resolved_entities.append(resolved_entity)
            seen_canonical.add(canonical_name)
        else:
            # Add to original_names for tracking
            for re in resolved_entities:
                if re['name'] == canonical_name:
                    if entity['name'] not in re.get('original_names', []):
                        re['original_names'].append(entity['name'])
                    break
    
    return canonical_map, resolved_entities


def resolve_extraction_result(result):
    """
    Apply entity resolution to an extraction result.
    Updates entity names and relationship references.
    """
    clinical_entities = result.get("clinical_entities", [])
    semantic_entities = result.get("semantic_entities", [])
    relationships = result.get("relationships", [])
    
    # Resolve clinical entities
    clinical_map, resolved_clinical = resolve_entities(clinical_entities)
    
    # Resolve semantic entities  
    semantic_map, resolved_semantic = resolve_entities(semantic_entities)
    
    # Combine maps for relationship resolution
    full_map = {**clinical_map, **semantic_map}
    
    # Update relationship references
    resolved_relationships = []
    for rel in relationships:
        resolved_rel = rel.copy()
        from_name = rel.get('from', '')
        to_name = rel.get('to', '')
        
        # Try to resolve names (check both maps)
        resolved_rel['from'] = full_map.get(from_name, from_name)
        resolved_rel['to'] = full_map.get(to_name, to_name)
        
        resolved_relationships.append(resolved_rel)
    
    # Count merges for reporting
    clinical_merges = len(clinical_entities) - len(resolved_clinical)
    semantic_merges = len(semantic_entities) - len(resolved_semantic)
    
    return {
        "clinical_entities": resolved_clinical,
        "semantic_entities": resolved_semantic,
        "relationships": resolved_relationships,
        "resolution_stats": {
            "clinical_before": len(clinical_entities),
            "clinical_after": len(resolved_clinical),
            "clinical_merged": clinical_merges,
            "semantic_before": len(semantic_entities),
            "semantic_after": len(resolved_semantic),
            "semantic_merged": semantic_merges
        }
    }


def extract_entities_llm(transcript):
    """Use Ollama to extract entities from transcript."""
    prompt = EXTRACTION_PROMPT.format(transcript=transcript)
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2000
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()
            
            # Try to parse JSON from response
            # Sometimes LLM adds extra text, try to find JSON block
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                print(f"  Warning: Could not find JSON in response")
                return None
        else:
            print(f"  Error: Ollama returned status {response.status_code}")
            return None
            
    except json.JSONDecodeError as e:
        print(f"  Error parsing JSON: {e}")
        return None
    except requests.exceptions.Timeout:
        print("  Error: Ollama timeout")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def store_in_neo4j(driver, episode_name, diagnosis, meets_criteria, extraction_result):
    """Store extracted entities and relationships in Neo4j."""
    
    clinical_entities = extraction_result.get("clinical_entities", [])
    semantic_entities = extraction_result.get("semantic_entities", [])
    relationships = extraction_result.get("relationships", [])
    
    with driver.session() as session:
        # Create Episode node
        session.run("""
            MERGE (e:Episode {name: $name})
            SET e.diagnosis = $diagnosis,
                e.meets_criteria = $meets_criteria
        """, name=episode_name, diagnosis=diagnosis, meets_criteria=meets_criteria)
        
        # Create Clinical entities
        for entity in clinical_entities:
            if entity.get("name"):
                session.run("""
                    MERGE (n:Entity:Clinical {name: $name, episode: $episode})
                    SET n.type = $type
                """, name=entity["name"], episode=episode_name, type=entity.get("type", "unknown"))
                
                # Link to episode
                session.run("""
                    MATCH (e:Episode {name: $episode})
                    MATCH (n:Entity:Clinical {name: $name, episode: $episode})
                    MERGE (e)-[:MENTIONS]->(n)
                """, episode=episode_name, name=entity["name"])
        
        # Create Semantic entities
        for entity in semantic_entities:
            if entity.get("name"):
                session.run("""
                    MERGE (n:Entity:Semantic {name: $name, episode: $episode})
                    SET n.type = $type
                """, name=entity["name"], episode=episode_name, type=entity.get("type", "unknown"))
                
                # Link to episode
                session.run("""
                    MATCH (e:Episode {name: $episode})
                    MATCH (n:Entity:Semantic {name: $name, episode: $episode})
                    MERGE (e)-[:MENTIONS]->(n)
                """, episode=episode_name, name=entity["name"])
        
        # Create relationships between entities
        for rel in relationships:
            from_name = rel.get("from")
            to_name = rel.get("to")
            rel_type = rel.get("type", "RELATES_TO").upper().replace(" ", "_")
            description = rel.get("description", "")
            
            if from_name and to_name:
                # Try to find entities (could be clinical or semantic)
                session.run(f"""
                    MATCH (a:Entity {{name: $from_name, episode: $episode}})
                    MATCH (b:Entity {{name: $to_name, episode: $episode}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r.description = $description
                """, from_name=from_name, to_name=to_name, episode=episode_name, description=description)
    
    return len(clinical_entities), len(semantic_entities), len(relationships)


def list_conversations():
    """List available conversations."""
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
    print("  python extract_clinical.py <name>    # Extract from specific conversation")
    print("  python extract_clinical.py all       # Extract from all conversations")
    print()


def extract_single(conv):
    """Extract entities from a single conversation."""
    diagnosis = conv.get('diagnosis', 'Unknown')
    meets = conv.get('meets_criteria', None)
    meets_str = "meets criteria" if meets else "subthreshold" if meets is False else ""
    
    print("=" * 65)
    print(f"  Extracting: {conv['name']}")
    print(f"  {diagnosis} ({meets_str})")
    print("=" * 65)
    
    # Connect to Neo4j
    print("\n[1/4] Connecting to Neo4j...")
    driver = get_neo4j_driver()
    print("      Connected")
    
    # Extract entities using LLM
    print("\n[2/4] Extracting entities with LLM...")
    result = extract_entities_llm(conv['content'])
    
    if result is None:
        print("      Extraction failed!")
        driver.close()
        return
    
    clinical_count = len(result.get("clinical_entities", []))
    semantic_count = len(result.get("semantic_entities", []))
    rel_count = len(result.get("relationships", []))
    print(f"      Found: {clinical_count} clinical, {semantic_count} semantic, {rel_count} relationships")
    
    # Entity resolution
    print("\n[3/4] Resolving similar entities...")
    result = resolve_extraction_result(result)
    stats = result.get("resolution_stats", {})
    
    if stats.get("clinical_merged", 0) > 0 or stats.get("semantic_merged", 0) > 0:
        print(f"      Merged: {stats.get('clinical_merged', 0)} clinical, {stats.get('semantic_merged', 0)} semantic")
        print(f"      After:  {stats.get('clinical_after', 0)} clinical, {stats.get('semantic_after', 0)} semantic")
    else:
        print("      No duplicates found")
    
    # Store in Neo4j
    print("\n[4/4] Storing in Neo4j...")
    store_in_neo4j(driver, conv['name'], diagnosis, meets, result)
    print("      Done!")
    
    driver.close()
    
    print("\n" + "=" * 65)
    print(f"  COMPLETE: {conv['name']}")
    print("=" * 65)
    
    # Print extracted entities
    print("\nCLINICAL ENTITIES:")
    for e in result.get("clinical_entities", []):
        print(f"  - {e.get('name')} ({e.get('type')})")
    
    print("\nSEMANTIC ENTITIES:")
    for e in result.get("semantic_entities", []):
        print(f"  - {e.get('name')} ({e.get('type')})")
    
    print("\nRELATIONSHIPS:")
    for r in result.get("relationships", [])[:10]:  # First 10
        print(f"  - {r.get('from')} --{r.get('type')}--> {r.get('to')}")
    if len(result.get("relationships", [])) > 10:
        print(f"  ... and {len(result.get('relationships', [])) - 10} more")
    print()


def extract_all():
    """Extract entities from all conversations."""
    print("=" * 65)
    print("  Extracting from All Conversations (with Entity Resolution)")
    print("=" * 65)
    
    driver = get_neo4j_driver()
    
    # Pre-load embedding model once
    print("\nLoading embedding model...")
    get_embedding_model()
    print("Ready!\n")
    
    results = []
    total_merged = {"clinical": 0, "semantic": 0}
    
    for i, conv in enumerate(CONVERSATIONS):
        diagnosis = conv.get('diagnosis', 'Unknown')
        meets = conv.get('meets_criteria', None)
        meets_str = "meets criteria" if meets else "subthreshold" if meets is False else ""
        
        print(f"[{i+1}/{len(CONVERSATIONS)}] {conv['name']}")
        print(f"    {diagnosis} ({meets_str})")
        
        result = extract_entities_llm(conv['content'])
        
        if result:
            # Apply entity resolution
            result = resolve_extraction_result(result)
            stats = result.get("resolution_stats", {})
            
            clinical_count, semantic_count, rel_count = store_in_neo4j(
                driver, conv['name'], diagnosis, meets, result
            )
            
            merged_info = ""
            if stats.get("clinical_merged", 0) > 0 or stats.get("semantic_merged", 0) > 0:
                merged_info = f" (merged: {stats.get('clinical_merged', 0)}c, {stats.get('semantic_merged', 0)}s)"
                total_merged["clinical"] += stats.get("clinical_merged", 0)
                total_merged["semantic"] += stats.get("semantic_merged", 0)
            
            print(f"    Extracted: {clinical_count} clinical, {semantic_count} semantic, {rel_count} rels{merged_info}")
            results.append({
                "name": conv['name'],
                "clinical": clinical_count,
                "semantic": semantic_count,
                "relationships": rel_count
            })
        else:
            print("    FAILED")
            results.append({"name": conv['name'], "clinical": 0, "semantic": 0, "relationships": 0})
    
    driver.close()
    
    # Summary
    print("\n" + "=" * 65)
    print("  EXTRACTION COMPLETE")
    print("=" * 65)
    print(f"\n{'Conversation':<35} {'Clinical':<10} {'Semantic':<10} {'Rels':<10}")
    print("-" * 65)
    for r in results:
        print(f"{r['name']:<35} {r['clinical']:<10} {r['semantic']:<10} {r['relationships']:<10}")
    
    total_clinical = sum(r['clinical'] for r in results)
    total_semantic = sum(r['semantic'] for r in results)
    total_rels = sum(r['relationships'] for r in results)
    print("-" * 65)
    print(f"{'TOTAL':<35} {total_clinical:<10} {total_semantic:<10} {total_rels:<10}")
    
    if total_merged["clinical"] > 0 or total_merged["semantic"] > 0:
        print(f"\nEntity Resolution: merged {total_merged['clinical']} clinical + {total_merged['semantic']} semantic duplicates")
    print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        list_conversations()
        return
    
    arg = sys.argv[1]
    
    if arg == "all":
        extract_all()
    elif arg in CONVERSATIONS_BY_NAME:
        extract_single(CONVERSATIONS_BY_NAME[arg])
    else:
        print(f"Unknown conversation: {arg}")
        print()
        list_conversations()


if __name__ == "__main__":
    main()
