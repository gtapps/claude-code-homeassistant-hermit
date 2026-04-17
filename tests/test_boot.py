from pathlib import Path

import pytest

from ha_agent_lab.boot import boot_status, read_language, save_boot_preferences, write_language, _command_prefix
from ha_agent_lab.config import load_config
from ha_agent_lab.ha_api import HomeAssistantClient, HomeAssistantError


def _write_launcher(root: Path) -> None:
    launcher = root / "bin" / "ha-agent-lab"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text("#!/usr/bin/env bash\n", encoding="utf-8")


def test_language_roundtrip(tmp_path: Path) -> None:
    write_language(tmp_path, "pt-PT")
    assert read_language(tmp_path) == "pt-PT"


def test_boot_preferences_store_operator_context(tmp_path: Path) -> None:
    save_boot_preferences(
        tmp_path,
        language="en",
        local_url="http://ha.local:8123",
        remote_url="https://ha.example.com",
        token="secret-token",
    )
    config = load_config(tmp_path)
    assert config.ha_local_url == "http://ha.local:8123"
    assert config.ha_remote_url == "https://ha.example.com"
    assert config.ha_token == "secret-token"
    assert read_language(tmp_path) == "en"


def test_boot_status_detects_missing_context(tmp_path: Path) -> None:
    write_language(tmp_path, "en")
    config = load_config(tmp_path)
    status = boot_status(config, probe=False)
    assert status.language == "en"
    assert status.needs_context_refresh
    assert not status.context_exists


def test_boot_status_reports_missing_required_setup(tmp_path: Path) -> None:
    _write_launcher(tmp_path)
    status = boot_status(load_config(tmp_path), probe=False)
    fields = {item["field"] for item in status.setup_hints}
    assert "Language" in fields
    assert "HOMEASSISTANT_LOCAL_URL" in fields
    assert "HOMEASSISTANT_TOKEN" in fields
    assert status.command_prefix == "./bin/ha-agent-lab"
    assert not status.can_refresh_context


def test_command_prefix_prefers_repo_launcher(tmp_path: Path) -> None:
    _write_launcher(tmp_path)
    assert _command_prefix(tmp_path) == "./bin/ha-agent-lab"


def test_command_prefix_falls_back_to_repo_venv(tmp_path: Path) -> None:
    python_path = tmp_path / ".venv" / "bin" / "python"
    python_path.parent.mkdir(parents=True, exist_ok=True)
    python_path.write_text("", encoding="utf-8")
    assert _command_prefix(tmp_path) == ".venv/bin/python -m ha_agent_lab"


def test_boot_status_exposes_single_pass_setup_checklist(tmp_path: Path) -> None:
    _write_launcher(tmp_path)
    status = boot_status(load_config(tmp_path), probe=False)
    checklist = {item["field"]: item for item in status.setup_checklist}
    assert checklist["Language"]["status"] == "missing"
    assert checklist["Home Assistant endpoint"]["status"] == "missing"
    assert checklist["HOMEASSISTANT_TOKEN"]["status"] == "missing"
    assert checklist["Context snapshot"]["status"] == "missing"
    assert checklist["HOMEASSISTANT_REMOTE_URL"]["status"] == "optional"


def test_home_assistant_client_reports_exact_missing_configuration(tmp_path: Path) -> None:
    _write_launcher(tmp_path)
    with pytest.raises(HomeAssistantError) as excinfo:
        HomeAssistantClient(load_config(tmp_path))

    message = str(excinfo.value)
    assert "HOMEASSISTANT_LOCAL_URL or HOMEASSISTANT_REMOTE_URL" in message
    assert "HOMEASSISTANT_TOKEN" in message
    assert "./bin/ha-agent-lab boot status --probe" in message


def test_home_assistant_client_distinguishes_missing_token_from_missing_endpoint(tmp_path: Path) -> None:
    _write_launcher(tmp_path)
    save_boot_preferences(tmp_path, local_url="http://ha.local:8123")

    with pytest.raises(HomeAssistantError) as excinfo:
        HomeAssistantClient(load_config(tmp_path))

    message = str(excinfo.value)
    assert "HOMEASSISTANT_TOKEN" in message
    assert "HOMEASSISTANT_LOCAL_URL or HOMEASSISTANT_REMOTE_URL" not in message
