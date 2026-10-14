"""
Local results server. Reads results/results.db and serves a live webpage.
Started automatically by 04_run_benchmarks.sh after all jobs finish.
  http://localhost:9090        -> HTML table
  http://localhost:9090/results -> JSON
"""

import json
import os
import sqlite3
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "results", "results.db")
PORT    = 9090

COLS = [
    ("ram_gb",            "RAM (GB)"),
    ("total_time_s",      "Total (s)"),
    ("throughput_mb_s",   "Throughput (MB/s)"),
    ("cpu_pct",           "CPU %"),
    ("io_read_mb",        "I/O Read (MB)"),
    ("io_write_mb",       "I/O Write (MB)"),
    ("records_per_chunk", "Records/Chunk"),
]


def fetch():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM results ORDER BY ram_gb").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def html(rows):
    header = "".join(f"<th>{lbl}</th>" for _, lbl in COLS)
    body   = ""
    for r in rows:
        cells = ""
        for key, _ in COLS:
            v = r.get(key, "")
            if isinstance(v, float): v = f"{v:.2f}"
            elif isinstance(v, int): v = f"{v:,}"
            cells += f"<td>{v}</td>"
        body += f"<tr>{cells}</tr>"
    if not rows:
        body = f'<tr><td colspan="{len(COLS)}" style="text-align:center;color:#666">No results yet</td></tr>'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="5">
<title>Benchmark Results</title>
<style>
  body{{font-family:monospace;padding:2rem;background:#111;color:#eee}}
  h1{{color:#7ec8e3}}p{{color:#888;font-size:.85rem}}
  table{{border-collapse:collapse;width:100%;margin-top:1rem}}
  th{{background:#1e3a4a;color:#7ec8e3;padding:10px 14px;text-align:left;white-space:nowrap}}
  td{{padding:8px 14px;border-bottom:1px solid #222}}
  tr:hover td{{background:#1a1a2e}}
  a{{color:#7ec8e3}}
</style></head><body>
<h1>External Sort Benchmark</h1>
<p>20M records (userid,score) &nbsp;|&nbsp; ~369 MB &nbsp;|&nbsp;
   {len(rows)} result(s) &nbsp;|&nbsp; auto-refreshes every 5s &nbsp;|&nbsp;
   <a href="/results">/results</a> for JSON</p>
<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def do_GET(self):
        if self.path == "/results":
            data = json.dumps(fetch(), indent=2).encode()
            self._respond(200, "application/json", data)
        else:
            self._respond(200, "text/html; charset=utf-8", html(fetch()).encode())

    def _respond(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"Results server running -> {url}")
    print("Press Ctrl+C to stop.")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    server.serve_forever()
