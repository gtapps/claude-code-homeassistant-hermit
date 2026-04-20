# Home Assistant Agent Lab

This repo is both the **`claude-code-homeassistant-hermit` plugin source** and a reference HA environment. Skills, agents, and the safety hook live in `skills/`, `agents/`, and `hooks/` (plugin root). When developing the plugin, work from the repo root; the operator environment runs via the installed plugin.

Autonomous HA agent powered by Claude Code + claude-code-hermit.

## Core Rules

- `/claude-code-homeassistant-hermit:ha-boot` is the single entry point — it starts hermit and checks HA connectivity.
- Never commit real HA URLs, tokens, or device inventories.
- Never autonomously actuate sensitive domains: `lock`, `alarm_control_panel`, security-related `cover`/`button`/`switch`.
- Use the stored language from `MEMORY.md` for all user-facing output.
- Prefer Python helpers over ad-hoc reasoning when a helper exists.
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

Hermit subagents (`session-mgr`) handle session tasks.

## MCP vs Python

- **Home Assistant MCP Server**: live operations — `GetLiveContext`, `GetDateTime`, light/cover/fan control
- **Python CLI**: bulk data — context refresh, simulation, policy checks, apply
- **Safety hooks**: MCP actuation tools are gated by `hooks/mcp-safety-gate.py`

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

Requires `.env` at project root (gitignored) with `HOMEASSISTANT_TOKEN` and `HOMEASSISTANT_LOCAL_URL`.

## Memory Conventions

- `MEMORY.md` (auto-loaded, max 200 lines): language, house profile, learned patterns, known issues
- `memory/*.md`: detailed topic files (entities, automation history)
- `.claude-code-hermit/raw/analysis/`: pattern analysis JSON artifacts
- Hermit session reports: `.claude-code-hermit/sessions/S-*-REPORT.md`

## Routines (hermit ≥ 1.0.12)

HA routines (`daily-ha-context`, `morning-brief`) are registered during `/claude-code-homeassistant-hermit:ha-hatch` into `config.routines[]`. To activate them in an interactive session run `/claude-code-hermit:hermit-routines load`. In always-on deployments they are loaded automatically at startup.

Enable the `morning-brief` routine in `config.json` (`"enabled": true`) once initial setup is complete.

## Repo Layout

```
src/ha_agent_lab/          Python package (REST client, policy, simulation, apply)
skills/ha-*/          HA workflow skills (plugin root)
agents/ha-*.md        HA domain subagents (plugin root)
.claude-code-hermit/       Hermit session state
.claude-code-hermit/state/ Runtime state (alert dedup, reflection, routine queue)
.claude-code-hermit/raw/   HA context snapshots, normalized data, audits, staged automation YAML
.claude-code-hermit/compiled/ Durable domain outputs injected at session start
memory/                    Durable topic memory files
hooks/                 Safety gate + hooks.json
```


