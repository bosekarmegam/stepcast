from __future__ import annotations


def narrate_step(
    label: str,
    stdout: str,
    duration: float,
    output_summary: str,
) -> str | None:
    """Call Gemini to narrate a completed step in plain English.

    Uses the user's own API key (BYOK model). Silently returns None
    if no key is configured or if the API call fails for any reason.
    Narration failure must NEVER affect pipeline execution.

    Supports both the new ``google-genai`` SDK and the legacy
    ``google-generativeai`` package.

    Args:
        label: Human-readable step label.
        stdout: Captured stdout from the step.
        duration: Step duration in seconds.
        output_summary: repr() of the step's return value (truncated).

    Returns:
        1–2 sentence narration string, or None on any failure.
    """
    from stepcast.config import get_gemini_api_key

    key = get_gemini_api_key()
    if not key:
        return None

    # Truncate stdout to avoid token bloat
    stdout_preview = stdout[:500] + "…" if len(stdout) > 500 else stdout

    prompt = (
        f'A Python pipeline step named "{label}" completed in {duration:.2f}s.\n'
        f"Stdout output:\n{stdout_preview}\n"
        f"Return value summary: {output_summary}\n"
        "In 1–2 plain English sentences, explain what happened and if it looks normal. "
        "Be direct. No jargon. The reader is a developer in a hurry."
    )

    # Try new google-genai SDK first
    try:
        from google import genai

        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        text = response.text
        return text.strip() if text else ""
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback to legacy google-generativeai
    try:
        import google.generativeai as genai_legacy

        genai_legacy.configure(api_key=key)  # type: ignore[attr-defined]
        model = genai_legacy.GenerativeModel("gemini-1.5-flash")  # type: ignore[attr-defined]
        response_legacy = model.generate_content(prompt)
        text_legacy = response_legacy.text
        return text_legacy.strip() if text_legacy else ""
    except Exception:
        return None  # narration failure must NEVER affect pipeline execution
