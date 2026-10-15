import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

RESULTS_FILE = "/data/results.json"
PORT = 8080


def load_results() -> list:
    
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE) as f:
        return json.load(f)


class Handler(BaseHTTPRequestHandler):
    
    def log_message(self, *_): pass

    def do_GET(self):
        body = json.dumps(load_results(), indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
