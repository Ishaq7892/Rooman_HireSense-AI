import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PORT = 5000
DIRECTORY = Path(__file__).parent.resolve()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/output/report.html'
        return super().do_GET()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server(start_port=5000, max_attempts=10):
    os.chdir(DIRECTORY)
    port = start_port

    for i in range(max_attempts):
        try:
            with ReusableTCPServer(("", port), Handler) as httpd:
                url = f"http://localhost:{port}"
                print("=" * 70)
                print(f"🚀 HireSense AI Web Server Running at: {url}")
                print(f"🌐 Opening {url} in your browser...")
                print("Press Ctrl+C in terminal to stop the server.")
                print("=" * 70)
                
                try:
                    webbrowser.open(url)
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\n" + "=" * 70)
                    print("🛑 HireSense AI Web Server stopped cleanly.")
                    print("=" * 70)
                return
        except OSError as e:
            if getattr(e, 'winerror', None) == 10048 or "address already in use" in str(e).lower():
                print(f"Port {port} is in use, trying port {port + 1}...")
                port += 1
            else:
                raise e

    print(f"Could not bind to any port between {start_port} and {port - 1}.")

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")


