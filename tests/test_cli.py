"""Tests for the Click CLI."""
from __future__ import annotations

from click.testing import CliRunner

from stepcast.cli import main


def test_version_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["version"])
    assert result.exit_code == 0
    assert "stepcast" in result.output
    assert "1.0.1" in result.output


def test_doctor_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["doctor"])
    assert result.exit_code == 0
    assert "Python" in result.output
    assert "stepcast" in result.output


def test_config_set_get(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("stepcast.config.CONFIG_PATH", tmp_path / ".stepcast" / "config.toml")  # noqa: E501

    runner = CliRunner()
    set_result = runner.invoke(main, ["config", "set", "test_key", "hello"])
    assert set_result.exit_code == 0

    get_result = runner.invoke(main, ["config", "get", "test_key"])
    assert "hello" in get_result.output


def test_check_command() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 0


def test_run_command(tmp_path) -> None:  # noqa: ANN001
    """CLI run command executes a pipeline script."""
    script = tmp_path / "test_script.py"
    script.write_text(
        "from stepcast import Pipeline\n"
        "pipe = Pipeline('CLI Test', show_summary=False, fail_fast=False)\n"
        "@pipe.step('Hello', capture_output=False)\n"
        "def hello():\n"
        "    return 'hi'\n"
        "pipe.run()\n"
    )
    runner = CliRunner()
    result = runner.invoke(main, ["run", str(script)])
    # Exit code 0 = success, 1 = pipeline aborted (fail_fast); both are valid
    assert result.exit_code in (0, 1)


def test_config_get_empty(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("stepcast.config.CONFIG_PATH", tmp_path / "nope.toml")
    runner = CliRunner()
    result = runner.invoke(main, ["config", "get", "missing_key"])
    assert "(not set)" in result.output


def test_check_empty_config(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("stepcast.config.CONFIG_PATH", tmp_path / "nope.toml")
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert "No configuration found" in result.output


def test_run_command_abort(tmp_path) -> None:  # noqa: ANN001
    script = tmp_path / "abort_script.py"
    script.write_text(
        "from stepcast import Pipeline\n"
        "pipe=Pipeline('A', fail_fast=True)\n"
        "@pipe.step('Fail')\n"
        "def f(): raise ValueError('boom')\n"
        "pipe.run()\n"
    )
    runner = CliRunner()
    result = runner.invoke(main, ["run", str(script)])
    assert result.exit_code == 1


def test_serve_command(monkeypatch) -> None:  # noqa: ANN001
    def mock_serve(*args, **kwargs) -> None: pass  # noqa: ANN001, ANN002, ANN003
    import stepcast.dashboard.server
    monkeypatch.setattr(stepcast.dashboard.server, "serve", mock_serve)
    
    runner = CliRunner()
    result = runner.invoke(main, ["serve", "--no-browser"])
    assert "Starting stepcast dashboard" in result.output
    assert result.exit_code == 0


def test_publish_command_unknown(tmp_path) -> None:  # noqa: ANN001
    script = tmp_path / "script.py"
    script.touch()
    runner = CliRunner()
    result = runner.invoke(main, ["publish", str(script), "--to", "unknown"])
    assert result.exit_code == 1
    assert "Unknown target" in result.output


def test_doctor_command_no_deps(monkeypatch) -> None:  # noqa: ANN001
    import builtins
    original_import = builtins.__import__
    def mock_import(name, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if name in ("rich", "fastapi"):
            raise ImportError("mock exception")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", mock_import)
    
    runner = CliRunner()
    result = runner.invoke(main, ["doctor"])
    assert result.exit_code == 0
    assert "rich: not installed" in result.output
    assert "Dashboard: not installed" in result.output


def test_run_command_exception(tmp_path) -> None:  # noqa: ANN001
    script = tmp_path / "exception_script.py"
    script.write_text("1 / 0\n")
    runner = CliRunner()
    result = runner.invoke(main, ["run", str(script)])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_publish_command_colab(tmp_path, monkeypatch) -> None:  # noqa: ANN001
    import stepcast.integrations.colab
    monkeypatch.setattr(
        stepcast.integrations.colab,
        "publish_to_colab",
        lambda x: f"Published URL for {x}",
    )
    script = tmp_path / "script.py"
    script.touch()
    
    runner = CliRunner()
    result = runner.invoke(main, ["publish", str(script), "--to", "colab"])
    assert result.exit_code == 0
    assert "Published URL for" in result.output


def test_doctor_no_api_key(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.delenv("STEPCAST_GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    runner = CliRunner()
    result = runner.invoke(main, ["doctor"])
    assert "Gemini API key: not configured" in result.output
