from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path.home() / ".stepcast" / "runs.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    success INTEGER NOT NULL,
    total_time REAL NOT NULL,
    timestamp TEXT NOT NULL,
    data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs (success);
"""


class RunStorage:
    """SQLite-backed run history storage.

    Args:
        db_path: Path to the SQLite database file.
            Use ':memory:' for in-memory testing.

    Example:
        >>> storage = RunStorage(':memory:')
        >>> storage.list_runs()
        []
    """

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self._path = str(db_path)
        if self._path != ":memory:":
            Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def save_run(self, report_dict: dict[str, Any]) -> str:
        """Save a run report and return its ID.

        Args:
            report_dict: Serialised RunReport (from RunReport.to_json()).

        Returns:
            Unique run ID string (UUID4).
        """
        run_id = str(uuid.uuid4())
        self._conn.execute(
            "INSERT INTO runs (id, pipeline_name, success, total_time, timestamp, data) "  # noqa: E501
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                run_id,
                report_dict.get("pipeline_name", ""),
                1 if report_dict.get("success") else 0,
                report_dict.get("total_time", 0.0),
                report_dict.get("timestamp", ""),
                json.dumps(report_dict),
            ),
        )
        self._conn.commit()
        return run_id

    def list_runs(
        self,
        limit: int = 50,
        status: str | None = None,
        pipeline_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """List recent runs with optional filters.

        Args:
            limit: Maximum number of runs to return.
            status: 'passed' or 'failed' filter (optional).
            pipeline_name: Filter by pipeline name (optional).

        Returns:
            List of run summary dicts.
        """
        query = "SELECT id, pipeline_name, success, total_time, timestamp FROM runs"
        params: list[Any] = []
        conditions = []

        if status == "passed":
            conditions.append("success = 1")
        elif status == "failed":
            conditions.append("success = 0")

        if pipeline_name:
            conditions.append("pipeline_name = ?")
            params.append(pipeline_name)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self._conn.execute(query, params).fetchall()
        return [
            {
                "id": r["id"],
                "pipeline_name": r["pipeline_name"],
                "success": bool(r["success"]),
                "total_time": r["total_time"],
                "timestamp": r["timestamp"],
            }
            for r in rows
        ]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        """Fetch the full run data for a given ID.

        Args:
            run_id: UUID string of the run.

        Returns:
            Full run dict or None if not found.
        """
        row = self._conn.execute(
            "SELECT data FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["data"])  # type: ignore[no-any-return]

    def delete_run(self, run_id: str) -> bool:
        """Delete a run by ID.

        Args:
            run_id: UUID string of the run to delete.

        Returns:
            True if a row was deleted, False if not found.
        """
        cur = self._conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def stats(self) -> dict[str, Any]:
        """Return simple aggregate statistics.

        Returns:
            Dict with total, passed, failed, avg_time.
        """
        row = self._conn.execute(
            "SELECT COUNT(*) as total, "
            "SUM(success) as passed, "
            "AVG(total_time) as avg_time "
            "FROM runs"
        ).fetchone()
        total = row["total"] or 0
        passed = row["passed"] or 0
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "avg_time": round(row["avg_time"] or 0, 3),
        }

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
