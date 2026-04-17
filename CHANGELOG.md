# Changelog

All notable changes to `claude-code-homeassistant-hermit` / `ha-agent-lab` are documented here.

## [0.0.1] — 2026-04-17

Initial public release.

- Skills: `ha-boot`, `ha-house-status`, `ha-morning-brief`, `ha-refresh-context`, `ha-build-automation`, `ha-apply-change`, `ha-analyze-patterns`, `ha-hatch`.
- Subagents: `ha-safety-reviewer`, `ha-automation-builder`, `ha-pattern-analyst`.
- MCP safety hook (`hooks/mcp-safety-gate.py`) blocking sensitive-domain actuation. Hook now matches all `mcp__homeassistant__Hass*` tools and fails closed when no resolvable entity IDs are found (area/device-only targets are blocked by default).
- Python CLI `ha-agent-lab` (REST client, policy engine, simulation, apply).
- Policy overrides via `.env`: `HA_SAFE_ENTITIES` (per-entity allow-list), `HA_EXTRA_SENSITIVE_DOMAINS`, `HA_EXTRA_SENSITIVE_KEYWORDS`. See `.env.example` for usage.
- Paired with `claude-code-hermit ≥ 1.0.0` for session discipline.
- Runtime deps: `pip install --user PyYAML python-dotenv` (checked and surfaced by `/claude-code-homeassistant-hermit:ha-hatch`).
