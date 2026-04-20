
---
<!-- claude-code-homeassistant-hermit: Home Assistant Workflow -->

## Core Rules

- `/claude-code-homeassistant-hermit:ha-boot` is the single entry point — starts the hermit session and checks HA connectivity.
- Never commit real HA URLs, tokens, or device inventories.
- Never autonomously actuate: `lock`, `alarm_control_panel`, security-related `cover`/`button`/`switch`.
- Use the stored language from `MEMORY.md` for all user-facing output.
- Uncertain entities default to sensitive. Blocked work becomes a proposal.

## Entry Flow

1. `/claude-code-homeassistant-hermit:ha-boot` — starts hermit session + checks HA connectivity, context freshness, locale
2. Work using skills and subagents (see below)
3. `/claude-code-hermit:session-close` — archive session with structured report

## Skills

| Skill | Purpose |
|-------|---------|
| `/claude-code-homeassistant-hermit:ha-boot` | Start hermit session + check HA connectivity and context freshness |
| `/claude-code-homeassistant-hermit:ha-refresh-context` | Fetch and normalize full HA state |
| `/claude-code-homeassistant-hermit:ha-build-automation` | Draft automation YAML with validation |
| `/claude-code-homeassistant-hermit:ha-apply-change` | Validate and apply YAML with safety checks |
| `/claude-code-homeassistant-hermit:ha-analyze-patterns` | Identify patterns and automation opportunities |
| `/claude-code-homeassistant-hermit:ha-house-status` | Quick live house status via MCP |
| `/claude-code-homeassistant-hermit:ha-morning-brief` | Morning house brief — live status, overnight anomalies, recommendations |
| `/claude-code-homeassistant-hermit:ha-safety-audit` | Re-audit all live automations against the safety policy (plugin_check, weekly) |
| `/claude-code-homeassistant-hermit:ha-integration-health` | Detect dropped integrations via per-domain unavailable ratios (plugin_check, daily) |
| `/claude-code-homeassistant-hermit:ha-automation-error-review` | Flag automations with recurring errors in HA's log (plugin_check, daily) |

## Subagents

| Agent | Purpose |
|-------|---------|
| `@ha-safety-reviewer` | Review YAML for safety policy compliance (read-only) |
| `@ha-automation-builder` | Build automation YAML in isolated worktree |
| `@ha-pattern-analyst` | Analyze history data for patterns (haiku, cheap) |

## MCP vs Python

- **MCP (`homeassistant`)**: live operations — `GetLiveContext`, `GetDateTime`, light/cover/fan control
- **Python CLI**: bulk data — context refresh, simulation, policy checks, apply
- **Safety hook**: MCP actuation tools are gated by `hooks/mcp-safety-gate.py` via `hooks/hooks.json`

MCP tool IDs follow the pattern `mcp__homeassistant__*`, assuming the Home Assistant MCP Server is registered in Claude Code as `homeassistant`. If you used a different registration name, update `hooks/hooks.json` accordingly.

## CLI Commands

```
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha refresh-context [--incremental]
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha simulate <artifact>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha validate-apply <artifact> [--reload automation|script]
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha policy-check <entity_id_or_yaml>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha audit-automations
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha automation-errors [--min-hits N]
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status [--probe]
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot store --language <locale> --local-url <url> [--remote-url <url>] [--token <token>]
.venv/bin/pytest tests/ -v
```

## Environment

Requires `.env` at project root (gitignored) with:

- `HOMEASSISTANT_LOCAL_URL` — e.g. `http://homeassistant.local:8123`
- `HOMEASSISTANT_TOKEN` — Long-Lived Access Token (never committed)
- `HOMEASSISTANT_REMOTE_URL` — optional external URL

## Safety

- Sensitive files: `.env` (HA token/URL), `hooks/mcp-safety-gate.py`, `src/ha_agent_lab/policy.py`
- MCP actuation tools are blocked by the safety hook before reaching HA
- Explicit operator approval required before applying automations or modifying safety policy

## Quick Reference

**HA skills**: `/claude-code-homeassistant-hermit:ha-boot` `/claude-code-homeassistant-hermit:ha-house-status` `/claude-code-homeassistant-hermit:ha-morning-brief` `/claude-code-homeassistant-hermit:ha-refresh-context` `/claude-code-homeassistant-hermit:ha-build-automation` `/claude-code-homeassistant-hermit:ha-apply-change` `/claude-code-homeassistant-hermit:ha-analyze-patterns`

**Routines** (hermit ≥ 1.0.12): `/claude-code-hermit:hermit-routines load` — activate scheduled routines (required once per interactive session). HA routines (`daily-ha-context`, `morning-brief`) are registered by `/claude-code-homeassistant-hermit:ha-hatch`. Enable `morning-brief` routine in `config.json` once setup is complete.

<!-- /claude-code-homeassistant-hermit: Home Assistant Workflow -->
