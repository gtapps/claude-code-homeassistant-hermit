<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License" /></a>
  <a href="https://code.claude.com/docs/en/plugins"><img src="https://img.shields.io/badge/Claude%20Code-plugin-orange.svg" alt="Claude Code Plugin" /></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-0.0.1-green.svg" alt="Version 0.0.1" /></a>
  <img src="https://img.shields.io/badge/Claude-Pro%20%7C%20Max-blueviolet.svg" alt="Claude Pro/Max Compatible" />
  <img src="https://img.shields.io/badge/status-early%20alpha-red.svg" alt="Early Alpha" />
</p>

# claude-code-homeassistant-hermit

A [`claude-code-hermit`](https://github.com/gtapps/claude-code-hermit) plugin for autonomous Home Assistant management — skills, safety hooks, subagents, and a Python CLI for entity control.

> **Early alpha — this plugin controls real home devices. Review every action before confirming.**

Five commands to a running HA hermit:

```
# Install core first
claude plugin marketplace add gtapps/claude-code-hermit
claude plugin install claude-code-hermit --scope project

# Then install the dev plugin
claude plugin marketplace add gtapps/claude-code-homeassistant-hermit
claude plugin install claude-code-homeassistant-hermit --scope project

# Initialize
/claude-code-homeassistant-hermit:ha-hatch
```

---

## What It Does

- **MCP-first live operations** — talks to Home Assistant through its [MCP Server](https://www.home-assistant.io/integrations/mcp_server/) for real-time status, light/cover/fan control, and context queries.

- **Safety gate on all actuation** — every MCP call matching `mcp__homeassistant__Hass*` is pre-screened by `hooks/mcp-safety-gate.py`. Locks, alarm panels, and security devices are blocked by policy. Blocked operations become proposals for human review.

- **Python CLI for bulk work** — `ha-agent-lab` handles entity inventory refresh, YAML simulation, policy checks, and safe apply. Skills call it automatically.

- **Hermit-integrated sessions** — inherits session discipline, proposals, cost tracking, and memory from `claude-code-hermit`. Start with `/ha-boot`, close with `/session-close`.

- **Auto-configured permissions** — ships a `settings.json` that pre-approves safe CLI commands and MCP read tools while blocking destructive operations.

---

## Quick Start

> **Requirements:** [Claude Code](https://code.claude.com) v2.1.98+, Python ≥ 3.12, a running [Home Assistant](https://www.home-assistant.io/) instance, and the [claude-code-hermit](https://github.com/gtapps/claude-code-hermit) core plugin.

### 1. Install

```bash
cd /path/to/your/project
claude plugin marketplace add gtapps/claude-code-hermit
claude plugin marketplace add gtapps/claude-code-homeassistant-hermit
claude plugin install claude-code-hermit@claude-code-hermit --scope project
claude plugin install claude-code-homeassistant-hermit@claude-code-homeassistant-hermit --scope project
pip install --user PyYAML python-dotenv
```

> **Local development?** Use `claude --plugin-dir /path/to/claude-code-homeassistant-hermit` to test without installing.

### 2. Configure

Create your environment file in the project directory:

```bash
cp .env.example .env
```

Fill in the required values:

```
HOMEASSISTANT_LOCAL_URL=http://homeassistant.local:8123
HOMEASSISTANT_TOKEN=<your long-lived access token>
```

Never commit `.env` — it is gitignored.

In Home Assistant, enable the MCP Server integration: **Settings → Devices & Services → Add Integration → Model Context Protocol Server**. See the [official docs](https://www.home-assistant.io/integrations/mcp_server/) for details.

### 3. Initialize

```
/claude-code-hermit:hatch
/claude-code-homeassistant-hermit:ha-hatch
```

`ha-hatch` verifies your `.env`, installs Python deps (creating a `.venv` if needed), writes a project-scoped `.mcp.json` that registers the HA MCP server under the canonical name `homeassistant`, updates `CLAUDE.md`, and confirms connectivity.

After running ha-hatch: **restart Claude Code**, approve the `homeassistant` server on first use, then verify with `/mcp`.

> **Name matters**: skills and the safety hook expect MCP tool IDs in the form `mcp__homeassistant__*`. The generated `.mcp.json` uses this name automatically.

---

## Usage

Start every session with:

```
/claude-code-homeassistant-hermit:ha-boot
```

| Skill | Purpose |
|-------|---------|
| `ha-house-status` | Live house status snapshot |
| `ha-morning-brief` | Daily brief — presence, energy, alerts, proposals |
| `ha-refresh-context` | Fetch and normalize full HA entity inventory |
| `ha-build-automation` | Draft and validate an automation YAML |
| `ha-apply-change` | Apply validated YAML with safety checks |
| `ha-analyze-patterns` | Identify automation opportunities from history data |
| `ha-safety-audit` | Re-audit live automations against the safety policy (weekly plugin_check) |
| `ha-integration-health` | Detect dropped integrations via per-domain unavailable ratios (daily plugin_check) |
| `ha-automation-error-review` | Flag automations with recurring errors in HA's log (daily plugin_check) |

The last three are registered as `plugin_checks` by `ha-hatch` and fire on a cadence via hermit's reflect pipeline — findings surface as proposals automatically.

All skills are namespaced: `/claude-code-homeassistant-hermit:ha-*`.

## Safety

Every MCP actuation call is pre-checked by `hooks/mcp-safety-gate.py` against `src/ha_agent_lab/policy.py`. Calls targeting unresolvable entities (area-only or device-only targets) are blocked by default. Blocked operations become proposals for human review.

**Policy overrides** (add to `.env`, see `.env.example`):

| Variable | Effect |
|---|---|
| `HA_SAFE_ENTITIES=cover.garage_door,...` | Per-entity allow-list. Exact IDs only, no wildcards. |
| `HA_EXTRA_SENSITIVE_DOMAINS=vacuum,...` | Block additional domains entirely. |
| `HA_EXTRA_SENSITIVE_KEYWORDS=pool,...` | Block extra keywords in conditionally-sensitive domains. |

## CLI

Skills invoke `ha-agent-lab` automatically via `${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab`. You can also run it directly:

```bash
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha refresh-context
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha simulate <artifact>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha validate-apply <artifact> --reload automation
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha policy-check <target>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha audit-automations
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha automation-errors [--min-hits N]
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status --probe
```

## Architecture

```
claude-code-homeassistant-hermit (this plugin)
  ├── skills/            HA workflow skills (11)
  ├── agents/            HA subagents (3)
  ├── hooks/             Safety gate (mcp-safety-gate.py) + hooks.json
  ├── bin/               ha-agent-lab CLI
  ├── src/ha_agent_lab/  Python package (REST client, policy, simulation, apply)
  ├── settings.json      Auto-configured permissions
  ├── state-templates/   CLAUDE-APPEND.md (injected by ha-hatch)
  └── tests/             Hook and policy tests

claude-code-hermit (core, required ≥ 1.0.12)
  └── Session lifecycle, proposals, cost tracking, memory
```

## License

MIT — see [LICENSE](LICENSE).
