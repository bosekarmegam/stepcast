from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any


def db_step(
    dsn: str,
    query: str,
    label: str | None = None,
    params: tuple[Any, ...] = (),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: wrap a database query step with automatic connection.

    Supports SQLite (stdlib) by default. For other DBs, install the appropriate driver.

    Args:
        dsn: SQLite file path or other DSN string.
        query: SQL query to execute.
        label: Step label (optional).
        params: Query parameters tuple.

    Returns:
        Decorator that wraps the function.

    Example:
        >>> @db_step(":memory:", "SELECT 1")
        ... def check_db(cursor):
        ...     return cursor.fetchone()
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            import sqlite3

            print(f"→ Connecting to {dsn}")
            conn = sqlite3.connect(dsn)
            try:
                cursor = conn.cursor()
                print("→ Executing query")
                cursor.execute(query, params)
                print(f"← {cursor.rowcount if cursor.rowcount >= 0 else '?'} rows affected")  # noqa: E501
                return fn(cursor, *args, **kwargs) if args or kwargs else fn(cursor)
            finally:
                conn.close()
                print("→ Connection closed")

        return wrapper

    return decorator
