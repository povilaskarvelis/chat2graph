#!/usr/bin/env python3
"""
API server for Chat2Graph dashboard with upload functionality.

Usage:
    python dashboard/api_server.py

Endpoints:
    GET /*                      - Serve static files
    POST /api/upload-transcript - Upload transcript for LLM processing
    POST /api/upload-json       - Upload pre-analyzed JSON
    GET /api/status/<job_id>    - Check processing status
"""

import http.server
import socketserver
import os
import sys
import json
import uuid
import threading
import subprocess
import traceback
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import re

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

PORT = 8000

# Job status tracking
jobs = {}


def parse_multipart(content_type, body):
    """Parse multipart form data without the deprecated cgi module."""
    # Extract boundary from content type
    boundary_match = re.search(r'boundary=([^\s;]+)', content_type)
    if not boundary_match:
        raise ValueError("No boundary found in Content-Type")
    
    boundary = boundary_match.group(1).encode()
    if boundary.startswith(b'"') and boundary.endswith(b'"'):
        boundary = boundary[1:-1]
    
    # Split by boundary
    parts = body.split(b'--' + boundary)
    
    result = {}
    
    for part in parts:
        if not part or part == b'--\r\n' or part == b'--':
            continue
        
        # Remove leading/trailing CRLF
        part = part.strip(b'\r\n')
        if not part:
            continue
        
        # Split headers from content
        if b'\r\n\r\n' in part:
            headers_section, content = part.split(b'\r\n\r\n', 1)
        else:
            continue
        
        # Parse Content-Disposition header
        headers_text = headers_section.decode('utf-8', errors='ignore')
        
        name_match = re.search(r'name="([^"]+)"', headers_text)
        if not name_match:
            continue
        
        field_name = name_match.group(1)
        
        # Check if it's a file
        filename_match = re.search(r'filename="([^"]*)"', headers_text)
        
        if filename_match:
            # File field
            result[field_name] = {
                'filename': filename_match.group(1),
                'content': content.rstrip(b'\r\n')
            }
        else:
            # Regular field
            result[field_name] = content.rstrip(b'\r\n').decode('utf-8')
    
    return result


def check_ollama_available():
    """Check if Ollama is running and accessible."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_neo4j_available():
    """Check if Neo4j is running and accessible."""
    try:
        from dotenv import load_dotenv
        from neo4j import GraphDatabase
        load_dotenv()

        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")

        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        return True
    except Exception:
        return False


def process_transcript_background(job_id, content, episode_name, disorder, meets_criteria):
    """Background task to process a transcript."""
    try:
        jobs[job_id]["status"] = "extracting"
        jobs[job_id]["step"] = "Extracting entities with LLM..."

        # Import the processing function
        from extract_clinical import extract_entities_llm, store_in_neo4j, get_neo4j_driver

        # Extract entities using LLM
        result = extract_entities_llm(content)

        if result is None:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = "LLM extraction failed. Check if Ollama is running."
            return

        jobs[job_id]["status"] = "storing"
        jobs[job_id]["step"] = "Storing in Neo4j..."
        jobs[job_id]["extraction_result"] = {
            "clinical_count": len(result.get("clinical_entities", [])),
            "semantic_count": len(result.get("semantic_entities", [])),
            "relationship_count": len(result.get("relationships", []))
        }

        # Store in Neo4j
        driver = get_neo4j_driver()
        store_in_neo4j(driver, episode_name, disorder, meets_criteria, result)
        driver.close()

        jobs[job_id]["status"] = "analyzing"
        jobs[job_id]["step"] = "Regenerating analysis..."

        # Run analyze_graphs.py to regenerate analysis
        analyze_script = os.path.join(parent_dir, "analyze_graphs.py")
        subprocess.run([sys.executable, analyze_script],
                      capture_output=True, cwd=parent_dir)

        jobs[job_id]["status"] = "complete"
        jobs[job_id]["step"] = "Done!"

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        traceback.print_exc()


def merge_json_data(uploaded_data):
    """Merge uploaded JSON data into the analysis_latest.json."""
    results_dir = os.path.join(parent_dir, "results")
    latest_path = os.path.join(results_dir, "analysis_latest.json")

    # Load existing data
    existing_data = {"by_episode": {}, "by_disorder": {}, "overall": {}}
    if os.path.exists(latest_path):
        with open(latest_path, "r") as f:
            existing_data = json.load(f)

    # Merge uploaded data
    if "by_episode" in uploaded_data:
        existing_data["by_episode"].update(uploaded_data["by_episode"])

    # Recalculate overall stats
    total_entities = 0
    clinical_entities = 0
    semantic_entities = 0
    total_relationships = 0

    for ep_data in existing_data.get("by_episode", {}).values():
        metrics = ep_data.get("metrics", {})
        total_entities += metrics.get("total", 0)
        clinical_entities += metrics.get("clinical", 0)
        semantic_entities += metrics.get("semantic", 0)
        total_relationships += metrics.get("relationships", 0)

    existing_data["overall"] = {
        "total_entities": total_entities,
        "clinical_entities": clinical_entities,
        "semantic_entities": semantic_entities,
        "total_relationships": total_relationships,
        "episodes": len(existing_data.get("by_episode", {}))
    }

    # Save merged data
    os.makedirs(results_dir, exist_ok=True)
    with open(latest_path, "w") as f:
        json.dump(existing_data, f, indent=2)

    return existing_data


class APIRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with API endpoints."""

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)

        # API: Check job status
        if parsed.path.startswith('/api/status/'):
            job_id = parsed.path.split('/')[-1]
            self.handle_status(job_id)
            return

        # API: Health check
        if parsed.path == '/api/health':
            self.handle_health_check()
            return

        # API: Get disorders list
        if parsed.path == '/api/disorders':
            self.handle_disorders()
            return

        # Static file serving
        super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)

        if parsed.path == '/api/upload-transcript':
            self.handle_transcript_upload()
        elif parsed.path == '/api/upload-json':
            self.handle_json_upload()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_health_check(self):
        """Return service health status."""
        health = {
            "server": True,
            "ollama": check_ollama_available(),
            "neo4j": check_neo4j_available()
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health).encode())

    def handle_disorders(self):
        """Return list of available disorders."""
        disorders = ["GAD", "ADHD", "Wernicke's Aphasia", "MDD", "OCD", "PTSD", "Other"]

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(disorders).encode())

    def handle_status(self, job_id):
        """Return job status."""
        if job_id not in jobs:
            self.send_error(404, "Job not found")
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(jobs[job_id]).encode())

    def handle_transcript_upload(self):
        """Handle transcript file upload."""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')

            if 'multipart/form-data' in content_type:
                # Read body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Parse multipart form
                form = parse_multipart(content_type, body)

                # Extract form fields
                episode_name = form.get('episode_name', '')
                disorder = form.get('disorder', '')
                meets_criteria_val = form.get('meets_criteria', 'false')
                meets_criteria = str(meets_criteria_val).lower() == 'true'

                # Get file content
                file_data = form.get('file')
                if file_data and isinstance(file_data, dict) and 'content' in file_data:
                    content = file_data['content'].decode('utf-8')
                else:
                    raise ValueError("No file uploaded")
            else:
                # Parse JSON body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)

                episode_name = data.get('episode_name', '')
                disorder = data.get('disorder', '')
                meets_criteria = data.get('meets_criteria', False)
                content = data.get('content', '')

            # Validate required fields
            if not episode_name:
                self.send_error(400, "Episode name is required")
                return
            if not disorder:
                self.send_error(400, "Disorder type is required")
                return
            if not content:
                self.send_error(400, "Transcript content is required")
                return

            # Check services availability
            if not check_ollama_available():
                self.send_error(503, "Ollama is not available. Please start Ollama first.")
                return
            if not check_neo4j_available():
                self.send_error(503, "Neo4j is not available. Please start Neo4j first.")
                return

            # Create job
            job_id = str(uuid.uuid4())
            jobs[job_id] = {
                "id": job_id,
                "status": "queued",
                "step": "Starting...",
                "episode_name": episode_name,
                "disorder": disorder,
                "meets_criteria": meets_criteria
            }

            # Start background processing
            thread = threading.Thread(
                target=process_transcript_background,
                args=(job_id, content, episode_name, disorder, meets_criteria)
            )
            thread.start()

            # Return job ID
            self.send_response(202)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"job_id": job_id}).encode())

        except Exception as e:
            traceback.print_exc()
            self.send_error(500, str(e))

    def handle_json_upload(self):
        """Handle pre-analyzed JSON upload."""
        try:
            content_type = self.headers.get('Content-Type', '')

            if 'multipart/form-data' in content_type:
                # Read body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Parse multipart form
                form = parse_multipart(content_type, body)

                # Get file content
                file_data = form.get('file')
                if file_data and isinstance(file_data, dict) and 'content' in file_data:
                    content = file_data['content'].decode('utf-8')
                    data = json.loads(content)
                else:
                    raise ValueError("No file uploaded")
            else:
                # Parse JSON body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)

            # Validate structure
            if 'by_episode' not in data:
                self.send_error(400, "Invalid JSON structure: missing 'by_episode' field")
                return

            # Merge data
            merged = merge_json_data(data)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "episodes_count": len(merged.get("by_episode", {}))
            }).encode())

        except json.JSONDecodeError as e:
            self.send_error(400, f"Invalid JSON: {str(e)}")
        except Exception as e:
            traceback.print_exc()
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        """Custom logging format."""
        method = args[0].split()[0] if args else "?"
        path = args[0].split()[1] if args and len(args[0].split()) > 1 else "?"
        status = args[1] if len(args) > 1 else "?"

        # Only log API requests and errors
        if '/api/' in path or str(status).startswith('4') or str(status).startswith('5'):
            print(f"[{method}] {path} - {status}")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded TCP server to handle multiple requests."""
    allow_reuse_address = True


def main():
    """Start the API server."""
    # Change to parent directory to serve from project root
    os.chdir(parent_dir)

    handler = APIRequestHandler

    with ThreadedTCPServer(("", PORT), handler) as httpd:
        print(f"""
+==============================================================+
|           Chat2Graph Dashboard API Server                    |
+==============================================================+
|  Server running at: http://localhost:{PORT}                  |
|  Dashboard URL: http://localhost:{PORT}/dashboard/           |
|                                                              |
|  API Endpoints:                                              |
|    POST /api/upload-transcript  - Upload transcript          |
|    POST /api/upload-json        - Upload pre-analyzed JSON   |
|    GET  /api/status/<job_id>    - Check processing status    |
|    GET  /api/health             - Service health check       |
|                                                              |
|  Press Ctrl+C to stop the server                            |
+==============================================================+
        """)

        # Check service availability
        print("Checking services...")
        ollama_ok = check_ollama_available()
        neo4j_ok = check_neo4j_available()
        print(f"  Ollama: {'OK' if ollama_ok else 'NOT AVAILABLE'}")
        print(f"  Neo4j:  {'OK' if neo4j_ok else 'NOT AVAILABLE'}")
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
