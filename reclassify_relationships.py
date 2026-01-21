#!/usr/bin/env python3
"""
Relationship Reclassification Script

This script uses Ollama to classify generic RELATES_TO edges into 
domain-specific relationship types for mental health applications.

The original RELATES_TO edges are preserved - new typed edges are created alongside them.

Usage:
    python reclassify_relationships.py

Relationship Types:
    TREATS          - Provider treats patient
    PRESCRIBED      - Provider prescribed medication
    TAKES           - Patient takes medication
    REFERRED        - Provider referred to another provider
    SUPPORTS        - Person supports another
    FAMILY_OF       - Family relationship
    WORKS_AT        - Person works at organization
    DIAGNOSED_WITH  - Patient has condition
    TRIGGERS        - Something triggers a condition
    UNCERTAIN       - Doesn't fit categories (kept as RELATES_TO only)
"""

import os
import json
import requests
from collections import Counter
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# ===========================================
# Configuration
# ===========================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

# Valid relationship types for mental health domain
RELATIONSHIP_TYPES = [
    "TREATS",           # Provider treats patient
    "PRESCRIBED",       # Provider prescribed medication  
    "TAKES",            # Patient takes medication
    "REFERRED",         # Provider referred to another
    "SUPPORTS",         # Person supports another
    "FAMILY_OF",        # Family relationship
    "WORKS_AT",         # Person works at organization
    "DIAGNOSED_WITH",   # Patient has condition
    "TRIGGERS",         # Something triggers condition
    "UNCERTAIN",        # Doesn't clearly fit
]

# Entity type patterns for inference
ENTITY_TYPE_PATTERNS = {
    "MEDICATION": [
        "sertraline", "bupropion", "escitalopram", "venlafaxine", "melatonin",
        "medication", "drug", "prescription", "mg", "dose", "antidepressant",
        "ssri", "snri", "anxiolytic", "prescribed"
    ],
    "CONDITION": [
        "anxiety", "depression", "disorder", "insomnia", "ptsd", "ocd",
        "phobia", "panic", "symptom", "diagnosis", "syndrome"
    ],
    "PROVIDER": [
        "dr.", "dr ", "doctor", "therapist", "psychiatrist", "psychologist",
        "counselor", "nurse", "lcsw", "social worker", "clinician", "practitioner",
        "md", "phd", "np"
    ],
    "PATIENT": [
        "patient", "client"
    ],
    "ORGANIZATION": [
        "inc.", "inc", "corp", "corp.", "llc", "clinic", "hospital", "center",
        "systems", "solutions", "analytics", "association", "capital", "tech",
        "university", "hr"
    ],
    "ASSESSMENT": [
        "phq-9", "gad-7", "score", "assessment", "scale", "measure", "test"
    ],
    "THERAPY": [
        "cbt", "cognitive behavioral", "therapy", "treatment", "intervention"
    ],
    "APP": [
        "app", "calm", "headspace", "application"
    ]
}


def infer_entity_type(name, summary):
    """Infer entity type from name and summary using pattern matching.
    
    Priority order: Check name first, then summary. Some types take priority.
    """
    name_lower = name.lower()
    summary_lower = (summary or "").lower()
    
    # PRIORITY 1: Check name for definitive patterns
    # Patient - highest priority if name contains "patient"
    if "patient" in name_lower:
        return "PATIENT"
    
    # Medications - check name for known drug names
    medication_names = ["sertraline", "bupropion", "escitalopram", "venlafaxine", "melatonin", "prozac", "zoloft", "lexapro"]
    if any(med in name_lower for med in medication_names):
        return "MEDICATION"
    
    # Providers - check for Dr., MD, etc. in name
    if any(p in name_lower for p in ["dr.", "dr ", "md", "phd", "lcsw", "therapist", "nurse practitioner"]):
        return "PROVIDER"
    
    # PRIORITY 2: Check name for other patterns
    if any(p in name_lower for p in ["inc.", "inc", "corp", "llc", "systems", "solutions", "analytics", "capital", "association"]):
        return "ORGANIZATION"
    
    if any(p in name_lower for p in ["app", "calm"]):
        return "APP"
    
    if any(p in name_lower for p in ["cbt", "cognitive behavioral", "therapy"]):
        return "THERAPY"
    
    if any(p in name_lower for p in ["phq", "gad-", "score", "assessment"]):
        return "ASSESSMENT"
    
    if any(p in name_lower for p in ["anxiety", "depression", "disorder", "insomnia"]):
        return "CONDITION"
    
    # PRIORITY 3: Check summary for clues
    # Provider indicators in summary
    if any(p in summary_lower for p in ["psychiatrist", "psychologist", "therapist", "doctor", "clinician", "nurse", "counselor", "prescrib"]):
        return "PROVIDER"
    
    # Patient indicators in summary
    if any(p in summary_lower for p in ["patient", "client", "symptoms", "diagnosed", "treatment for"]):
        return "PATIENT"
    
    # Medication indicators in summary  
    if any(p in summary_lower for p in ["medication", "drug", "mg", "dose", "prescribed", "antidepressant"]):
        return "MEDICATION"
    
    # Organization indicators
    if any(p in summary_lower for p in ["company", "organization", "corporation", "founded", "ceo", "cto"]):
        return "ORGANIZATION"
    
    # Check if name looks like a person (has capitalized words, no org indicators)
    words = name.split()
    if len(words) >= 2 and all(w[0].isupper() for w in words if w):
        # Likely a person name
        if any(p in summary_lower for p in ["support", "partner", "sister", "brother", "family", "friend"]):
            return "PERSON"
        return "PERSON"
    
    return "UNKNOWN"

CLASSIFICATION_PROMPT = """You are classifying relationships in a mental health knowledge graph.

Given a relationship between two entities (with their types), you must:
1. Classify it into one of these types
2. Determine the correct direction

Relationship types and their REQUIRED directions:
- TREATS: Provider → Patient (healthcare provider treats a patient)
- PRESCRIBED: Provider → Medication (doctor prescribed a medication)
- TAKES: Patient → Medication (patient takes a medication)
- REFERRED: Provider → Provider (one provider referred to another)
- SUPPORTS: Person → Person (someone emotionally supports another)
- FAMILY_OF: Person → Person (family relationship)
- WORKS_AT: Person → Organization (person works at an organization)
- DIAGNOSED_WITH: Patient → Condition (patient has a condition)
- TRIGGERS: Event → Condition (something triggers a condition)
- UNCERTAIN: Doesn't clearly fit any category

CRITICAL RULES:
- TREATS must have a PROVIDER as source and PATIENT as target
- PRESCRIBED must have a PROVIDER as source and MEDICATION as target
- TAKES must have a PATIENT as source and MEDICATION as target
- WORKS_AT must have a PERSON as source and ORGANIZATION as target

Respond in this exact format (two lines only):
TYPE: <relationship_type>
DIRECTION: <KEEP or REVERSE>

FROM: {from_name}
FROM TYPE: {from_type}

TO: {to_name}
TO TYPE: {to_type}

CONTEXT: {fact}

Answer:"""


# ===========================================
# Functions
# ===========================================

def get_neo4j_driver():
    """Create Neo4j driver connection."""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_all_relates_to_edges(driver):
    """Query all RELATES_TO edges with their entity information."""
    query = """
    MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity)
    RETURN 
        elementId(r) as rel_id,
        elementId(a) as from_id,
        a.name as from_name, 
        a.summary as from_summary,
        elementId(b) as to_id,
        b.name as to_name, 
        b.summary as to_summary,
        r.fact as fact
    """
    
    with driver.session() as session:
        result = session.run(query)
        edges = []
        for record in result:
            edges.append({
                "rel_id": record["rel_id"],
                "from_id": record["from_id"],
                "from_name": record["from_name"] or "Unknown",
                "from_summary": record["from_summary"] or "",
                "to_id": record["to_id"],
                "to_name": record["to_name"] or "Unknown",
                "to_summary": record["to_summary"] or "",
                "fact": record["fact"] or ""
            })
        return edges


def check_existing_typed_edge(driver, from_id, to_id, rel_type):
    """Check if a typed edge already exists between two nodes."""
    query = f"""
    MATCH (a:Entity)-[r:{rel_type}]->(b:Entity)
    WHERE elementId(a) = $from_id AND elementId(b) = $to_id
    RETURN count(r) as count
    """
    
    with driver.session() as session:
        result = session.run(query, from_id=from_id, to_id=to_id)
        record = result.single()
        return record["count"] > 0 if record else False


def validate_and_correct(rel_type, should_reverse, from_type, to_type):
    """Apply validation rules to catch and correct common errors.
    
    Returns:
        tuple: (corrected_rel_type, corrected_should_reverse)
    """
    # Determine effective source and target types after potential reversal
    if should_reverse:
        source_type, target_type = to_type, from_type
    else:
        source_type, target_type = from_type, to_type
    
    # Rule 1: TREATS must be Provider → Patient/Person
    if rel_type == "TREATS":
        # If target is medication, change to TAKES
        if target_type == "MEDICATION":
            rel_type = "TAKES"
            # Ensure non-medication is source
            if from_type == "MEDICATION":
                should_reverse = True
            else:
                should_reverse = False
        # If target is Provider (doctor treating doctor), mark uncertain
        elif target_type == "PROVIDER" and source_type == "PROVIDER":
            # Could be REFERRED instead
            rel_type = "REFERRED"
        # If source is Patient and target is Provider, reverse
        elif source_type == "PATIENT" and target_type == "PROVIDER":
            should_reverse = not should_reverse
        # If neither is provider, it's uncertain
        elif source_type != "PROVIDER" and target_type != "PROVIDER":
            if source_type in ["PATIENT", "PERSON"]:
                # Patient being treated - check if we need to reverse
                pass  # Keep as is, might be patient → something else
            else:
                rel_type = "UNCERTAIN"
    
    # Rule 2: PRESCRIBED must be Provider → Medication
    if rel_type == "PRESCRIBED":
        # If source is medication, reverse
        if source_type == "MEDICATION":
            should_reverse = not should_reverse
        # If target is Provider (not medication), this is wrong
        elif target_type == "PROVIDER":
            if source_type == "PROVIDER":
                rel_type = "REFERRED"  # Provider → Provider is referral
            else:
                rel_type = "UNCERTAIN"
        # If target is Patient, this is wrong (you prescribe medication, not patients)
        elif target_type == "PATIENT":
            rel_type = "TREATS"  # Provider treats patient
        # If source is Patient, they don't prescribe
        elif source_type == "PATIENT":
            rel_type = "TAKES"
    
    # Rule 3: TAKES must be Patient/Person → Medication
    if rel_type == "TAKES":
        # If source is medication, reverse
        if source_type == "MEDICATION":
            should_reverse = not should_reverse
        # If target is not medication, this is wrong
        elif target_type != "MEDICATION":
            if target_type == "PROVIDER":
                rel_type = "TREATS"
                should_reverse = not should_reverse  # Provider treats person
            else:
                rel_type = "UNCERTAIN"
        # If source is Provider, they prescribe not take
        elif source_type == "PROVIDER":
            rel_type = "PRESCRIBED"
    
    # Rule 4: WORKS_AT must be Person/Provider → Organization
    if rel_type == "WORKS_AT":
        if source_type == "ORGANIZATION" and target_type in ["PROVIDER", "PATIENT", "PERSON", "UNKNOWN"]:
            should_reverse = not should_reverse
        elif target_type != "ORGANIZATION":
            # Target should be organization
            if source_type == "ORGANIZATION":
                should_reverse = not should_reverse
            else:
                rel_type = "UNCERTAIN"
    
    # Rule 5: DIAGNOSED_WITH must be Patient → Condition
    if rel_type == "DIAGNOSED_WITH":
        if source_type == "CONDITION" or source_type == "ASSESSMENT":
            should_reverse = not should_reverse
        elif target_type not in ["CONDITION", "ASSESSMENT"]:
            rel_type = "UNCERTAIN"
    
    # Rule 6: SUPPORTS - supporter → supported (person → person)
    if rel_type == "SUPPORTS":
        # If supporting a medication or organization, likely wrong
        if target_type in ["MEDICATION", "ORGANIZATION"]:
            rel_type = "UNCERTAIN"
    
    # Rule 7: FAMILY_OF - person → person
    if rel_type == "FAMILY_OF":
        if source_type in ["MEDICATION", "ORGANIZATION"] or target_type in ["MEDICATION", "ORGANIZATION"]:
            rel_type = "UNCERTAIN"
    
    return rel_type, should_reverse


def classify_relationship(edge, from_type, to_type):
    """Use Ollama to classify a relationship and determine direction.
    
    Returns:
        tuple: (relationship_type, should_reverse)
               should_reverse is True if the edge direction should be flipped
    """
    prompt = CLASSIFICATION_PROMPT.format(
        from_name=edge["from_name"],
        from_type=from_type,
        to_name=edge["to_name"],
        to_type=to_type,
        fact=edge["fact"]
    )
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistency
                    "num_predict": 50     # Need more tokens for two-line response
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip().upper()
            
            # Parse the response for TYPE and DIRECTION
            rel_type = "UNCERTAIN"
            should_reverse = False
            
            for line in response_text.split("\n"):
                line = line.strip()
                if line.startswith("TYPE:"):
                    type_value = line.replace("TYPE:", "").strip()
                    for rt in RELATIONSHIP_TYPES:
                        if rt in type_value:
                            rel_type = rt
                            break
                elif line.startswith("DIRECTION:"):
                    direction_value = line.replace("DIRECTION:", "").strip()
                    should_reverse = "REVERSE" in direction_value
            
            # Fallback: if no structured response, try to extract type from full text
            if rel_type == "UNCERTAIN":
                for rt in RELATIONSHIP_TYPES:
                    if rt in response_text:
                        rel_type = rt
                        break
            
            # Apply validation rules to correct common errors
            rel_type, should_reverse = validate_and_correct(
                rel_type, should_reverse, from_type, to_type
            )
            
            return rel_type, should_reverse
        else:
            print(f"  ⚠ Ollama error: {response.status_code}")
            return "UNCERTAIN", False
            
    except requests.exceptions.Timeout:
        print("  ⚠ Ollama timeout")
        return "UNCERTAIN", False
    except Exception as e:
        print(f"  ⚠ Classification error: {e}")
        return "UNCERTAIN", False


def create_typed_edge(driver, from_id, to_id, rel_type, fact):
    """Create a new typed edge between two entities."""
    # We need to use a dynamic relationship type, which requires APOC or string formatting
    # Since we control the rel_type values, this is safe
    query = f"""
    MATCH (a:Entity), (b:Entity)
    WHERE elementId(a) = $from_id AND elementId(b) = $to_id
    CREATE (a)-[r:{rel_type} {{fact: $fact, source: 'reclassified'}}]->(b)
    RETURN r
    """
    
    with driver.session() as session:
        session.run(query, from_id=from_id, to_id=to_id, fact=fact)


def reclassify_all():
    """Main function to reclassify all RELATES_TO edges."""
    print("""
╔══════════════════════════════════════════════════════════╗
║         Relationship Reclassification Tool               ║
╠══════════════════════════════════════════════════════════╣
║  Classifies RELATES_TO edges into specific types using   ║
║  Ollama. Original edges are preserved.                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Connect to Neo4j
    print("📊 Connecting to Neo4j...")
    driver = get_neo4j_driver()
    
    # Get all RELATES_TO edges
    print("📊 Querying RELATES_TO edges...")
    edges = get_all_relates_to_edges(driver)
    print(f"   Found {len(edges)} edges to classify\n")
    
    if len(edges) == 0:
        print("No RELATES_TO edges found. Nothing to do.")
        driver.close()
        return
    
    # Classify each edge
    stats = Counter()
    skipped = 0
    reversed_count = 0
    corrected_count = 0
    
    for i, edge in enumerate(edges, 1):
        # Infer entity types
        from_type = infer_entity_type(edge["from_name"], edge["from_summary"])
        to_type = infer_entity_type(edge["to_name"], edge["to_summary"])
        
        print(f"[{i}/{len(edges)}] {edge['from_name']} ({from_type}) → {edge['to_name']} ({to_type})")
        
        # Classify using Ollama (now returns type and direction)
        rel_type, should_reverse = classify_relationship(edge, from_type, to_type)
        
        direction_note = " (REVERSED)" if should_reverse else ""
        print(f"         Classified as: {rel_type}{direction_note}")
        
        stats[rel_type] += 1
        
        # Skip UNCERTAIN - keep only RELATES_TO
        if rel_type == "UNCERTAIN":
            print("         → Keeping as RELATES_TO only")
            continue
        
        # Determine source and target based on direction
        if should_reverse:
            source_id = edge["to_id"]
            target_id = edge["from_id"]
            reversed_count += 1
            print(f"         → Direction: {edge['to_name']} → {edge['from_name']}")
        else:
            source_id = edge["from_id"]
            target_id = edge["to_id"]
        
        # Check if typed edge already exists
        if check_existing_typed_edge(driver, source_id, target_id, rel_type):
            print(f"         → {rel_type} edge already exists, skipping")
            skipped += 1
            continue
        
        # Create the new typed edge with correct direction
        create_typed_edge(driver, source_id, target_id, rel_type, edge["fact"])
        print(f"         → Created {rel_type} edge")
    
    driver.close()
    
    # Print summary
    print("\n" + "=" * 50)
    print("CLASSIFICATION SUMMARY")
    print("=" * 50)
    
    for rel_type in RELATIONSHIP_TYPES:
        count = stats.get(rel_type, 0)
        if count > 0:
            status = "(kept as RELATES_TO)" if rel_type == "UNCERTAIN" else "(new edge created)"
            print(f"  {rel_type:15} : {count:3} {status}")
    
    print(f"\n  Total processed   : {len(edges)}")
    print(f"  New edges created : {len(edges) - stats['UNCERTAIN'] - skipped}")
    print(f"  Direction reversed: {reversed_count}")
    print(f"  Skipped (exists)  : {skipped}")
    print(f"  Kept as RELATES_TO: {stats['UNCERTAIN']}")
    print("\n✅ Done! Original RELATES_TO edges preserved.")
    print("   View in Neo4j: MATCH (n)-[r]->() RETURN type(r), count(r)")


if __name__ == "__main__":
    reclassify_all()
