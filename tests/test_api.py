import json
import threading
import urllib.error
import urllib.request

import pytest

from tasks.server import serve


@pytest.fixture
def base():
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=None if body is None else body.encode())
    try:
        with urllib.request.urlopen(req) as res:
            raw = res.read()
            return res.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read() or b"null")


def test_task_lifecycle(base):
    status, task = call("POST", f"{base}/tasks", json.dumps({"title": "Write tests"}))
    assert status == 201
    assert len(call("GET", f"{base}/tasks?done=false")[1]) == 1
    assert call("POST", f"{base}/tasks/{task['id']}/complete")[1]["done"] is True
    assert call("DELETE", f"{base}/tasks/{task['id']}")[0] == 204
    assert call("DELETE", f"{base}/tasks/{task['id']}")[0] == 404


def test_validation(base):
    assert call("POST", f"{base}/tasks", "{}")[0] == 400
    assert call("POST", f"{base}/tasks", "{nope")[0] == 400
