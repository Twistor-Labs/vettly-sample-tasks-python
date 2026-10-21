# Task tracker API (Python)

Small JSON API for a task list on the standard library HTTP server. Python 3.10+.

```bash
pip install -r requirements.txt   # pytest only
python -m tasks.server            # http://127.0.0.1:3000
python -m pytest -q
```

Routes: `GET /tasks?done=true|false`, `POST /tasks` with `{"title": "..."}` (1-200 chars),
`POST /tasks/<id>/complete`, `DELETE /tasks/<id>`. Validation errors return 400, unknown
ids 404, bodies are capped at 16 KB. The store sits behind a small class so a database can
replace it without touching the handler.
