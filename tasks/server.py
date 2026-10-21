import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from tasks.store import TaskStore, ValidationError

MAX_BODY = 16 * 1024
ITEM = re.compile(r"^/tasks/([\w-]+)(/complete)?$")


def make_handler(store: TaskStore):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body=None):
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.end_headers()
            if body is not None:
                self.wfile.write(json.dumps(body).encode())

        def _json(self):
            length = int(self.headers.get("content-length") or 0)
            if length > MAX_BODY:
                raise ValidationError("body too large")
            try:
                return json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError as exc:
                raise ValidationError("body must be valid JSON") from exc

        def do_GET(self):
            url = urlparse(self.path)
            if url.path != "/tasks":
                return self._send(404, {"error": "route not found"})
            done = parse_qs(url.query).get("done", [None])[0]
            return self._send(200, store.list(None if done is None else done == "true"))

        def do_POST(self):
            try:
                if self.path == "/tasks":
                    return self._send(201, store.create(self._json()))
                m = ITEM.match(self.path)
                if m and m.group(2):
                    task = store.complete(m.group(1))
                    return self._send(200, task) if task else self._send(404, {"error": "task not found"})
                return self._send(404, {"error": "route not found"})
            except ValidationError as exc:
                return self._send(400, {"error": str(exc)})

        def do_DELETE(self):
            m = ITEM.match(self.path)
            if m and not m.group(2):
                return self._send(204) if store.remove(m.group(1)) else self._send(404, {"error": "task not found"})
            return self._send(404, {"error": "route not found"})

        def log_message(self, *args):
            pass

    return Handler


def serve(port: int = 3000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(TaskStore()))


if __name__ == "__main__":
    serve().serve_forever()
