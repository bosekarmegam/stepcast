from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any


def http_step(
    url: str,
    method: str = "GET",
    label: str | None = None,
    log_response: bool = True,
    retries: int = 3,
    timeout: float = 30.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: wrap an HTTP call with request/response logging.

    Requires the `requests` library (not a stepcast dependency — install separately).

    Args:
        url: Target URL.
        method: HTTP method (default GET).
        label: Step label (default: inferred from URL).
        log_response: Print status code and response size (default True).
        retries: Number of retry attempts on failure.
        timeout: Request timeout in seconds.

    Returns:
        Decorator that wraps the function.

    Example:
        >>> @http_step("https://api.example.com/data", method="GET")
        ... def fetch_data():
        ...     pass  # The decorator handles the request
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            try:
                import requests  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ImportError(
                    "http_step requires requests: pip install requests"
                ) from exc

            print(f"→ {method} {url}")

            for attempt in range(1, retries + 2):
                try:
                    resp = requests.request(method, url, timeout=timeout)
                    if log_response:
                        print(f"← {resp.status_code} ({len(resp.content)} bytes)")
                    resp.raise_for_status()
                    return fn(resp, *args, **kwargs) if args or kwargs else fn(resp)
                except Exception as e:
                    if attempt <= retries:
                        print(f"  retry {attempt}/{retries}: {e}")
                    else:
                        raise

        return wrapper

    return decorator
