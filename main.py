"""Dependency-free KataBump health endpoint; not an LLM inference server."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        checkpoint = Path("checkpoints/tiny.pt").exists()
        payload = {
            "service": "PersianGPT",
            "status": "online",
            "checkpoint_present": checkpoint,
            "inference": "not_available_on_free_tier",
            "note": "KataBump Free has very limited RAM; this endpoint is a health check only."
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"PersianGPT health server listening on 0.0.0.0:{port}", flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
