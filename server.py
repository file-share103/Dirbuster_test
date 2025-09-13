#!/usr/bin/env python3
"""
DirBuster Demo HTTP Server

- Serves files from the ./site directory
- Listens on 0.0.0.0:8000 by default so you can access it from your LAN
- Returns 403 for the directory path /private/ to simulate restricted areas

Usage:
  python server.py --host 0.0.0.0 --port 8000

Then visit:
  http://127.0.0.1:8000
  http://YOUR_LAN_IP:8000

Educational purpose only. Only test on networks/systems you own or have explicit permission to test.
"""

import argparse
import os
import re
import socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.join(os.path.dirname(__file__), "site")


class DemoHandler(SimpleHTTPRequestHandler):
    """Custom handler that serves from BASE_DIR and simulates a 403 on /private/."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        # Simulate a restricted directory: return 403 for /private/ but still allow direct file access like /private/secrets.txt
        if re.fullmatch(r"/private/?", self.path):
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"403 Forbidden: Directory listing is disabled.")
            return

        # Simple health check endpoint
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        return super().do_GET()

    def log_message(self, format: str, *args):  # type: ignore[override]
        # Cleaner logs with client IP and timestamp
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))


def get_lan_ip() -> str:
    # Best-effort LAN IP detection
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    httpd = ThreadingHTTPServer((host, port), DemoHandler)
    try:
        lan_ip = get_lan_ip()
    except Exception:
        lan_ip = host

    print("DirBuster Demo Server running on:")
    print(f"  http://127.0.0.1:{port}")
    print(f"  http://{lan_ip}:{port}  (LAN)")
    print("Press Ctrl+C to stop.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the DirBuster demo HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="Host/IP to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    args = parser.parse_args()
    run(args.host, args.port)