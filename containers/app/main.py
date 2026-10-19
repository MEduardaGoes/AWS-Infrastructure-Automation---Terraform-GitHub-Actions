"""Small standard-library HTTP API for an isolated Docker Swarm lab."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import signal
import socket
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def version_string(self):
        return "SwarmDemo"

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            self.send_json(200, {"status": "ok"})
        elif path == "/":
            self.send_json(
                200,
                {
                    "service": "devsecops-swarm-demo",
                    "version": os.environ.get("APP_VERSION", "1.0.0"),
                    "hostname": socket.gethostname(),
                },
            )
        else:
            self.send_json(404, {"error": "not_found"})

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def stop_server(_signum, _frame):
    raise KeyboardInterrupt


def main():
    signal.signal(signal.SIGTERM, stop_server)
    with ThreadingHTTPServer(("0.0.0.0", 8080), Handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
