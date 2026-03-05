from __future__ import annotations

import sys

import click

from stepcast import __version__
from stepcast.config import get_config_value, get_gemini_api_key, set_config
from stepcast.utils import detect_platform, terminal_supports_unicode


@click.group()
def main() -> None:
    """stepcast — Every Python script deserves a voice."""


@main.command()
def version() -> None:
    """Print the stepcast version."""
    click.echo(f"stepcast {__version__}")


@main.command()
def doctor() -> None:
    """Check your environment for common setup issues."""
    ok = "  ✅ " if terminal_supports_unicode() else "  OK  "
    warn = "  ⚠️  " if terminal_supports_unicode() else "  WW  "

    click.echo("\nstepcast doctor")
    click.echo("─" * 40)

    # Python
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"  # noqa: E501
    click.echo(f"{ok} Python {py_ver}")

    # stepcast version
    click.echo(f"{ok} stepcast {__version__}")

    # Platform
    platform_str = detect_platform()
    click.echo(f"{ok} Platform: {platform_str}")

    # Terminal
    enc = getattr(sys.stdout, "encoding", "unknown")
    click.echo(f"{ok} Terminal: {enc}")

    # Gemini key
    key = get_gemini_api_key()
    if key:
        click.echo(f"{ok} Gemini API key: configured")
    else:
        click.echo(f"{warn} Gemini API key: not configured")
        click.echo("       → Run: stepcast config set gemini_api_key YOUR_KEY")
        click.echo("       → Or:  export STEPCAST_GEMINI_API_KEY=YOUR_KEY")
        click.echo("       → Get free key: https://aistudio.google.com/app/apikey")

    # rich
    try:
        import rich  # noqa: F401

        click.echo(f"{ok} rich: installed (beautiful output enabled)")
    except ImportError:
        click.echo(f"{warn} rich: not installed")
        click.echo("       → pip install stepcast[rich]")

    # dashboard
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401

        click.echo(f"{ok} Dashboard: installed")
    except ImportError:
        click.echo(f"{warn} Dashboard: not installed")
        click.echo("       → pip install stepcast[dashboard]")

    click.echo()


@main.group()
def config() -> None:
    """Read and write stepcast user configuration."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value.

    Example: stepcast config set gemini_api_key YOUR_KEY
    """
    set_config(key, value)
    click.echo(f"✓ Set {key}")


@config.command("get")
@click.argument("key")
def config_get(key: str) -> None:
    """Get a configuration value.

    Example: stepcast config get gemini_api_key
    """
    val = get_config_value(key)
    if val is None:
        click.echo("(not set)")
    else:
        click.echo(val)


@main.command()
@click.argument("script", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Print steps without executing")
def run(script: str, dry_run: bool) -> None:
    """Execute a pipeline Python script.

    SCRIPT should define a `pipe` Pipeline and call `pipe.run()`.
    """
    import runpy

    from stepcast.exceptions import PipelineAbortError

    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit:
        pass
    except PipelineAbortError as exc:
        # fail_fast aborted — this is normal pipeline behaviour, not a tool error
        click.echo(f"\nPipeline aborted: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@main.command()
def check() -> None:
    """Validate the current configuration."""
    from stepcast.config import get_config

    cfg = get_config()
    if cfg:
        click.echo("Config OK:")
        for k, v in cfg.items():
            display = "***" if "key" in k.lower() or "secret" in k.lower() else v
            click.echo(f"  {k} = {display}")
    else:
        click.echo("No configuration found at ~/.stepcast/config.toml")


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True, help="Bind host")
@click.option("--port", default=4321, show_default=True, help="Bind port")
@click.option("--no-browser", is_flag=True, help="Do not open the browser")
def serve(host: str, port: int, no_browser: bool) -> None:
    """Launch the local stepcast web dashboard."""
    try:
        from stepcast.dashboard.server import serve as _serve

        click.echo(f"  Starting stepcast dashboard at http://{host}:{port}")
        click.echo("  Press Ctrl+C to stop\n")
        _serve(host=host, port=port, open_browser=not no_browser)
    except ImportError:
        click.echo(
            "Dashboard dependencies not installed.\n"
            "Run: pip install 'stepcast[dashboard]'",
            err=True,
        )
        sys.exit(1)


@main.command()
@click.argument("script", type=click.Path(exists=True))
@click.option("--to", default="colab", help="Target platform (colab)")
def publish(script: str, to: str) -> None:
    """Publish a pipeline script to a supported platform."""
    if to == "colab":
        try:
            from stepcast.integrations.colab import (
                publish_to_colab,
            )

            url = publish_to_colab(script)
            click.echo(f"Published: {url}")
        except ImportError:
            click.echo(
                "Colab dependencies not installed.\n"
                "Run: pip install 'stepcast[colab]'",
                err=True,
            )
            sys.exit(1)
    else:
        click.echo(f"Unknown target: {to}", err=True)
        sys.exit(1)
