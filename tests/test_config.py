from pathlib import Path

from pytest import MonkeyPatch

from stepcast import config


def test_config_gemini_api_key(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STEPCAST_GEMINI_API_KEY", "test_key")
    assert config.get_gemini_api_key() == "test_key"


def test_config_server_url(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STEPCAST_SERVER_URL", "http://test")
    assert config.get_server_url() == "http://test"


def test_config_server_key(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STEPCAST_AUTH_KEY", "auth_test")
    assert config.get_server_key() == "auth_test"


def test_parse_simple_toml(tmp_path: Path) -> None:
    p = tmp_path / "config.toml"
    p.write_text("key = \"value\"\nother = 'test'\n")
    data = config._parse_simple_toml(p)
    assert data == {"key": "value", "other": "test"}


def test_get_config_not_exists(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "nope.toml")
    assert config.get_config() == {}
