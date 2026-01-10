#!/usr/bin/env python3
"""
Simple preview server for the Jekyll website.
Serves static files from the website directory with basic Jekyll-like routing.
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import unquote

PORT = 4000
BASE_URL = "/lightgroove"

class JekyllPreviewHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to simulate Jekyll routing"""
    
    def do_GET(self):
        # Remove base URL prefix if present
        path = unquote(self.path)
        if path.startswith(BASE_URL):
            path = path[len(BASE_URL):]
        
        # Handle root
        if path == "" or path == "/":
            path = "/index.html"
        
        # Handle pages without extensions (Jekyll-style)
        if not os.path.splitext(path)[1]:
            # Try as .html first
            if os.path.exists("website" + path + ".html"):
                path = path + ".html"
            # Try as directory index
            elif os.path.exists("website" + path + "/index.html"):
                path = path + "/index.html"
            # Try in _pages
            elif os.path.exists("website/_pages" + path + ".md"):
                print(f"⚠️  Markdown file found but not rendered: _pages{path}.md")
                print(f"   Jekyll would convert this to HTML. Using basic preview.")
        
        # Update the path for the request
        self.path = "/website" + path
        
        # Serve the file
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("🌐 Jekyll Website Preview Server")
    print("=" * 60)
    print()
    print(f"📁 Serving from: {os.path.join(os.getcwd(), 'website')}")
    print(f"🌍 Local URL: http://localhost:{PORT}{BASE_URL}/")
    print()
    print("⚠️  NOTE: This is a simple preview server.")
    print("   - Markdown files are NOT rendered")
    print("   - Liquid templates are NOT processed")
    print("   - For full Jekyll preview, use Docker or install Jekyll")
    print()
    print("   To see the full site, run: ./run_website.sh")
    print("   (requires Docker or Ruby/Jekyll)")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    with socketserver.TCPServer(("", PORT), JekyllPreviewHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
            sys.exit(0)

if __name__ == "__main__":
    main()
