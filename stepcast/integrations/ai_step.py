from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any


def ai_step(
    prompt_fn: Callable[[Any], str] | str,
    model: str = "gemini-1.5-flash",
    label: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: wrap an LLM call step.

    Uses the user's own Gemini API key (BYOK). Requires google-generativeai.

    Args:
        prompt_fn: Callable taking prev_output and returning a prompt string,
            or a static prompt string.
        model: Gemini model name (default 'gemini-1.5-flash').
        label: Step label override.

    Returns:
        Decorator that wraps the function with an LLM call.

    Example:
        >>> @ai_step(lambda data: f"Summarise: {data}")
        ... def summarise(ai_response: str):
        ...     return ai_response
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(prev_output: Any = None) -> Any:  # noqa: ANN401
            from stepcast.config import get_gemini_api_key

            key = get_gemini_api_key()
            if not key:
                raise RuntimeError(
                    "ai_step requires a Gemini API key.\n"
                    "Set STEPCAST_GEMINI_API_KEY or run: "
                    "stepcast config set gemini_api_key YOUR_KEY"
                )

            try:
                import google.generativeai as genai  # lazy import
            except ImportError as exc:
                raise ImportError(
                    "ai_step requires google-generativeai: "
                    "pip install 'stepcast[gemini]'"
                ) from exc

            genai.configure(api_key=key)  # type: ignore[attr-defined]
            gen_model = genai.GenerativeModel(model)  # type: ignore[attr-defined]

            prompt = (
                prompt_fn(prev_output)
                if callable(prompt_fn)
                else prompt_fn
            )
            print(f"→ Calling {model}...")
            response = gen_model.generate_content(prompt)
            ai_text = response.text.strip()
            print(f"← {len(ai_text)} chars returned")

            import inspect

            sig = inspect.signature(fn)
            if sig.parameters:
                return fn(ai_text)
            return fn()

        return wrapper

    return decorator
