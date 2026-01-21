#!/usr/bin/env python3
"""
Simple HTTP server for the Chat2Graph dashboard.

Usage:
    python dashboard/serve.py

Then open http://localhost:8000/dashboard/ in your browser.
"""

import http.server
import socketserver
import os
import sys

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow loading JSON files
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    # Change to parent directory to serve from project root
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(parent_dir)
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════╗
║           Chat2Graph Dashboard Server                    ║
╠══════════════════════════════════════════════════════════╣
║  Server running at: http://localhost:{PORT}              ║
║  Dashboard URL: http://localhost:{PORT}/dashboard/       ║
║                                                          ║
║  Press Ctrl+C to stop the server                        ║
╚══════════════════════════════════════════════════════════╝
        """)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()

