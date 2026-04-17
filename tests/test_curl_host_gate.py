"""Tests for hooks/curl-host-gate.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "curl-host-gate.py"

HA_LOCAL = "http://homeassistant.local:8123"


def _run(command: str, tool_name: str = "Bash", extra_env: dict | None = None) -> dict | None:
    env = os.environ.copy()
    env.pop("HOMEASSISTANT_LOCAL_URL", None)
    env.pop("HOMEASSISTANT_REMOTE_URL", None)
    env["HOMEASSISTANT_LOCAL_URL"] = HA_LOCAL
    if extra_env:
        env.update(extra_env)

    payload = json.dumps({"tool_name": tool_name, "tool_input": {"command": command}})
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    return json.loads(result.stdout) if result.stdout.strip() else None


def test_curl_ha_local_allows():
    out = _run(f"curl {HA_LOCAL}/api/states")
    assert out is not None
    assert out["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_curl_loopback_allows():
    out = _run("curl http://127.0.0.1:8123/api/")
    assert out is not None
    assert out["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_non_ha_curl_passthrough():
    out = _run("curl https://example.com/data")
    assert out is None


def test_non_bash_passthrough():
    out = _run("/tmp/x", tool_name="Read")
    assert out is None


def test_unrelated_bash_passthrough():
    out = _run("ls -la /tmp")
    assert out is None
