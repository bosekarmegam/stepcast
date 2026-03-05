# Dashboard Guide

## Model A — Local (Default, Zero Config)

```bash
stepcast serve
# → Opens http://localhost:4321 automatically
# → Run history stored in ~/.stepcast/runs.db
# → Ctrl+C to stop
```

Stream a live run:
```python
pipe = Pipeline("ETL Job", dashboard=True)
pipe.run()
```

**Dashboard features:**
- Live step streaming via WebSocket
- Run history with search and filter by status
- Per-run detail view: steps, durations, stdout, errors, narrations
- Analytics: total/pass/fail counts, average duration
- Export any run as JSON

**Install:**
```bash
pip install "stepcast[dashboard]"
```

---

## Model B — Self-Hosted Team (Docker)

```bash
docker-compose up -d
# Team connects at http://your-server:4321
```

**Set a shared API key:**
```bash
STEPCAST_AUTH_KEY=your-secret docker-compose up
```

**Configure developers:**
```bash
stepcast config set server_url http://your-server:4321
stepcast config set server_key your-secret
```

**Submit runs to team server:**
```python
pipe = Pipeline("ETL", dashboard="http://your-server:4321")
pipe.run()
```

---

## Model C — Cloud SaaS

⚠️ Not yet built. Planned for Phase 3 only if user growth justifies it.
See `INSTRUCTIONS_2.md` for details on the open-core model.
